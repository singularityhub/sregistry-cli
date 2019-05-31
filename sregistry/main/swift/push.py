'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import (
    parse_image_name,
    remove_uri
)

import sys
import os


def push(self, path, name, tag=None):
    '''push an image to your Storage. If the collection doesn't exist,
       it is created.
   
       Parameters
       ==========
       path: should correspond to an absolute image path (or derive it)
       name: should be the complete uri that the user has requested to push.
       tag: should correspond with an image tag. This is provided to mirror Docker

    '''
    path = os.path.abspath(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.exit('%s does not exist.' % path)

    # Parse image names
    names = parse_image_name(remove_uri(name), tag=tag)

    # Get the size of the file
    file_size = os.path.getsize(path)

    # Create / get the collection
    self._get_or_create_collection(names['collection'])

    # The image name is the name followed by tag
    image_name = os.path.basename(names['storage'])
 
    # prepare the progress bar
    progress = 0
    bot.show_progress(progress, file_size, length=35)

    # Put the (actual) container into the collection
    with open(path, 'rb') as F:
        self.conn.put_object(names['collection'], image_name,
                             contents= F.read(),
                             content_type='application/octet-stream')

    # Finish up
    bot.show_progress(iteration=file_size,
                      total=file_size,
                      length=35,
                      carriage_return=True)

    # Newline to finish download
    sys.stdout.write('\n')
