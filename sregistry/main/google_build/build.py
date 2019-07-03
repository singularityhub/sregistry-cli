'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import (
    get_file_hash,
    get_recipe_tag,
    get_tmpdir,
    parse_image_name,
    remove_uri
)

from sregistry.main.google_build.utils import get_build_template

try:
    from urllib.parse import unquote
except:
    from urllib2 import unquote

from glob import glob
import time
import tarfile
import shutil
import json
import os
import re

################################################################################
# Manual Build Logic
# 1. Intended for run on the command line, simply use the client to run sregistry
#    build, provide a recipe and a name, and it will update the terminal with
#    status until finished using the build function here. 
#     - If you provide a GitHub uri in the recipe, instead we run build_repo 
#       and get the recipe file from there.
#     - If headless is False, we assume running from the sregistry client and
#       wait for the build to finish, returning the URL to the user.
#     - If headless is True, we assume the function is being run outside of
#       the client, and build_status and build_finish can be used for updates.
#     - if a webhook is provided, headless must be True, and a response is
#       sent here with curl (under development)

def build(self, name,
                recipe="Singularity",
                context=None, 
                preview=False,
                headless=False,
                working_dir=None,
                webhook=None,
                timeout=10800,
                extra_data=None):
    '''trigger a build on Google Cloud (builder then storage) given a name
       recipe, and Github URI where the recipe can be found. This means
       creating and uploading a build package to use for the build.
    
       Parameters
       ==========
       recipe: the local recipe to build.
       name: should be the complete uri that the user has requested to push.
       context: the dependency files needed for the build. If not defined, only
                the recipe is uploaded.
       preview: if True, preview but don't run the build
       working_dir: The working directory for the build. Defaults to pwd.
       timeout: the number of seconds for the build to timeout. The default 
                is 3 hours, and the maximum is 24 hours. If unset (None)
                it will be 10 minutes.
       webhook: if not None, add a curl POST to finish the build. 
       headless: If true, don't track the build, but submit and provide
                 an endpoint to send a response to.
       extra_data: a dictionary of extra_data to send back to the webhook (they
                   are passed in the environment)

       Environment
       ===========
       SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION: the version of Singularity
           to use, defaults to v3.2.1-slim
       SREGISTRY_GOOGLE_BUILD_CLEANUP: after build, delete intermediate 
           dependencies in cloudbuild bucket.

    '''
    bot.debug("BUILD %s" % recipe)

    build_package = [recipe]

    if context:

        # If the user gives a ., include recursive $PWD
        if '.' in context:
            context = glob(os.getcwd() + '/**/*', recursive=True)
        build_package = build_package + context
        
    # We need to get and save relative paths for the config.
    package = create_build_package(build_package, working_dir)

    # Does the package already exist? If the user cached, it might
    destination='source/%s' % os.path.basename(package)
    blob = self._build_bucket.blob(destination)

    # if it doesn't exist, upload it
    if not blob.exists() and preview is False:
        bot.log('Uploading build package!')
        self._upload(source=package, 
                     bucket=self._build_bucket,
                     destination=destination)
    else:
        bot.log('Build package found in %s.' % self._build_bucket.name)

    # This returns a data structure with collection, container, based on uri
    names = parse_image_name(remove_uri(name))

    prefix = "%s/" % names['collection']

    # The name should include the complete uri so it's searchable
    name = os.path.basename(names['uri'])

    # Update the recipe name to use a relative path
    recipe = get_relative_path(recipe, working_dir)

    # Load the build configuration (defaults to local)
    config = self._load_build_config(name=name,
                                     prefix=prefix,
                                     recipe=recipe)
    # Add a webhook, if defined
    if webhook and headless:
        config = add_webhook(config=config, 
                             webhook=webhook, 
                             extra_data=extra_data)
 
    # The source should point to the bucket with the .tar.gz, latest generation
    config["source"]["storageSource"]['bucket'] = self._build_bucket.name
    config["source"]["storageSource"]['object'] = destination

    # If the user wants a timeout
    if timeout is not None:
        config['timeout'] = "%ss" % timeout

    # If not a preview, run the build and return the response
    if not preview:
        if not headless:
            config = self._run_build(config)
        else:
            config = self._submit_build(config)

        # If the user wants to cache cloudbuild files, this will be set
        env = 'SREGISTRY_GOOGLE_BUILD_CACHE'
        if not self._get_and_update_setting(env, self.envars.get(env)):
            if headless is False:
                blob.delete()

    # Clean up either way, return config or response
    shutil.rmtree(os.path.dirname(package))
    return config


