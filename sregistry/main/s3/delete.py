'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

Written by Tom Schoonjans (Tom.Schoonjans@diamond.ac.uk)

'''

from sregistry.logger import bot
from sregistry.utils import (parse_image_name, remove_uri, confirm_delete)

def delete(self, image, force=False):
    '''delete an image from an S3 bucket'''

    q = parse_image_name(remove_uri(image))

    uri = q['storage']

    try:
        _object = self.bucket.Object(uri)
        _object.load() # this throws an exception if the object does not exist! -> if delete() fails no exception is thrown...

        if confirm_delete(uri, force) is True:
            _object.delete()
        else:
            bot.info("Delete cancelled.")
    except Exception as e: # pylint: disable=broad-except
        bot.error('Could not delete object {}: {}'.format(uri, str(e)))
        return None

    return image
