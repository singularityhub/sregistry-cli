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

from sregistry.utils import mkdir_p
from sregistry.auth import ( read_client_secrets, update_client_secrets )
import re
import os


# Secrets and Settings


def get_settings(self, client_name=None):
    '''get all settings, either for a particular client if a name is provided,
       or across clients.

       Parameters
       ==========
       client_name: the client name to return settings for (optional)

    '''
    settings = read_client_secrets()
    if client_name is not None and client_name in settings:
        return settings[client_name]           
    return settings


def get_setting(self, name, default=None):
    '''return a setting from the environment (first priority) and then
       secrets (second priority) if one can be found. If not, return None.

       Parameters
       ==========
       name: they key (index) of the setting to look up
       default: (optional) if not found, return default instead.
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

    if setting is None and default is not None:
        setting = default
    return setting


def get_and_update_setting(self, name, default=None):
    '''Look for a setting in the environment (first priority) and then
       the settings file (second). If something is found, the settings
       file is updated. The order of operations works as follows:

       1. The .sregistry settings file is used as a cache for the variable
       2. the environment variable always takes priority to cache, and if
          found, will update the cache.
       3. If the variable is not found and the cache is set, we are good
       5. If the variable is not found and the cache isn't set, return
          default (default is None)

       So the user of the function can assume a return of None equates to
       not set anywhere, and take the appropriate action.
    ''' 

    setting = self._get_setting(name)

    if setting is None and default is not None:
        setting = default

    # If the setting is found, update the client secrets
    if setting is not None:
        updates = {name : setting}
        update_client_secrets(backend=self.client_name, 
                              updates=updates)

    return setting


def update_setting(self, name, value):
    '''Just update a setting, doesn't need to be returned.
    ''' 

    if value is not None:
        updates = {name : value}
        update_client_secrets(backend=self.client_name, 
                              updates=updates)


def get_storage_name(self, names, remove_dir=False):
    '''use a parsed names dictionary from get_image_name (above) to return
       the path in storage based on the user's preferences

       Parameters
       ==========
       names: the output from parse_image_name
    '''
    storage_folder = os.path.dirname(names['storage'])
    storage_folder = "%s/%s" %(self.storage, storage_folder)
    mkdir_p(storage_folder)
    file_name = names['storage'].replace('/','-')
    storage_path = "%s/%s" %(self.storage, file_name)
    if remove_dir is True:
        return file_name
    return storage_path