################################################################################
# GitHub Build Logic
# 1. Intended for run from a server, we submit a job that uses a Github repo#
#    as a parameter, and if there is a response url provided, the finished
#    build will send a response to that server with curl (recommended).
#    If a private repository is provided, it must be prefixed with a token
    
def build_repo(self, 
               repo,
               recipe,
               commit=None,
               branch=None,
               headless=False,
               preview=False,
               webhook=None,
               timeout=10800,
               token=None,
               extra_data=None):
    '''trigger a build on Google Cloud (builder then storage) given a
       Github repo where a recipe can be found. We assume that github.com (or
       some other Git repo) is provided in the name (repo).
    
       Parameters
       ==========
       repo: the full repository address
       recipe: the local recipe to build.
       headless: if True, return the first response (and don't wait to finish)
       commit: if not None, check out a commit after clone.
       branch: if defined, checkout a branch.
       token: if an authentication token is provided, add to GitHub clone url.
       timeout: the number of seconds for the build to timeout. The default 
                is 3 hours, and the maximum is 24 hours. If unset (None)
                it will be 10 minutes.
       webhook: if not None, add a curl POST to finish the build. 
       extra_data: a dictionary of extra_data to send back to the webhook (they
                   are passed in the environment)
    '''
    bot.debug("BUILD %s" % recipe)

    # This returns a data structure with collection, container, based on uri
    names = parse_image_name(remove_uri(repo))

    # Strip git from the end
    if repo.endswith('git'):
        repo = repo.rstrip('.git')

    # In case they added a tag, strip
    if not repo.startswith('http') and not repo.startswith("git@"):
        repo = "https://%s" % repo

    bot.debug("REPO %s" % repo)

    # First preference to command line, then recipe tag
    tag = get_recipe_tag(recipe) or names.get('tag')

    # Update the tag, if recipe provides one
    names = parse_image_name(remove_uri(repo), tag=tag)

    # <collection>/<image>/<tag>/<commit|branch>/<container>.sif
    prefix = "%s/" % names['collection']

    # The name should include the complete uri so it's searchable
    name = os.path.basename(names['uri'])

    if commit or branch:
        name = "%s@%s" %(name, (commit or branch))

    # Load the build configuration
    config = self._load_build_config(template="singularity-cloudbuild-git.json",
                                     prefix=prefix,
                                     name=name,
                                     recipe=recipe)

    # If we need to checkout a particular commit
    if commit or branch:
        commit = commit or branch
        config['steps'].insert(0, {'args': ['checkout', commit],
                                   'name': 'gcr.io/cloud-builders/git'})

    # If the repo is private, add the token
    clone_url = repo
    if token is not None:
        clone_url = "https://%s@%s" %(token, remove_uri(repo))

    # Add the GitHub repo to the recipe, clone to $PWD (.)
    config['steps'].insert(0, {'args': ['clone', clone_url, "."],
                               'name': 'gcr.io/cloud-builders/git'})

    # If the user wants a timeout
    if timeout is not None:
        config['timeout'] = "%ss" % timeout

    # Add the webhook step, if applicable.
    if webhook and headless:
        config = add_webhook(config=config, 
                             webhook=webhook, 
                             extra_data=extra_data)

    # If not a preview, run the build and return the response
    if not preview:
        if not headless:
            return self._run_build(config)
        return self._submit_build(config)

    # If preview is True, we return the config
    return config

def create_build_package(package_files, working_dir=None):
    '''given a list of files, copy them to a temporary folder,
       compress into a .tar.gz, and rename based on the file hash.
       Return the full path to the .tar.gz in the temporary folder.

       Parameters
       ==========
       package_files: a list of files to include in the tar.gz
       working_dir: If set, the path derived for the recipe and
                    files is relative to this.

    '''
    # Ensure package files all exist
    for package_file in package_files:
        if not os.path.exists(package_file):
            bot.exit('Cannot find %s.' % package_file)

    bot.log('Generating build package for %s files...' % len(package_files))
    build_dir = get_tmpdir(prefix="sregistry-build")
    build_tar = '%s/build.tar.gz' % build_dir
    tar = tarfile.open(build_tar, "w:gz")

    # Create the tar.gz, making sure relative to working_dir
    for package_file in package_files:
 
        # Get a relative path
        relative_path = get_relative_path(package_file, working_dir)
        tar.add(package_file, arcname=relative_path)
    tar.close()

    # Get hash (sha256), and rename file
    sha256 = get_file_hash(build_tar)
    hash_tar =  "%s/%s.tar.gz" %(build_dir, sha256)
    shutil.move(build_tar, hash_tar)
    return hash_tar


