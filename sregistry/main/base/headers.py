'''

sregistry.api: base template for making a connection to an API

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
import json
import re
import os

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
