'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
# from sregistry.utils import (
#    parse_image_name,
#    remove_uri
#)

# see the registry push for example of how to do this
# from requests_toolbelt import (
#    MultipartEncoder,
#    MultipartEncoderMonitor
# )

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
    # names = parse_image_name(remove_uri(name),tag=tag)

    # use Singularity client, if exists, to inspect to extract metadata
    # metadata = self.get_metadata(path, names=names)

    # If you want a spinner
    bot.spinner.start()
    # do your push request here. Generally you want to except a KeyboardInterrupt
    # and give the user a status from the response
    bot.spinner.stop()
    # print('\n[Return status {0} {1}]'.format(response.status_code, message))

    # (see registry push for examople of creating progress bar)
