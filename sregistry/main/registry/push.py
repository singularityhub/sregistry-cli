'''

push.py: push functions for sregistry client

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
from requests_toolbelt.streaming_iterator import StreamingIterator
from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

import requests
import hashlib
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
    image_size = os.path.getsize(path) >> 20

# COLLECTION ###################################################################

    # Prepare push request, this will return a collection ID if permission
    url = '%s/push/' % self.base
    auth_url = '%s/upload/chunked_upload' % self.base
    SREGISTRY_EVENT = self.authorize(request_type="push",
                                     names=names)

    # Data fields for collection
    fields = { 'collection': names['collection'],
               'name':names['image'],
               'tag': names['tag']}

    headers = { 'Authorization': SREGISTRY_EVENT }

    r = requests.post(auth_url, json=fields, headers=headers)

    # Always tell the user what's going on!
    message = self._read_response(r)
    print('\n[1. Collection return status {0} {1}]'.format(r.status_code, message))

    # Get the collection id, if created, and continue with upload
    if r.status_code != 200:
        sys.exit(1)


# UPLOAD #######################################################################

    url = '%s/upload' % self.base.replace('/api','')
    bot.debug('Seting upload URL to {0}'.format(url))

    cid = r.json()['cid']
    upload_to = os.path.basename(names['storage'])

    SREGISTRY_EVENT = self.authorize(request_type="upload",
                                     names=names)

    encoder = MultipartEncoder(fields={'SREGISTRY_EVENT': SREGISTRY_EVENT,
                                       'name': names['image'],
                                       'collection': str(cid),
                                       'tag': names['tag'],
                                       'file1': (upload_to, open(path, 'rb'), 'text/plain')})

    progress_callback = create_callback(encoder, self.quiet)
    monitor = MultipartEncoderMonitor(encoder, progress_callback)
    headers = {'Content-Type': monitor.content_type,
               'Authorization': SREGISTRY_EVENT }

    try:
        r = requests.post(url, data=monitor, headers=headers)
        r.raise_for_status()
        message = r.json()['message']
        print('\n[Return status {0} {1}]'.format(r.status_code, message))
    except requests.HTTPError as e:
        print('\nUpload failed: {0}.'.format(e))
    except KeyboardInterrupt:
        print('\nUpload cancelled.')
    except Exception as e:
        print(e)


def create_callback(encoder, quiet=False):
    encoder_len = encoder.len / (1024*1024.0)

    bar = ProgressBar(expected_size=encoder_len,
                      filled_char='=',
                      hide=quiet)

    def callback(monitor):
        bar.show(monitor.bytes_read / (1024*1024.0))
    return callback
