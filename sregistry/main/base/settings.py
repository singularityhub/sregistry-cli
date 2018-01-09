'''

sregistry.api: base template for making a connection to an API

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

from requests.exceptions import HTTPError

from sregistry.logger import bot
from sregistry.defaults import SREGISTRY_DATABASE
from sregistry.auth import ( read_client_secrets, update_client_secrets )
import threading
import shutil
import requests
import tempfile
import json
import sys
import re
import os


# Secrets and Settings

        

def get_setting(self, name):
    '''return a setting from the environment (first priority) and then
       secrets (second priority) if one can be found. If not, return None.
    ''' 

    # First priority is the environment
    setting = os.environ.get(name)

    # Second priority is the secrets file
    if setting is None:
        secrets = read_client_secrets()
        if self.client_name in secrets:
            secrets = secrets[self.client_name]
            if name in secrets:
                setting = secrets[name]

    return setting


def get_and_update_setting(self, name):
    '''Look for a setting in the environment (first priority) and then
       the settings file (second). If something is found, the settings
       file is updated. The order of operations works as follows:

       1. The .sregistry settings file is used as a cache for the variable
       2. the environment variable always takes priority to cache, and if
          found, will update the cache.
       3. If the variable is not found and the cache is set, we are good
       5. If the variable is not found and the cache isn't set, return None

       So the user of the function can assume a return of None equates to
       not set anywhere, and take the appropriate action.
    ''' 

    setting = self._get_setting(name)

    # If the setting is found, update the client secrets
    if setting is not None:
        updates = {name : setting}
        update_client_secrets(backend=self.client_name, 
                              updates=updates)
    return setting
