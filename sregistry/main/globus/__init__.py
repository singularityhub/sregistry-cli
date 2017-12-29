'''

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

from sregistry.logger import bot
from sregistry.auth import (
    read_client_secrets,
    update_client_secrets
)

from sregistry.auth.secrets import _get_secrets_file
from sregistry.main import ApiConnection
import globus_sdk
import json
import sys
import os

from .auth import authorize
from .pull import pull
from .push import push
from .delete import remove
from .query import ( search, update_endpoints, list_endpoints )

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self._client = None
        self.response = None
        self._client_id = "ae32247c-2c17-4c43-92b5-ba7fe9957dbb"
        self._get_endpoint_id()
        super(ApiConnection, self).__init__(**kwargs)

    def __str__(self):
        return type(self)


    def _get_endpoint_id(self):
        '''the user is instructed to export the SREGISTRY_GLOBUS_ENDPOINT_ID for
           the storage folder in the environment. The logic to derive this
           endpoint id works as follows:

           1. It is always required to use the Globus client
           2. The .sregistry settings file is used as a cache for the id
           3. the environment variable always takes priority to cache, and if
              found, will update the cache.
           4. If the variable is not found and the cache is set, we are good
           5. If the variable is not found and the cache isn't set, exit 1
        ''' 
        endpoint_id = os.environ.get('SREGISTRY_GLOBUS_ENDPOINT_ID')
        if endpoint_id is None:
            secrets = read_client_secrets()
            if "globus" in secrets:
                globus_secrets = secrets['globus']
                if 'SREGISTRY_GLOBUS_ENDPOINT_ID' in globus_secrets:
                    endpoint_id = globus_secrets['SREGISTRY_GLOBUS_ENDPOINT_ID']

        if endpoint_id is None:
            secrets_file = _get_secrets_file()
            msg = 'SREGISTRY_GLOBUS_ENDPOINT_ID not set or in %s' %secrets_file
            bot.error(msg)
            sys.exit(1)

        updates = {'SREGISTRY_GLOBUS_ENDPOINT_ID': endpoint_id}
        update_client_secrets(backend='globus', updates=updates)
        self._endpoint_id = endpoint_id


    def _get_base_client(self, reset=False):
        '''the base client has entrypoints for getting a transfer or 
           authentication client, starting with a token for the app
        '''
        if self._client is None or reset is True:
            self._client = globus_sdk.NativeAppAuthClient(self._client_id)
            self._client.oauth2_start_flow()
        return self._client      


    def _get_transfer_client(self):
        '''return a transfer client for the user
        ''' 
        if not hasattr(self, '_transfer'):
            self._init_clients()

        transfer_token = self._transfer['access_token']
        authorizer = globus_sdk.AccessTokenAuthorizer(transfer_token)
        self._transfer_client = globus_sdk.TransferClient(authorizer=authorizer)
        return self._transfer_client


    def _init_clients(self):
        '''redo the authentication flow with a code, and then tokens.
           Taken almost verbatim from:

           http://globus-sdk-python.readthedocs.io/en/stable/...
                  tutorial/#step-2-get-and-save-client-id
        '''

        # Step 1: open browser and authenticate
        self._client = self._get_base_client()

        self._client = globus_sdk.NativeAppAuthClient(self._client_id)
        self._client.oauth2_start_flow()

        url = self._client.oauth2_get_authorize_url()
        print('Please go to this URL and login: %s' %url)

        # Step 2: Get codes for client
        get_input = getattr(__builtins__, 'raw_input', input)
        message = 'Please enter the code you get after login here: '
        auth_code = get_input(message).strip()

        # Step 3: Exchange code for tokens
        self._response = self._client.oauth2_exchange_code_for_tokens(auth_code)
        self._auth = self._response.by_resource_server['auth.globus.org']
        self._transfer = self._response.by_resource_server['transfer.api.globus.org']

    # TODO:
    # 1. write function to connect to an endpoint. 
    # 2. initialize the endpoint with a base structure, if doesn't exist
    # 3. write functions to save, pull, list, etc, based on endpoint.
    # 4. write a logout / revoke tokens function to be called at session end

#Client.pull = pull
#Client.push = push

# Search and helpers
Client.search = search
Client._update_endpoints = update_endpoints
Client._list_endpoints = list_endpoints
Client._list_endpoint_contents = list_endpoint_contents
