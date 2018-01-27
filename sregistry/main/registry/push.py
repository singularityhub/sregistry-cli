'''

push.py: push functions for sregistry client

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

from sregistry.logger import bot, ProgressBar
from sregistry.utils import (
    parse_image_name,
    parse_header,
    remove_uri
)
from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

import requests
import json
import sys
import os


def push(self, path, name, tag=None):
    '''push an image to Singularity Registry'''

    path = os.path.abspath(path)
    image = os.path.basename(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.error('%s does not exist.' %path)
        sys.exit(1)

    # Interaction with a registry requires secrets
    self.require_secrets()

    # Extract the metadata
    names = parse_image_name(remove_uri(name), tag=tag)
    metadata = self.get_metadata(path, names=names)

    # Try to add the size
    try:
        image_size = os.path.getsize(path) >> 20
        if metadata['data']['attributes']['labels'] is None:
            metadata['data']['attributes']['labels'] = {'SREGISTRY_SIZE_MB': image_size }
        else:
            metadata['data']['attributes']['labels']['SREGISTRY_SIZE_MB'] = image_size

    except:
        bot.warning("Cannot load metadata to add calculated size.")
        pass


    if "deffile" in metadata['data']['attributes']:
        if metadata['data']['attributes']['deffile'] is not None:
            fromimage = parse_header(metadata['data']['attributes']['deffile'],
                                     header="from",
                                     remove_header=True) 
            metadata['data']['attributes']['labels']['SREGISTRY_FROM'] = fromimage
            bot.debug("%s was built from a definition file." % image)


    # Prepare push request with multipart encoder
    url = '%s/push/' % self.base
    upload_to = os.path.basename(names['storage'])

    SREGISTRY_EVENT = self.authorize(request_type="push",
                                     names=names)

    encoder = MultipartEncoder(fields={'collection': names['collection'],
                                       'name':names['image'],
                                       'metadata': json.dumps(metadata),
                                       'tag': names['tag'],
                                       'datafile': (upload_to, open(path, 'rb'), 'text/plain')})

    progress_callback = create_callback(encoder)
    monitor = MultipartEncoderMonitor(encoder, progress_callback)
    headers = {'Content-Type': monitor.content_type,
               'Authorization': SREGISTRY_EVENT }

    try:
        r = requests.post(url, data=monitor, headers=headers)
        message = self._read_response(r)

        print('\n[Return status {0} {1}]'.format(r.status_code, message))

    except KeyboardInterrupt:
        print('\nUpload cancelled.')



def create_callback(encoder):
    encoder_len = encoder.len / (1024*1024.0)
    bar = ProgressBar(expected_size=encoder_len,
                      filled_char='=')

    def callback(monitor):
        bar.show(monitor.bytes_read / (1024*1024.0))

    return callback
