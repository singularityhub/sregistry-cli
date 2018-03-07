'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from sregistry.defaults import SINGULARITY_CACHE
from sregistry.logger import bot
from sregistry.utils import ( mkdir_p, print_json, get_template, create_tar )
import json
import math
import os
import re
import requests
import shutil
import sys
import tempfile


###############################################################################

def update_token(self, response):
    '''update_token uses HTTP basic authentication to get a token for
    Docker registry API V2 operations. We get here if a 401 is
    returned for a request.

    Parameters
    ==========
    response: the http request response to parse for the challenge.
    
    https://docs.docker.com/registry/spec/auth/token/
    '''

    not_asking_auth = "Www-Authenticate" not in response.headers
    if response.status_code != 401 or not_asking_auth:
        bot.error("Authentication error, exiting.")
        sys.exit(1)

    challenge = response.headers["Www-Authenticate"]
    regexp = '^Bearer\s+realm="(.+)",service="(.+)",scope="(.+)",?'
    match = re.match(regexp, challenge)

    if not match:
        bot.error("Unrecognized authentication challenge, exiting.")
        sys.exit(1)

    realm = match.group(1)
    service = match.group(2)
    scope = match.group(3).split(',')[0]

    token_url = realm + '?service=' + service + '&expires_in=900&scope=' + scope

    # Default headers must be False so that client's current headers not used
    response = self._get(token_url)

    try:
        token = response["token"]
        token = {"Authorization": "Bearer %s" % token}
        self.headers.update(token)

    except Exception:
        bot.error("Error getting token.")
        sys.exit(1)



def get_manifests(self, repo_name, digest=None):
    '''get_manifests calls get_manifest for each of the schema versions,
       including v2 and v1. Version 1 includes image layers and metadata,
       and version 2 must be parsed for a specific manifest, and the 2nd
       call includes the layers. If a digest is not provided
       latest is used.

       Parameters
       ==========
       repo_name: reference to the <username>/<repository>:<tag> to obtain
       digest: a tag or shasum version

    '''

    if not hasattr(self, 'manifests'):
        self.manifests = {}

    # Obtain schema version 1 (metadata) and 2, and image config
    schemaVersions = ['v1', 'v2', 'config']
    for schemaVersion in schemaVersions:
        manifest = self._get_manifest(repo_name, digest, schemaVersion)
        if manifest is not None:

            # If we don't have a config yet, try to get from version 2 manifest
            if schemaVersion == "v2" and "config" in manifest:
                bot.debug('Attempting to get config as blob in verison 2 manifest')
                url = self._get_layerLink(repo_name, manifest['config']['digest'])        
                headers = {'Accept': manifest['config']['mediaType']}
                self.manifests['config'] = self._get(url, headers=headers)

            self.manifests[schemaVersion] = manifest


    return self.manifests


def get_manifest_selfLink(self, repo_name, digest=None):
    ''' get a selfLink for the manifest, for use by the client get_manifest
        function, along with the parents pull and record
 
       Parameters
       ==========
       repo_name: reference to the <username>/<repository>:<tag> to obtain
       digest: a tag or shasum version

    '''
    url = "%s/%s/manifests" % (self.base, repo_name)

    # Add a digest - a tag or hash (version)
    if digest is None:
        digest = 'latest'
    return "%s/%s" % (url, digest)


def get_manifest(self, repo_name, digest=None, version="v1"):
    '''
       get_manifest should return an image manifest
       for a particular repo and tag.  The image details
       are extracted when the client is generated.

       Parameters
       ==========
       repo_name: reference to the <username>/<repository>:<tag> to obtain
       digest: a tag or shasum version
       version: one of v1, v2, and config (for image config)

    '''

    accepts = {'config': "application/vnd.docker.container.image.v1+json",
               'v1': "application/vnd.docker.distribution.manifest.v1+json",
               'v2': "application/vnd.docker.distribution.manifest.v2+json" }

    url = self._get_manifest_selfLink(repo_name, digest)

    bot.verbose("Obtaining manifest: %s %s" % (url,version))
    headers = {'Accept': accepts[version] }

    try:
        manifest = self._get(url, headers=headers, quiet=True)
        manifest['selfLink'] = url
    except:
        manifest = None

    return manifest
 


