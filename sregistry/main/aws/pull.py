'''

Copyright (C) 2017-2018 Vanessa Sochat.

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

from sregistry.logger import bot
from spython.main import Client as Singularity
from sregistry.utils import ( 
    get_tmpdir, 
    parse_image_name,
    remove_uri,
    extract_tar 
)
import shutil
import os
import re
import sys


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
        bot.error('Image exists! Remove first, or use --force to overwrite')
        sys.exit(1)

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
            bot.error(result['message'])
            sys.exit(1)        

    sudo = kwargs.get('sudo', False)

    # Build from a sandbox (recipe) into the image_file (squashfs)
    image_file = Singularity.build(image=file_name,
                                   recipe=sandbox,
                                   sudo=sudo)

    # Fall back to using Singularity
    if image_file is None:
        bot.info('Downloading with native Singularity, please wait...')
        image = image.replace('aws://', 'docker://')
        image_file = Singularity.pull(image, pull_folder=sandbox)

    # Save to local storage
    if save is True:

        # Did we get the manifests?
        manifests = {}
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