def get_relative_path(filename, working_dir=None):
    '''given a filename and a working directory, return
       a relative path for the builder to use. This means
       removing the working directory from the filename

       Parameters
       ==========
       filename: the name of the file to get a path for
       working_dir: if not None, remove from paths.
    '''
    relative_path = filename

    # If a working directory is provided, it must end with / 
    if working_dir is not None:
        if not working_dir.endswith(os.sep):
            working_dir = "%s%s" %(working_dir, os.sep)

    if working_dir is not None:
        relative_path = filename.replace(working_dir, '') 
    return relative_path


def add_webhook(config, webhook, extra_data=None):
    '''add a webhook to a config. We assume that the sha256 is calculated in 
       the present working directory. Optionally, the user can provide
       extra_data to post back with the build_id.
    '''
    data = {'id':'$BUILD_ID'}
    substitutions = {}

    if extra_data is not None:

        # Keep a list of envars to add
        for key, val in extra_data.items(): 
            sub = "_SREGISTRY_%s" % key.upper()
            data[key] = "${%s}" % sub
            substitutions[sub] = val

    config['steps'].append({
        "name": "gcr.io/cloud-builders/curl",
        "args":  ["-d", json.dumps(data), "-X", "POST", webhook]})

    config['substitutions'] = substitutions
    return config


def load_build_config(self, name, recipe, 
                            template="singularity-cloudbuild-local.json", 
                            version="v3.2.1-slim",
                            prefix=""):
    '''load a google compute config, meaning that we start with a template,
       and mimic the following example cloudbuild.yaml:

        steps:
        - name: "singularityware/singularity:${_SINGULARITY_VERSION}"
          args: ['build', 'julia-centos-another.sif', 'julia.def']
        artifacts:
          objects:
            location: 'gs://sregistry-gcloud-build-vanessa'
            paths: ['julia-centos-another.sif']


        Parameters
        ==========
        recipe: the local recipe file for the builder.
        name: the name of the container, based on the uri
        template: the template to use, will be populated based on name
        prefix: a prefix for the storage path, defaults to empty string.
    '''
    version_envar = 'SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION'
    version = self._get_and_update_setting(version_envar, version)

    # Get the build template based on its name
    config = get_build_template(template)

    # Name is in format 'dinosaur/container:latest'
    storage_name = '%s%s.sif' %(prefix, name)
    container_name = os.path.basename(storage_name)

    # We need to create the equivalent directory for the image
    folder_name = os.path.dirname(storage_name)

    # The bucket location should have the uri
    bucket_location = "gs://%s/%s/" % (self._bucket_name, folder_name)

    # Last step: tag the blog with the sha256 sum
    bucket_sif = '%s%s' %(bucket_location, container_name)
    metadata_command = "gsutil setmeta -h x-goog-meta-sha256sum:$(cat SHA256SUM) %s" % bucket_sif
    config['steps'].insert(0, {'args': ["-c", metadata_command],
                               'entrypoint': "/bin/bash",
                               'name': 'gcr.io/cloud-builders/gsutil'})

    # Second to last step: manually upload the blob
    config['steps'].insert(0, {'args': ['cp', container_name, bucket_sif ],
                               'name': 'gcr.io/cloud-builders/gsutil'})

    # Calculate a hash (happens after build)
    sha256_command = 'sha256sum %s | cut -c 1-64 > SHA256SUM' % container_name
    config['steps'].insert(0, {'args': ['-c', sha256_command],
                               'entrypoint': '/bin/bash',
                               'name': 'ubuntu'})

    # Insert the build step (second step)
    config['steps'].insert(0, {'args': ['build', container_name, recipe],
                               'name': 'singularityware/singularity:%s' % version})

    return config
                

