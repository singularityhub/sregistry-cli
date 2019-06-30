'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import (
    get_file_hash,
    get_thumbnail,
    parse_image_name,
    remove_uri
)

from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import base64
import os



def push(self, path, name, tag=None):
    '''push an image to Google Cloud Drive, meaning uploading it
    
    path: should correspond to an absolte image path (or derive it)
    name: should be the complete uri that the user has requested to push.
    tag: should correspond with an image tag. This is provided to mirror Docker
    '''
    # The root of the drive for containers (the parent folder)
    parent = self._get_or_create_folder(self._base)

    image = None
    path = os.path.abspath(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.exit('%s does not exist.' % path)

    names = parse_image_name(remove_uri(name),tag=tag)
    if names['version'] is None:
        version = get_file_hash(path, "sha256")
        names = parse_image_name(remove_uri(name), tag=tag, version=version)

    # Update metadata with names, flatten to only include labels
    metadata = self.get_metadata(path, names=names)
    metadata = metadata['data']
    metadata.update(names)
    metadata.update(metadata['attributes']['labels'])
    del metadata['attributes']

    file_metadata = {
        'name': names['storage'],
        'mimeType' : 'application/octet-stream',
        'parents': [parent['id']],
        'properties': metadata
    }

    media = MediaFileUpload(path,resumable=True)
    try:
        bot.spinner.start()
        image = self._service.files().create(body=file_metadata,
                                             media_body=media,
                                             fields='id').execute()

        # Add a thumbnail!
        thumbnail = get_thumbnail()

        with open(thumbnail, "rb") as f:
            body = { "contentHints": { 
                     "thumbnail": { "image": base64.urlsafe_b64encode(f.read()).decode('utf8'),
                                     "mimeType": "image/png" }
                                  }}
            image = self._service.files().update(fileId=image['id'],
                                                 body = body).execute()
 
        bot.spinner.stop()
        print(image['name'])

    except HttpError:
        bot.error('Error uploading %s' % path)

    return image
