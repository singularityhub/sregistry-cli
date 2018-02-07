'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
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
from sregistry.client import Singularity
from sregistry.utils import ( parse_image_name, remove_uri, extract_tar )
import tempfile
import shutil
import os
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
                              default_collection='nvidia' )

        # Use Singularity to build the image, based on user preference
        if file_name is None:
            file_name = self._get_storage_name(q)

        # Determine if the user already has the image
        if os.path.exists(file_name) and force is False:
            bot.error('Image exists! Remove first, or use --force to overwrite')
            sys.exit(1)

        digest = q['version'] or q['tag']

        # This is the Docker Hub namespace and repository
        layers = self._download_layers(q['url'], digest)

        # This is the url where the manifests were obtained
        url = self._get_manifest_selfLink(q['url'], digest)

        # Create client to build from sandbox
        cli = Singularity()

        # Build from sandbox 
        sandbox = tempfile.mkdtemp()

        # Add environment to the layers
        envtar = self._get_environment_tar()
        layers = [envtar] + layers

        # Create singularity image from an empty folder
        for layer in layers:
            bot.info('Exploding %s' %layer)
            result = extract_tar(layer, sandbox)
            if result['return_code'] != 0:
                bot.error(result['message'])
                sys.exit(1)        

        if os.geteuid() == 0:
             image_file = cli.build(file_name, sandbox)
        else:
            image_file = cli.build(file_name, sandbox, sudo=False)

        # Save to local storage
        if save is True:

            container = self.add(image_path = image_file,
                                 image_uri = q['uri'],
                                 metadata = self.manifests,
                                 url = url)

            # When the container is created, this is the path to the image
            image_file = container.image

        # If the image_file is different from sandbox, remove sandbox
        if image_file != sandbox:
            shutil.rmtree(sandbox)

        if os.path.exists(image_file):
            bot.debug('Retrieved image file %s' %image_file)
            bot.custom(prefix="Success!", message=image_file)
            finished.append(image_file)

    if len(finished) == 1:
        finished = finished[0]
    return finished