def download_layers(self, repo_name, digest=None, destination=None):
    ''' download layers is a wrapper to do the following for a client loaded
        with a manifest for an image:
      
        1. use the manifests to retrieve list of digests (get_digests)
        2. atomically download the list to destination (get_layers)

        This function uses the MultiProcess client to download layers
        at the same time.
    '''
    from sregistry.main.workers import ( Workers, download_task )

    # 1. Get manifests if not retrieved
    if not hasattr(self, 'manifests'):
        self._get_manifests(repo_name, digest)

    # Obtain list of digets, and destination for download
    digests = self._get_digests()
    destination = self._get_download_cache(destination)

    # Create multiprocess download client
    workers = Workers()

    # Download each layer atomically
    tasks = []
    layers = []
    for digest in digests:

        targz = "%s/%s.tar.gz" % (destination, digest)

        # Only download if not in cache already
        if not os.path.exists(targz):
            url = "%s/%s/blobs/%s" % (self.base, repo_name, digest)
            tasks.append((url, self.headers, targz))
        layers.append(targz)

    # Download layers with multiprocess workers
    if len(tasks) > 0:
        download_layers = workers.run(func=download_task,
                                      tasks=tasks)
    # Create the metadata tar
    metadata = self._create_metadata_tar(destination)
    if metadata is not None:
        layers.append(metadata)


    return layers


def get_download_cache(self, destination, subfolder='docker'):
    '''determine the user preference for atomic download of layers. If
       the user has set a singularity cache directory, honor it. Otherwise,
       use the Singularity default.
    '''
    # First priority after user specification is Singularity Cache
    if destination is None:
        destination = self._get_setting('SINGULARITY_CACHEDIR', 
                                         SINGULARITY_CACHE)
     
        # If not set, the user has disabled (use tmp)
        if destination is None:
            destination = tempfile.mkdtemp()

    if not destination.endswith(subfolder):
        destination = "%s/%s" %(destination, subfolder)

    # Create subfolders, if don't exist
    mkdir_p(destination)
    return destination
        

def get_digests(self):
    '''
       return a list of layers from a manifest.
       The function is intended to work with both version
       1 and 2 of the schema. All layers (including redundant)
       are returned. By default, we try version 2 first,
       then fall back to version 1.

       For version 1 manifests: extraction is reversed

       Parameters
       ==========
       manifest: the manifest to read_layers from

    '''
    if not hasattr(self, 'manifests'):
        bot.error('Please retrieve manifests for an image first.')
        sys.exit(1)

    digests = []

    reverseLayers = False
    schemaVersions = list(self.manifests.keys())
    schemaVersions.reverse()

    # Select the manifest to use
    for schemaVersion in schemaVersions:

        manifest = self.manifests[schemaVersion]

        if manifest['schemaVersion'] == 1:
            reverseLayers = True

        # version 2 indices used by default
        layer_key = 'layers'
        digest_key = 'digest'

        # Docker manifest-v2-2.md#image-manifest
        if 'layers' in manifest:
            bot.debug('Image manifest version 2.2 found.')
            break

        # Docker manifest-v2-1.md#example-manifest  # noqa
        elif 'fsLayers' in manifest:
            layer_key = 'fsLayers'
            digest_key = 'blobSum'
            bot.debug('Image manifest version 2.1 found.')
            break

        else:
            msg = "Improperly formed manifest, "
            msg += "layers, manifests, or fsLayers must be present"
            bot.error(msg)
            sys.exit(1)

    for layer in manifest[layer_key]:
        if digest_key in layer:
            bot.debug("Adding digest %s" % layer[digest_key])
            digests.append(layer[digest_key])

    # Reverse layer order for manifest version 1.0
    if reverseLayers is True:
        message = 'v%s manifest, reversing layers' % schemaVersion
        bot.debug(message)
        digests.reverse()

    return digests


def get_layerLink(self, repo_name, digest):
    '''get the url for a layer based on a digest and repo name

       Parameters
       ==========
       digest: The image digest to obtain
       repo_name: the image name (library/ubuntu) to retrieve

    '''
    return "%s/%s/blobs/%s" % (self.base,
                               repo_name,
                               digest)


