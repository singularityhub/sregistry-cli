'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from spython.main import Client as Singularity
from sregistry.logger import bot
from sregistry.utils import ( 
    get_tmpdir, 
    parse_image_name,
    remove_uri,
    extract_tar 
)
import shutil
import os


def pull(self, images, file_name=None, save=True, force=False, **kwargs):
    '''pull an image from a docker hub. This is a (less than ideal) workaround
       that actually does the following:

       - creates a sandbox folder
       - adds docker layers, metadata folder, and custom metadata to it
       - converts to a squashfs image with build

    the docker manifests are stored with registry metadata.
 
    Parameters
    ==========
    images: refers to the uri given by the user to pull in the format
    <collection>/<namespace>. You should have an API that is able to 
    retrieve a container based on parsing this uri.
    file_name: the user's requested name for the file. It can 
               optionally be None if the user wants a default.
    save: if True, you should save the container to the database
          using self.add()
    
    Returns
    =======
    finished: a single container path, or list of paths
    '''

    if not isinstance(images,list):
        images = [images]

    bot.debug('Execution of PULL for %s images' %len(images))

    # If used internally we want to return a list to the user.

    finished = []
    for image in images:

        q = parse_image_name( remove_uri(image), 
                              default_collection='aws' )

        image_file = self._pull(file_name=file_name, 
                                save=save, 
                                force=force, 
                                names=q,
                                kwargs=kwargs)

        finished.append(image_file)

    if len(finished) == 1:
        finished = finished[0]
    return finished


def _pull(self, 
          file_name, 
          names, 
          save=True, 
          force=False, 
          **kwargs):

    '''pull an image from aws. This is a (less than ideal) workaround
       that actually does the following:

       - creates a sandbox folder
       - adds docker layers from S3
       - converts to a squashfs image with build
 
    Parameters
    ==========
    images: refers to the uri given by the user to pull in the format
    <collection>/<namespace>. You should have an API that is able to 
    retrieve a container based on parsing this uri.
    file_name: the user's requested name for the file. It can 
               optionally be None if the user wants a default.
    save: if True, you should save the container to the database
          using self.add()
    
    Returns
    =======
    finished: a single container path, or list of paths
    '''

    # Use Singularity to build the image, based on user preference
    if file_name is None:
        file_name = self._get_storage_name(names)

    # Determine if the user already has the image
    if os.path.exists(file_name) and force is False:
        bot.exit('Image exists! Remove first, or use --force to overwrite')

    digest = names['version'] or names['tag']

    # Build from sandbox 
    sandbox = get_tmpdir(prefix="sregistry-sandbox")

    # First effort, get image via Sregistry
    layers, url = self._download_layers(names['url'], digest)

    # Add environment to the layers
    envtar = self._get_environment_tar()
    layers = [envtar] + layers

    # Create singularity image from an empty folder
    for layer in layers:
        bot.info('Exploding %s' %layer)
        result = extract_tar(layer, sandbox, handle_whiteout=True)
        if result['return_code'] != 0:
            bot.exit(result['message'])

    sudo = kwargs.get('sudo', False)

    # Build from a sandbox (recipe) into the image_file (squashfs)
    image_file = Singularity.build(image=file_name,
                                   recipe=sandbox,
                                   sudo=sudo)

    # Fall back to using Singularity
    if image_file is None:
        bot.info('Downloading with native Singularity, please wait...')
        image = file_name.replace('aws://', 'docker://')
        image_file = Singularity.pull(image, pull_folder=sandbox)

    # Save to local storage
    if save is True:

        # Did we get the manifests?
        if hasattr(self, 'manifest'):
            manifest = self.manifest

        container = self.add(image_path = image_file,
                             image_uri = names['uri'],
                             metadata = manifest,
                             url = url)

        # When the container is created, this is the path to the image
        image_file = container.image

    if os.path.exists(image_file):
        bot.debug('Retrieved image file %s' %image_file)
        bot.custom(prefix="Success!", message=image_file)

    # Clean up sandbox
    shutil.rmtree(sandbox)

    return image_file
