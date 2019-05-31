'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import ( parse_image_name, remove_uri, confirm_delete )

def delete(self, image, force=False):
    '''delete an image to Singularity Registry'''

    q = parse_image_name(remove_uri(image))

    # If the registry is provided in the uri, use it
    if q['registry'] is None:
        q['registry'] = self.base

    # If the base doesn't start with http or https, add it
    q = self._add_https(q)

    url = '%s/container/%s/%s:%s' % (q['registry'], 
                                     q["collection"],
                                     q["image"], 
                                     q["tag"])

    SREGISTRY_EVENT = self.authorize(request_type="delete", names=q)
    headers = {'Authorization': SREGISTRY_EVENT }
    self._update_headers(fields=headers)

    if confirm_delete(q['uri'], force) is True:
        response = self._delete(url)
        message = self._read_response(response)
        bot.info("Response %s, %s" %(response.status_code, message))
        # add some error handling here??
    else:
        bot.info("Delete cancelled.")

    return image
