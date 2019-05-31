'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
import json
import os

################################################################################

def update_token(self):
    '''update_token uses HTTP basic authentication to get a token for
    Docker registry API V2 operations. We get here if a 401 is
    returned for a request.

    Parameters
    ==========
    response: the http request response to parse for the challenge.
    
    https://docs.docker.com/registry/spec/auth/token/
    '''
    # Add Amazon headers

    tokens = self.aws.get_authorization_token()
    token = tokens['authorizationData'][0]['authorizationToken']    

    try:
        token = {"Authorization": "Basic %s" % token}
        self.headers.update(token)

    except:
        bot.exit("Error getting token.")


def download_layers(self, repo_name, digest=None, destination=None):
    ''' download layers is a wrapper to do the following for a client loaded
        with a manifest for an image:
      
        1. use the manifests to retrieve list of digests (get_digests)
        2. atomically download the list to destination (get_layers)

        This function uses the MultiProcess client to download layers
        at the same time.
    '''
    from sregistry.main.workers import Workers
    from sregistry.main.workers.aws import download_task

    # Obtain list of digets, and destination for download
    self._get_manifest(repo_name, digest)
    digests = self._get_digests(repo_name, digest)
    destination = self._get_download_cache(destination)

    # Create multiprocess download client
    workers = Workers()

    # Download each layer atomically
    tasks = []
    layers = []

    # Start with a fresh token
    self._update_token()

    for digest in digests:

        targz = "%s/%s.tar.gz" % (destination, digest['digest'])
        url = '%s/%s/blobs/%s' % (self.base, repo_name, digest['digest'])
         
        # Only download if not in cache already
        if not os.path.exists(targz):
            tasks.append((url, self.headers, targz))
        layers.append(targz)

    # Download layers with multiprocess workers
    if len(tasks) > 0:
        workers.run(func=download_task, tasks=tasks)

    return layers, url


def get_manifest(self, repo_name, tag):
    '''return the image manifest via the aws client, saved in self.manifest
    '''

    image = None
    repo = self.aws.describe_images(repositoryName=repo_name)
    if 'imageDetails' in repo:
        for contender in repo.get('imageDetails'):
            if tag in contender['imageTags']:
                image = contender
                break

    # if the image isn't found, we need to exit
    if image is None:
        bot.exit('Cannot find %s:%s, is the uri correct?' %(repo_name, tag))

    digest = image['imageDigest']
    digests = self.aws.batch_get_image(repositoryName=repo_name, 
                                       imageIds=[{"imageDigest": digest,
                                                  "imageTag": tag}])

    self.manifest = json.loads(digests['images'][0]['imageManifest'])
    return self.manifest 


def get_digests(self, repo_name, tag):
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
    if not hasattr(self, 'manifest'):
        bot.exit('Please retrieve manifest for the image first.')

    # version 2 manifest here!
    return self.manifest['layers']
