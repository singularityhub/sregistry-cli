'''

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
from sregistry.main import ApiConnection
import globus_sdk
import pickle
import json
import time
import sys
import os

from .utils import (
    create_endpoint_cache,
    create_endpoint_folder,
    get_endpoint,
    get_endpoints,
    get_endpoint_path,
    init_transfer_client,
    parse_endpoint_name
)

from .push import push
from .pull import pull
from .query import (
    search,
    list_endpoint,
    list_endpoints
)

if sys.version_info[0] == 3:
    raw_input=input


class Client(ApiConnection):

    # Initialization Calls

    def __init__(self, secrets=None, base=None, **kwargs):

        # These are unlikely to change

        self._client_id = "ae32247c-2c17-4c43-92b5-ba7fe9957dbb"
        self._redirect_url = "https://auth.globus.org/v2/web/auth-code"
        self._init_clients()
         
        super(ApiConnection, self).__init__(**kwargs)


    def _init_clients(self):
        '''init_ cliends will obtain the tranfer and access tokens, and then
           use them to create a transfer client.
        '''

        self._client = globus_sdk.NativeAppAuthClient(self._client_id)
        self._load_secrets()


    def _load_secrets(self):
        '''load the secrets credentials file with the Globus OAuthTokenResponse
        '''

        # Second priority: load from cache
       
        self.auth = self._get_and_update_setting('GLOBUS_AUTH_RESPONSE')
        self.transfer = self._get_and_update_setting('GLOBUS_TRANSFER_RESPONSE')
        

    # Runtime Calls

    def _tokens_need_update(self):
        '''return boolean True or False if the client tokens (self._auth and
           self._transfer) need updating.
        '''

        # Assumes that auth and transfer have same refresh time

        needs_update = True
        if self.auth is not None:
            if self.auth['expires_at_seconds'] > time.time():
                needs_update = False
        return needs_update

        
    def _update_tokens(self):
        '''Present the client with authentication flow to get tokens from code.
           This simply updates the client _response to be used to get tokens
           for auth and transfer (both use access_token as index). We call
           this not on client initialization, but when the client is actually
           needed.
        '''

        self._client.oauth2_start_flow(refresh_tokens=True)
        authorize_url = self._client.oauth2_get_authorize_url()
        print('Please go to this URL and login: {0}'.format(authorize_url))

        auth_code = raw_input(
                    'Please enter the code you get after login here: ').strip()

        # Save to client

        self._response = self._client.oauth2_exchange_code_for_tokens(auth_code)
        self.auth = self._response.by_resource_server['auth.globus.org']
        self.transfer = self._response.by_resource_server['transfer.api.globus.org']
        self._update_setting('GLOBUS_TRANSFER_RESPONSE', self.transfer)
        self._update_setting('GLOBUS_AUTH_RESPONSE', self.auth)


# Transfer
Client._init_transfer_client = init_transfer_client

# Endpoints
Client._create_endpoint_cache = create_endpoint_cache
Client._create_endpoint_folder = create_endpoint_folder
Client._get_endpoint = get_endpoint
Client._get_endpoints = get_endpoints
Client._parse_endpoint_name = parse_endpoint_name
Client._get_endpoint_path = get_endpoint_path

# Push
Client.push = push
Client.pull = pull

# Search
Client.search = search
Client._list_endpoint = list_endpoint
Client._list_endpoints = list_endpoints
