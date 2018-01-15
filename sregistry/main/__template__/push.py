'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

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

# If you need to get metadata (or otherwise interact with an image) use
# the Singularity client (cli = Singularity() --> cli.inspect(..))
from sregistry.client import Singularity
from sregistry.logger import bot, ProgressBar
from sregistry.utils import (
    parse_image_name,
    parse_header,
    remove_uri
)

# see the registry push for example of how to do this
from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

import requests
import json
import sys
import os

# These functions might be important to decode/encode secrets.
# see the registry push for an example
from sregistry.auth import (
    generate_signature,
    generate_credential,
    generate_timestamp
)



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

    # here is an exampole of getting metadata for a container
    cli = Singularity()
    metadata = cli.inspect(image_path=path, quiet=True)

    # This returns a data structure with collection, container, based on uri
    names = parse_image_name(remove_uri(name),tag=tag)

    # If you want a spinner
    bot.spinner.start()
    # do your push request here. Generally you want to except a KeyboardInterrupt
    # and give the user a status from the response
    bot.spinner.stop()
    # print('\n[Return status {0} {1}]'.format(response.status_code, message))

    # (see registry push for examople of creating progress bar)
