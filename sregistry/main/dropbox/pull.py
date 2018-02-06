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
from sregistry.utils import ( parse_image_name, remove_uri )
import os
import sys

def pull(self, images, file_name=None, save=True, **kwargs):
    '''pull an image from a dropbox. The image is found based on the storage 
       uri
 
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

    bot.debug('Execution of PULL for %s images' %len(images))

    # If used internally we want to return a list to the user.
    finished = []
    for image in images:

        names = parse_image_name(remove_uri(image))

        # Dropbox path is the path in storage with a slash
        dropbox_path = '/%s' % names['storage']
        
        # If the user didn't provide a file, make one based on the names
        if file_name is None:
            file_name = self._get_storage_name(names)

        # If the file already exists and force is False
        if os.path.exists(file_name) and force is False:
            bot.error('Image exists! Remove first, or use --force to overwrite')
            sys.exit(1) 

        # First ensure that exists
        if self.exists(dropbox_path) is True:

            # _stream is a function to stream using the response to start
            metadata, response = self.dbx.files_download(dropbox_path)
            image_file = self._stream(response, stream_to=file_name)

            # parse the metadata (and add inspected image)
            metadata = self._get_metadata(image_file, metadata)

            # If we save to storage, the uri is the dropbox_path
            if save is True:
                container = self.add(image_path = image_file,
                                     image_uri = dropbox_path.strip('/'),
                                     metadata = metadata,
                                     url = response.url)

                # When the container is created, this is the path to the image
                image_file = container.image

            if os.path.exists(image_file):
                bot.debug('Retrieved image file %s' %image_file)
                bot.custom(prefix="Success!", message=image_file)
                finished.append(image_file)

        else:
            bot.error('%s does not exist. Try sregistry search to see images.' %path)

    if len(finished) == 1:
        finished = finished[0]
    return finished

'''
            with open(storage_path, 'wb') as output:
                output.write(F.content)

#TODO: this is "batch/big? way to do it
metadata, res = dbx.files_download(path)
for data in res.iter_content(10):
 print(data)
'''