def run_build(self, config):
    '''run a build, meaning creating a build. Retry if there is failure
    '''

    response = self._submit_build(config)
    status = response['metadata']['build']['status']
    build_id = response['metadata']['build']['id']

    start = time.time()
    while status not in ['COMPLETE', 'FAILURE', 'SUCCESS', 'TIMEOUT']:
        time.sleep(15)
        response = self._build_status(build_id)
        status = response['status']
    
    end = time.time()
    bot.log('Total build time: %s seconds' % (round(end - start, 2)))   
    return self._finish_build(build_id, response=response, config=config)


def submit_build(self, config):
    '''run a build, meaning creating a build. Retry if there is failure
    '''

    project = self._get_project()

    #          prefix,    message, color
    bot.custom('PROJECT', project, "CYAN")
    for i, step in enumerate(config['steps']):
        bot.custom('BUILD %s' % i , step['name'], "CYAN")

    response = self._build_service.projects().builds().create(body=config, 
                                              projectId=project).execute()

    build_id = response['metadata']['build']['id']
    status = response['metadata']['build']['status']
    bot.log("build %s: %s" % (build_id, status))

    return response


def build_status(self, build_id):
    '''get a build status based on a build id. We return the entire response
       object for the client to parse.
    '''
    project = self._get_project()
    response = self._build_service.projects().builds().get(id=build_id, 
                                              projectId=project).execute()


    build_id = response['id']
    status = response['status']
    bot.log("build %s: %s" % (build_id, status))

    return response
   

def finish_build(self, build_id, 
                       config=None, 
                       response=None):

    '''finish a build, meaning if the build was successful, we check the
       user preference to make it private. If it's set, we leave it 
       private. Otherwise, we make it public (default).

       Parameters
       ==========
       build_id: the build id returned from submission to track the build.
       config: optionally provide a config to get metadata from for the blob
       response: if we've already gotten a response status, include here
    '''
    # Get the build status, we will only complete on SUCCESS
    if not response:
        response = self._build_status(build_id)

    # If successful, update blob metadata and visibility
    if response['status'] == 'SUCCESS':

        # Does the user want to keep the container private?
        env = 'SREGISTRY_GOOGLE_STORAGE_PRIVATE'
        blob_location = get_blob_location(response, self._bucket_name)
        blob = self._bucket.get_blob(blob_location)
        
        # Make Public, if desired
        if not self._get_and_update_setting(env, self.envars.get(env)):
            blob.make_public()
            response['public_url'] = unquote(blob.public_url)

        # Add the metadata directly to the object, return updaated response
        response = update_blob_metadata(blob=blob, 
                                        response=response,
                                        config=config, 
                                        bucket=self._bucket)

    return response


def get_blob_location(response, bucket):
    '''return a relative path for a blob based on finding the build step,
       and the container built from it.

       Parameters
       ==========
       response: the response from client._build_status(build_id)
       bucket: the name of the build bucket.

    '''
    # Find the build step, it uses singularityware as a builder
    build_step = [x for x in response['steps'] 
                    if x['name'] == 'gcr.io/cloud-builders/gsutil' and
                    x['args'][0] == 'cp']

    # This is fragile, but we have to get the container name
    if len(build_step) > 0:
        location = build_step[0]['args'][-1]
        return re.sub('(gs://%s|%s)' %(bucket, bucket), '', location).strip('/')
    bot.exit("Cannot find build step with image name.")


def update_blob_metadata(blob, response, bucket, config=None):
    '''a specific function to take a blob, along with a SUCCESS response
       from Google build, the original config, and update the blob 
       metadata with the artifact file name, dependencies, and image hash.
    '''
    metadata = blob.metadata or {}

    metadata.update({'crc32c': blob.crc32c,
                     'media_link': blob.media_link,
                     'self_link': blob.self_link,
                     'md5sum': blob.md5_hash,
                     'size': blob.size,
                     'type': "container"}) # identify that the blob is container

    # If a configuration is provided
    if config:
        metadata['buildCommand'] = ' '.join(config['steps'][0]['args'])
        metadata['builder'] = config['steps'][0]['name']

        # If a source was used, add it.
        if "source" in config:
            metadata['storageSourceBucket'] = config['source']['storageSource']['bucket']
            metadata['storageSourceObject'] = config['source']['storageSource']['object']

    # Update the response, keeping data structure flat (and we don't overwrite)
    response.update(metadata)
    blob.metadata = metadata
    blob._properties['metadata'] = metadata
    blob.patch()
    return response
