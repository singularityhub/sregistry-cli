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
from sregistry.utils import ( parse_image_name, remove_uri, extract_tar )
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

        image_file = self._pull(file_name=file_name, 
                                uri='nvidia://',
                                save=save, 
                                force=force, 
                                names=q,
                                kwargs=kwargs)

        finished.append(image_file)

    if len(finished) == 1:
        finished = finished[0]
    return finished
