'''

sregistry.api: base template for making a connection to an API

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot

# Headers

def get_headers(self):
    '''simply return the headers
    '''
    return self.headers

def reset_headers(self):
    '''reset headers to a reasonable default to specify content type of json
    '''
    self.headers = {'Content-Type':"application/json"}


def update_headers(self,fields=None):
    '''update headers with a token & other fields
    '''
    do_reset = True
    if hasattr(self, 'headers'):
        if self.headers is not None:
            do_reset = False

    if do_reset is True:
        self._reset_headers()

    if fields is not None:
        for key,value in fields.items():
            self.headers[key] = value

    header_names = ",".join(list(self.headers.keys()))
    bot.debug("Headers found: %s" %header_names)
