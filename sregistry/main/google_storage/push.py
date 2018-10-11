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

from sregistry.logger import bot, ProgressBar
from sregistry.utils import (
    get_image_hash,
    parse_image_name,
    remove_uri
)

from sregistry.main.google_storage.utils import prepare_metadata
from googleapiclient.http import MediaFileUpload
from retrying import retry
import json
import sys
import os


def push(self, path, name, tag=None):
    '''push an image to Google Cloud Storage, meaning uploading it
    
    path: should correspond to an absolte image path (or derive it)
    name: should be the complete uri that the user has requested to push.
    tag: should correspond with an image tag. This is provided to mirror Docker
    '''
    path = os.path.abspath(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.error('%s does not exist.' %path)
        sys.exit(1)


    # This returns a data structure with collection, container, based on uri
    names = parse_image_name(remove_uri(name),tag=tag)

    if names['version'] is None:
        version = get_image_hash(path)
        names = parse_image_name(remove_uri(name), tag=tag, version=version)    

    # Update metadata with names
    metadata = self.get_metadata(path, names=names)
    metadata = metadata['data']
    metadata.update(names)

    manifest = self._upload(source=path, 
                            destination=names['storage'],
                            metadata=metadata)

    print(manifest['mediaLink'])



@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def upload(self, source, destination, chunk_size = 2 * 1024 * 1024, metadata=None):
    '''upload a file from a source to a destination. The client is expected
       to have a bucket (self._bucket) that is created when instantiated.
     
       This would be the method to do the same using the storage client,
       but not easily done for resumable

       blob = self._bucket.blob(destination)
       blob.upload_from_filename(filename=source, 
                                 content_type="application/zip",
                                 client=self._service)

       url = blob.public_url
       if isinstance(url, six.binary_type):
           url = url.decode('utf-8')

       return url
    '''
    env = 'SREGISTRY_GOOGLE_STORAGE_PRIVATE'
    keep_private = self._get_and_update_setting(env)

    media = MediaFileUpload(source, chunksize=chunk_size, resumable=True)
    request = self._storage_service.objects().insert(bucket=self._bucket_name, 
                                                     name=destination,
                                                     media_body=media)

    response = None
    total = request.resumable._size / (1024*1024.0)

    bar = ProgressBar(expected_size=total, filled_char='=', hide=self.quiet)

    while response is None:
        error = None
        try:
            progress, response = request.next_chunk()
            if progress:
                bar.show(progress.resumable_progress / (1024*1024.0))
        except:
            raise

    # When we finish upload, get as blob
    blob = self._bucket.blob(destination)
    if blob.exists():

        if not keep_private:
            blob.make_public()
    
        # If the user has a dictionary of metadata to update
        if metadata is not None:
            body = prepare_metadata(metadata)
            blob.metadata = metadata   
            blob._properties['metadata'] = metadata
            blob.patch()

    return response
