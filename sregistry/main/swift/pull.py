'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import ( parse_image_name, remove_uri )
from swiftclient.exceptions import ClientException
import os
import sys


def pull(self, images, file_name=None, save=True, **kwargs):
    '''pull an image from storage using Swift. The image is found based on the
       storage uri
 
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
    force = False
    if "force" in kwargs:
        force = kwargs['force']

    if not isinstance(images, list):
        images = [images]

    bot.debug('Execution of PULL for %s images' % len(images))

    # If used internally we want to return a list to the user.
    finished = []
    for image in images:

        names = parse_image_name(remove_uri(image))

        # First try to get the collection
        collection = self._get_collection(names['collection'])
        if collection is None:
            bot.error('Collection %s does not exist.' % names['collection'])

            # Show the user collections he/she does have access to
            collections = self.get_collections()
            if collections:
                bot.info('Collections available to you: \n%s' %'\n'.join(collections))
            sys.exit(1)

        # Determine if the container exists in storage
        image_name = os.path.basename(names['storage'])
        
        try:
            obj_tuple = self.conn.get_object(names['collection'], image_name)
        except ClientException:
            bot.exit('%s does not exist.' % names['storage'])

        # Give etag as version if version not defined
        if names['version'] is None:
            names['version'] = obj_tuple[0]['etag']
        
        # If the user didn't provide a file, make one based on the names
        if file_name is None:
            file_name = self._get_storage_name(names)

        # If the file already exists and force is False
        if os.path.exists(file_name) and force is False:
            bot.exit('Image exists! Remove first, or use --force to overwrite') 

        # Write to file
        with open(file_name, 'wb') as filey:
            filey.write(obj_tuple[1])

        # If we save to storage, the uri is the dropbox_path
        if save is True:

            names.update(obj_tuple[0])
            container = self.add(image_path = file_name,
                                 image_uri = names['uri'],
                                 metadata = names)

            # When the container is created, this is the path to the image
            image_file = container.image

            if os.path.exists(image_file):
                bot.debug('Retrieved image file %s' %image_file)
                bot.custom(prefix="Success!", message=image_file)
                finished.append(image_file)

            else:
                bot.error('%s does not exist. Try sregistry search to see images.' % image_file)

    if len(finished) == 1:
        finished = finished[0]
    return finished