def get_layer(self, image_id, repo_name, download_folder=None):
    '''download an image layer (.tar.gz) to a specified download folder.

       Parameters
       ==========
       download_folder: download to this folder. If not set, uses temp.
       repo_name: the image name (library/ubuntu) to retrieve

    '''
    url = self._get_layerLink(repo_name, image_id)

    bot.verbose("Downloading layers from %s" % url)

    if download_folder is None:
        download_folder = tempfile.mkdtemp()

    download_folder = "%s/%s.tar.gz" % (download_folder, image_id)

    # Update user what we are doing
    bot.debug("Downloading layer %s" % image_id)

    # Step 1: Download the layer atomically
    file_name = "%s.%s" % (download_folder,
                           next(tempfile._get_candidate_names()))

    tar_download = self.download(url, file_name)

    try:
        shutil.move(tar_download, download_folder)
    except Exception:
        msg = "Cannot untar layer %s," % tar_download
        msg += " was there a problem with download?"
        bot.error(msg)
        sys.exit(1)
    return download_folder


def get_size(self, add_padding=True, round_up=True, return_mb=True):
    '''get_size will return the image size (must use v.2.0 manifest)
        
       Parameters
       ==========
       add_padding: if true, return reported size * 5
       round_up: if true, round up to nearest integer
       return_mb: if true, defaults bytes are converted to MB
    
    '''
    if not hasattr(self,'manifests'):
        bot.error('Please retrieve manifests for an image first.')
        sys.exit(1)

    size = 768  # default size
    for schemaVersion, manifest in self.manifests.items():
        if "layers" in manifest:
            size = 0
            for layer in manifest["layers"]:
                if "size" in layer:
                    size += layer['size']

            if add_padding is True:
                size = size * 5

            if return_mb is True:
                size = size / (1024 * 1024)  # 1MB = 1024*1024 bytes

            if round_up is True:
                size = math.ceil(size)
            size = int(size)

        return size


################################################################################
# Metadata (Environment, Labels, Runscript)
################################################################################


def get_config(self, key="Entrypoint", delim=None):
    '''get_config returns a particular key (default is Entrypoint)
        from a VERSION 1 manifest obtained with get_manifest.

        Parameters
        ==========
        key: the key to return from the manifest config
        delim: Given a list, the delim to use to join the entries.
        Default is newline

    '''
    if not hasattr(self,'manifests'):
        bot.error('Please retrieve manifests for an image first.')
        sys.exit(1)

    cmd = None

    # If we didn't find the config value in version 2
    for version in ['config', 'v1']:
        if cmd is None and 'config' in self.manifests:
            
            # First try, version 2.0 manifest config has upper level config
            manifest = self.manifests['config']
            if "config" in manifest:
                if key in manifest['config']:
                    cmd = manifest['config'][key]

            # Second try, config manifest (not from verison 2.0 schema blob)

            if cmd is None and "history" in manifest:
                for entry in manifest['history']:
                    if 'v1Compatibility' in entry:
                        entry = json.loads(entry['v1Compatibility'])
                        if "config" in entry:
                            if key in entry["config"]:
                                cmd = entry["config"][key]

    # Standard is to include commands like ['/bin/sh']
    if isinstance(cmd, list):
        if delim is not None:
            cmd = delim.join(cmd)
    bot.verbose("Found Docker config (%s) %s" % (key, cmd))
    return cmd


def get_environment_tar(self):
    '''return the environment.tar generated with the Singularity software.
       We first try the Linux Filesystem expected location in /usr/libexec
       If not found, we detect the system archicture

       dirname $(singularity selftest 2>&1 | grep 'lib' | awk '{print $4}' | sed -e 's@\(.*/singularity\).*@\1@')
    '''
    from sregistry.utils import ( which, run_command )

    # First attempt - look at File System Hierarchy Standard (FHS)
    res = which('singularity')['message']
    libexec = res.replace('/bin/singularity','')
    envtar = '%s/libexec/singularity/bootstrap-scripts/environment.tar' %libexec

    if os.path.exists(envtar):
        return envtar

    # Second attempt, debian distribution will identify folder
    try:
        res = which('dpkg-architecture')['message']
        if res is not None:
            cmd = ['dpkg-architecture', '-qDEB_HOST_MULTIARCH']
            triplet = run_command(cmd)['message'].strip('\n')
            envtar = '/usr/lib/%s/singularity/bootstrap-scripts/environment.tar' %triplet
            if os.path.exists(envtar):
                return envtar
    except:
        pass

    # Final, return environment.tar provided in package
    return "%s/environment.tar" %os.path.abspath(os.path.dirname(__file__))


