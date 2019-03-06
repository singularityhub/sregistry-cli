'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import ( parse_image_name, remove_uri )

def remove(self, image, force=False):
    '''delete an image to Singularity Registry'''

    q = parse_image_name(remove_uri(image))

    # If the registry is provided in the uri, use it
    if q['registry'] == None:
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

    continue_delete = True
    if force is False:
        response = input("Are you sure you want to delete %s?" % q['uri'])
        while len(response) < 1 or response[0].lower().strip() not in "ynyesno":
            response = input("Please answer yes or no: ")
        if response[0].lower().strip() in "no":
            continue_delete = False

    if continue_delete is True:
        response = self._delete(url)
        message = self._read_response(response)
        bot.info("Response %s, %s" %(response.status_code, message))

    else:
        bot.info("Delete cancelled.")
