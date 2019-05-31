'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import (parse_image_name, remove_uri)


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
