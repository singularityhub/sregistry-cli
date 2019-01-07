'''

Copyright (C) 2018-2019 Vanessa Sochat.

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

import sys
import os


def push(self, path, name, tag=None):
    '''push an image to an S3 endpoint'''

    path = os.path.abspath(path)
    image = os.path.basename(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.error('%s does not exist.' %path)
        sys.exit(1)

    # Extract the metadata
    names = parse_image_name(remove_uri(name), tag=tag)
    image_size = os.path.getsize(path) >> 20

    # Create extra metadata, this is how we identify the image later
    # *important* bug in boto3 will return these capitalized
    # see https://github.com/boto/boto3/issues/1709
    metadata = {'sizemb': "%s" % image_size,
                'client': 'sregistry' }

    self.bucket.upload_file(path, names['storage_uri'], {"Metadata": metadata })
