'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import ( parse_image_name, remove_uri )
import botocore
import os
import sys


def pull(self, images, file_name=None, save=True, **kwargs):
    '''pull an image from a s3 storage
 
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

    finished = []
    for image in images:

        image = remove_uri(image)
        names = parse_image_name(image)

        if file_name is None:
            file_name = names['storage'].replace('/','-')

        # Assume the user provided the correct uri to start
        uri = names['storage']

        # First try to get the storage uri directly.
        try:
            self.bucket.download_file(uri, file_name)

        # If we can't find the file, help the user
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":

                # Case 1, image not found, but not error with API
                bot.error('Cannot find %s!' % file_name)

                # Try to help the user with suggestions
                results = self._search_all()
                if len(results) > 0:
                    bot.info('Did you mean:\n' % '\n'.join(results))      
                sys.exit(1)

            else:
                # Case 2: error with request, exit.
                bot.exit('Error downloading image %s' % image)
 
        # if we get down here, we have a uri
        found = None
        for obj in self.bucket.objects.filter(Prefix=image):
            if image in obj.key:
                found = obj

        # If we find the object, get metadata
        metadata = {}
        if found is not None:
            metadata = found.get()['Metadata']

            # Metadata bug will capitalize all fields, workaround is to lowercase
            # https://github.com/boto/boto3/issues/1709
            metadata = dict((k.lower(), v) for k, v in metadata.items())
  
        metadata.update(names)

        # If the user is saving to local storage
        if save is True and os.path.exists(file_name):
            container = self.add(image_path = file_name,
                                 image_uri = names['uri'],
                                 metadata = metadata)
            file_name = container.image

        # If the image was pulled to either
        if os.path.exists(file_name):
            bot.custom(prefix="Success!", message = file_name)
            finished.append(file_name)

    if len(finished) == 1:
        finished = finished[0]
    return finished
