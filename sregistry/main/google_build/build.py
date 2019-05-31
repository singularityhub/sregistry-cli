'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import (
    get_file_hash,
    get_tmpdir,
    parse_image_name,
    remove_uri
)

from sregistry.main.google_build.utils import get_build_template

from glob import glob
import time
import tarfile
import shutil
import json
import os


def build(self, name,
                recipe="Singularity",
                context=None, 
                preview=False):

    '''trigger a build on Google Cloud (builder then storage) given a name
       recipe, and Github URI where the recipe can be found.
    
       Parameters
       ==========
       recipe: the local recipe to build.
       name: should be the complete uri that the user has requested to push.
       context: the dependency files needed for the build. If not defined, only
                the recipe is uploaded.
       preview: if True, preview but don't run the build

       Environment
       ===========
       SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION: the version of Singularity
           to use, defaults to 3.0.2-slim
       SREGISTRY_GOOGLE_BUILD_CLEANUP: after build, delete intermediate 
           dependencies in cloudbuild bucket.

    '''
    bot.debug("BUILD %s" % recipe)

    # This returns a data structure with collection, container, based on uri
    names = parse_image_name(remove_uri(name))

    # Load the build configuration
    config = self._load_build_config(name=names['uri'], recipe=recipe)

    build_package = [recipe]
    if context not in [None, '', []]:

        # If the user gives a ., include recursive $PWD
        if '.' in context:
            context = glob(os.getcwd() + '/**/*', recursive=True)
        build_package = build_package + context
        
    package = create_build_package(build_package)

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

    # The source should point to the bucket with the .tar.gz, latest generation
    config["source"]["storageSource"]['bucket'] = self._build_bucket.name
    config["source"]["storageSource"]['object'] = destination

    # If not a preview, run the build and return the response
    if preview is False:
        config = self._run_build(config, self._bucket, names)

    # If the user wants to cache cloudbuild files, this will be set
    if not self._get_and_update_setting('SREGISTRY_GOOGLE_BUILD_CACHE'):
        blob.delete()

    # Clean up either way, return config or response
    shutil.rmtree(os.path.dirname(package))
    return config
    


def create_build_package(package_files):
    '''given a list of files, copy them to a temporary folder,
       compress into a .tar.gz, and rename based on the file hash.
       Return the full path to the .tar.gz in the temporary folder.

       Parameters
       ==========
       package_files: a list of files to include in the tar.gz

    '''
    # Ensure package files all exist
    for package_file in package_files:
        if not os.path.exists(package_file):
            bot.exit('Cannot find %s.' % package_file)

    bot.log('Generating build package for %s files...' % len(package_files))
    build_dir = get_tmpdir(prefix="sregistry-build")
    build_tar = '%s/build.tar.gz' % build_dir
    tar = tarfile.open(build_tar, "w:gz")

    # Create the tar.gz
    for package_file in package_files:
        tar.add(package_file)
    tar.close()

    # Get hash (sha256), and rename file
    sha256 = get_file_hash(build_tar)
    hash_tar =  "%s/%s.tar.gz" %(build_dir, sha256)
    shutil.move(build_tar, hash_tar)
    return hash_tar


def load_build_config(self, name, recipe):
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

    '''
    version_envar = 'SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION'
    version = self._get_and_update_setting(version_envar, '3.0.2-slim')
    config = get_build_template()

    # Name is in format 'dinosaur/container-latest'

    # The command to give the builder, with image name
    container_name = '%s.sif' % name.replace('/','-', 1)
    config['steps'][0]['name'] = 'singularityware/singularity:%s' % version
    config['steps'][0]['args'] = ['build', container_name, recipe]

    config["artifacts"]["objects"]["location"] = "gs://%s" % self._bucket_name
    config["artifacts"]["objects"]["paths"] = [container_name]

    return config
                

def run_build(self, config, bucket, names):
    '''run a build, meaning creating a build. Retry if there is failure
    '''

    project = self._get_project()

    #          prefix,    message, color
    bot.custom('PROJECT', project, "CYAN")
    bot.custom('BUILD  ', config['steps'][0]['name'], "CYAN")

    response = self._build_service.projects().builds().create(body=config, 
                                              projectId=project).execute()

    build_id = response['metadata']['build']['id']
    status = response['metadata']['build']['status']
    bot.log("build %s: %s" % (build_id, status))

    start = time.time()
    while status not in ['COMPLETE', 'FAILURE', 'SUCCESS']:
        time.sleep(15)
        response = self._build_service.projects().builds().get(id=build_id, 
                                                  projectId=project).execute()

        build_id = response['id']
        status = response['status']
        bot.log("build %s: %s" % (build_id, status))

    end = time.time()
    bot.log('Total build time: %s seconds' % (round(end - start, 2)))
   
    # If successful, update blob metadata and visibility
    if status == 'SUCCESS':

        # Does the user want to keep the container private?
        env = 'SREGISTRY_GOOGLE_STORAGE_PRIVATE'
        blob = bucket.blob(response['artifacts']['objects']['paths'][0])
        
        # Make Public, if desired
        if self._get_and_update_setting(env) is None:
            blob.make_public()
            response['public_url'] = blob.public_url

        # Add the metadata directly to the object
        update_blob_metadata(blob, response, config, bucket, names)
        response['media_link'] = blob.media_link
        response['size'] = blob.size
        response['file_hash'] = blob.md5_hash

    return response



def update_blob_metadata(blob, response, config, bucket, names):
    '''a specific function to take a blob, along with a SUCCESS response
       from Google build, the original config, and update the blob 
       metadata with the artifact file name, dependencies, and image hash.
    '''

    manifest = os.path.basename(response['results']['artifactManifest'])
    manifest = json.loads(bucket.blob(manifest).download_as_string())

    metadata = {'file_hash': manifest['file_hash'][0]['file_hash'][0]['value'],
                'artifactManifest': response['results']['artifactManifest'],
                'location': manifest['location'],
                'storageSourceBucket': config['source']['storageSource']['bucket'],
                'storageSourceObject': config['source']['storageSource']['object'],
                'buildCommand': ' '.join(config['steps'][0]['args']),
                'builder': config['steps'][0]['name'],
                'media_link': blob.media_link,
                'self_link': blob.self_link,
                'size': blob.size,
                'name': names['tag_uri'],
                'type': "container"} # identifier that the blob is a container

    blob.metadata = metadata   
    blob._properties['metadata'] = metadata
    blob.patch()
