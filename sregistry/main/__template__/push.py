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
from sregistry.utils import (
    parse_image_name,
    remove_uri
)

# see the registry push for example of how to do this
from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

import requests
import sys
import os


def push(self, path, name, tag=None):
    '''push an image to Singularity Registry
    
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

    # use Singularity client, if exists, to inspect to extract metadata
    metadata = self.get_metadata(path, names=names)

    # If you want a spinner
    bot.spinner.start()
    # do your push request here. Generally you want to except a KeyboardInterrupt
    # and give the user a status from the response
    bot.spinner.stop()
    # print('\n[Return status {0} {1}]'.format(response.status_code, message))

    # (see registry push for examople of creating progress bar)
