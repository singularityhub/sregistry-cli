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
    remove_uri
)

from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

import requests
import os


def build(self, recipe, name, extra=None):
    '''push a recipe file to Singularity Registry server for a Google
       Cloud (or similar) build
    '''
    path = os.path.abspath(recipe)
    bot.debug("BUILD %s" % path)

    if extra is None:
        extra = {}

    if not os.path.exists(path):
        bot.exit('%s does not exist.' % path)

    if not os.path.isfile(path):
        bot.exit("Build takes a Singularity recipe file")

    # Interaction with a registry requires secrets
    self.require_secrets()

    valid = ['google_build']

    # Only one valid type
    if "google_build" not in extra:
        bot.exit('Please include --builder google_build as the last extra arugment for Google Cloud Build')

    builder_type = None
    for builder_type in extra:
        if builder_type in valid:
            break

    # Must have valid builder type
    if builder_type is None:
        bot.exit("Invalid builder type.")

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

    # Prepare build request
    url = '%s/%s/build/' %(names['registry'].replace('/api', ''), builder_type)
    SREGISTRY_EVENT = self.authorize(request_type="build", names=names)
    headers = { 'Authorization': SREGISTRY_EVENT }

    bot.debug('Setting build URL to {0}'.format(url))

    # Fields for build endpoint
    fields={'SREGISTRY_EVENT': SREGISTRY_EVENT,
            'name': names['image'],
            'collection': names['collection'],
            'tag': names['tag'],
            'datafile': (upload_to, open(path, 'rb'), 'text/plain')}

    encoder = MultipartEncoder(fields=fields)
    progress_callback = create_callback(encoder, self.quiet)
    monitor = MultipartEncoderMonitor(encoder, progress_callback)
    headers = {'Content-Type': monitor.content_type,
               'Authorization': SREGISTRY_EVENT }

    try:
        r = requests.post(url, data=monitor, headers=headers)
        r.raise_for_status()
        print('\n[Return status {0} Created]'.format(r.status_code))
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
