'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import (
    parse_image_name,
    remove_uri
)

import os
import botocore


def push(self, path, name, tag=None):
    '''push an image to an S3 endpoint'''

    path = os.path.abspath(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.exit('%s does not exist.' %path)

    # Extract the metadata
    names = parse_image_name(remove_uri(name), tag=tag)
    image_size = os.path.getsize(path) >> 20

    # Create extra metadata, this is how we identify the image later
    # *important* bug in boto3 will return these capitalized
    # see https://github.com/boto/boto3/issues/1709
    metadata = {'sizemb': "%s" % image_size,
                'client': 'sregistry'}

    ExtraArgs = {"Metadata": metadata}

    acl = self._get_and_update_setting('SREGISTRY_S3_OBJECT_ACL')

    if acl is not None:
        ExtraArgs['ACL'] = acl

    try:
        self.bucket.upload_file(path, names['storage'], ExtraArgs)
    except botocore.exceptions.ClientError as e:
        bot.exit("Could not upload {} to bucket. Ensure you have sufficient permissions to put objects in the bucket (s3:PutObject), as well as modify the object ACL if SREGISTRY_S3_OBJECT_ACL is set (s3:PutObjectAcl): {}".format(path, str(e)))
