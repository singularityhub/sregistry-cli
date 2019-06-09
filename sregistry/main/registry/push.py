'''

push.py: push functions for sregistry client

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot, ProgressBar
from sregistry.utils import (
    parse_image_name,
    remove_uri
)
from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

import requests
import sys
import os


def push(self, path, name, tag=None):
    '''push an image to Singularity Registry'''

    path = os.path.abspath(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.exit('%s does not exist.' % path)

    # Interaction with a registry requires secrets
    self.require_secrets()

    # Extract the metadata
    names = parse_image_name(remove_uri(name), tag=tag)

# COLLECTION ###################################################################

    # If the registry is provided in the uri, use it
    if names['registry'] is None:
        names['registry'] = self.base

    # If the base doesn't start with http or https, add it
    names = self._add_https(names)

    # Prepare push request, this will return a collection ID if permission
    url = '%s/push/' % names['registry']
    auth_url = '%s/upload/chunked_upload' % names['registry']
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

    url = '%s/upload' % names['registry'].replace('/api','')
    bot.debug('Setting upload URL to {0}'.format(url))

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


def create_callback(encoder, quiet=False):
    encoder_len = encoder.len / (1024*1024.0)

    bar = ProgressBar(expected_size=encoder_len,
                      filled_char='=',
                      hide=quiet)

    def callback(monitor):
        bar.show(monitor.bytes_read / (1024*1024.0))
    return callback
