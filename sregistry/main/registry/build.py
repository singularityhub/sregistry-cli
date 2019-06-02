'''

build.py: push a Singularity recipe to Singularity Registry Server to build

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot, ProgressBar
from sregistry.utils import (
    parse_image_name,
    remove_uri,
    get_uri
)

from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

import requests
import sys
import os


def build(self, path, name):
    '''push a recipe file to Singularity Register server for a Google
       Cloud (or similar) build
    '''

    path = os.path.abspath(path)
    bot.debug("BUILD %s" % path)

    if not os.path.exists(path):
        bot.exit('%s does not exist.' % path)

    if not os.path.isfile(path):
        bot.exit("Build takes a Singularity recipe file")

    # Interaction with a registry requires secrets
    self.require_secrets()

    # The prefix (uri) defines the kind of builder
    builder_type = (get_uri(name, validate=False) or 
                    os.environ.get('SREGISTRY_BUILD_TYPE'))

    # Only one valid type
    if builder_type != "google_build":
        bot.exit('Please include google_build:// to specify Google Cloud Build')

    # Extract the metadata
    names = parse_image_name(remove_uri(name))

# COLLECTION ###################################################################

    # If the registry is provided in the uri, use it
    if names['registry'] is None:
        names['registry'] = self.base

    # If the base doesn't start with http or https, add it
    names = self._add_https(names)

    # Recipe filename to upload to
    upload_to = "Singularity.%s-%s-%s" % (names['collection'],
                                          names['image'],
                                          names['tag'])

    # Data fields for collection
    fields = { 'collection': names['collection'],
               'name': names['image'],
               'tag': names['tag']}

    # Prepare build request
    url = '%s/%s/build/' %(names['registry'].replace('/api', ''), builder_type)
    SREGISTRY_EVENT = self.authorize(request_type="build", names=names)
    headers = { 'Authorization': SREGISTRY_EVENT }

    bot.debug('Setting build URL to {0}'.format(url))

    encoder = MultipartEncoder(fields={'SREGISTRY_EVENT': SREGISTRY_EVENT,
                                       'name': names['image'],
                                       'collection': names['collection'],
                                       'tag': names['tag'],
                                       'datafile': (upload_to, open(path, 'rb'), 'text/plain')})

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
        print('\nRecipe upload failed: {0}.'.format(e))
    except KeyboardInterrupt:
        print('\nRecipe upload cancelled.')


def create_callback(encoder, quiet=False):
    encoder_len = encoder.len / (1024*1024.0)

    bar = ProgressBar(expected_size=encoder_len,
                      filled_char='=',
                      hide=quiet)

    def callback(monitor):
        bar.show(monitor.bytes_read / (1024*1024.0))
    return callback