def create_metadata_tar(self, destination=None, metadata_folder=".singularity.d"):
    '''create a metadata tar (runscript and environment) to add to the
       downloaded image. This function uses all functions in this section
       to obtain key--> values from the manifest config, and write
       to a .tar.gz

       Parameters
       ==========
       metadata_folder: the metadata folder in the singularity image.
                        default is .singularity.d
    '''  
    tar_file = None
   
    # We will add these files to it
    files = []

    # Extract and add environment
    environ = self._extract_env()
    if environ not in [None, ""]:
        bot.verbose3('Adding Docker environment to metadata tar')
        template = get_template('tarinfo')
        template['name'] = './%s/env/10-docker.sh' % (metadata_folder)
        template['content'] = environ
        files.append(template)

    # Extract and add labels
    labels = self._extract_labels()
    if labels is not None:
        labels = print_json(labels)
        bot.verbose3('Adding Docker labels to metadata tar')
        template = get_template('tarinfo')
        template['name'] = "./%s/labels.json" % metadata_folder
        template['content'] = labels
        files.append(template)

    # Runscript
    runscript = self._extract_runscript()
    if runscript is not None:
        bot.verbose3('Adding Docker runscript to metadata tar')
        template = get_template('tarinfo')
        template['name'] = "./%s/runscript" % metadata_folder
        template['content'] = runscript
        files.append(template)

    if len(files) > 0:
        dest = self._get_download_cache(destination, subfolder='metadata')
        tar_file = create_tar(files, dest)
    else:
        bot.warning("No metadata will be included.")
    return tar_file


def extract_env(self):
    '''extract the environment from the manifest, or return None.
       Used by functions env_extract_image, and env_extract_tar
    '''
    environ = self._get_config('Env')
    if environ is not None:
        if not isinstance(environ, list):
            environ = [environ]

        lines = []
        for line in environ:
            line = re.findall("(?P<var_name>.+?)=(?P<var_value>.+)", line)
            line = ['export %s="%s"' % (x[0], x[1]) for x in line]
            lines = lines + line

        environ = "\n".join(lines)
        bot.verbose3("Found Docker container environment!")
    return environ


def extract_runscript(self):
    '''extract the runscript (EntryPoint) as first priority, unless the
       user has specified to use the CMD. If Entrypoint is not defined,
       we default to None:
 
       1. IF SREGISTRY_DOCKERHUB_CMD is set, use Cmd
       2. If not set, or Cmd is None/blank, try Entrypoint
       3. If Entrypoint is not set, use default /bin/bash

    '''
    use_cmd = self._get_setting('SREGISTRY_DOCKER_CMD')

    # Does the user want to use the CMD instead of ENTRYPOINT?
    commands = ["Entrypoint", "Cmd"]
    if use_cmd is not None:
        commands.reverse()

    # Parse through commands until we hit one
    for command in commands:
        cmd = self._get_config(command)
        if cmd is not None:
            break

    # Only continue if command still isn't None
    if cmd is not None:
        bot.verbose3("Adding Docker %s as Singularity runscript..."
                     % command.upper())

        # If the command is a list, join. (eg ['/usr/bin/python','hello.py']
        bot.debug(cmd)
        if not isinstance(cmd, list):
            cmd = [cmd]

        cmd = " ".join(['"%s"' % x for x in cmd])

        cmd = 'exec %s "$@"' % cmd
        cmd = "#!/bin/sh\n\n%s\n" % cmd
        return cmd

    bot.debug("CMD and ENTRYPOINT not found, skipping runscript.")
    return cmd


def extract_labels(self):
    '''extract_labels will write a file of key value pairs including
       maintainer, and labels.
    
    Parameters
    ==========
    manifest: the manifest to use
    
    '''
    labels = self._get_config('Labels')
    if labels in [[],'',None]:
        labels = None

    return labels
