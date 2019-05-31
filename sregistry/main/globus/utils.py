'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import read_file
import os
import globus_sdk
from globus_sdk.exc import TransferAPIError


def parse_endpoint_name(self, endpoint):
    '''split an endpoint name by colon, as the user can provide an
       endpoint name separated from a path:

       Parameters
       ==========
       endpoint 12345:/path/on/remote
    
    '''
    parts = [x for x in endpoint.split(':') if x]
    endpoint = parts[0]
    if len(parts) == 1:
        path = ''
    else:
        path = '/'.join(parts[1:])

    return endpoint, path



def create_endpoint_cache(self, 
                          endpoint_id, 
                          cache='.singularity/shub'):

    '''create a directory for sregistry in the user's 
       base folder to share images.

       Parameters
       ==========
       endpoint_id: the endpoint id parameters
       cache: the relative path for the images cache folder at the
              root of the endpoint

    '''
    self._create_endpoint_folder(endpoint_id, cache)


def create_endpoint_folder(self, endpoint_id, folder):
    '''create an endpoint folder, catching the error if it exists.

       Parameters
       ==========
       endpoint_id: the endpoint id parameters
       folder: the relative path of the folder to create

    '''
    try:
        res = self.transfer_client.operation_mkdir(endpoint_id, folder)
        bot.info("%s --> %s" %(res['message'], folder))
    except TransferAPIError:
        bot.info('%s already exists at endpoint' %folder)


def get_endpoint_path(self, endpoint_id):
    '''return the first fullpath to a folder in the endpoint based on
       expanding the user's home from the globus config file. This
       function is fragile but I don't see any other way to do it.
    
       Parameters
       ==========
       endpoint_id: the endpoint id to look up the path for

    '''
    config = os.path.expanduser("~/.globusonline/lta/config-paths")
    if not os.path.exists(config):
        bot.exit('%s not found for a local Globus endpoint.')

    path = None

    # Read in the config and get the root path

    config = [x.split(',')[0] for x in read_file(config)]
    for path in config:
        if os.path.exists(path):
            break

    # If we don't have an existing path, exit

    if path is None:
        bot.exit('No path was found for a local Globus endpoint.')

    return path



def init_transfer_client(self):
    '''return a transfer client for the user''' 

    if self._tokens_need_update():
        self._update_tokens()

    # Createe Refresh Token Authorizer

    authorizer = globus_sdk.RefreshTokenAuthorizer(
                                 self.transfer['refresh_token'],
                                 self._client, 
                                 access_token=self.transfer['access_token'], 
                                 expires_at=self.transfer['expires_at_seconds'])

    self.transfer_client = globus_sdk.TransferClient(authorizer=authorizer)


def get_endpoint(self, endpoint_id):
    '''use a transfer client to get a specific endpoint based on an endpoint id.
       
       Parameters
       ==========
       endpoint_id: the endpoint_id to retrieve

    ''' 
    endpoint = None
    
    if not hasattr(self, 'transfer_client'):
        self._init_transfer_client()

    try:
        endpoint = self.transfer_client.get_endpoint(endpoint_id).data
    except TransferAPIError:
        bot.info('%s does not exist.' %endpoint_id)
    
    return endpoint


def get_endpoints(self, query=None):
    '''use a transfer client to get endpoints. If a search term is included,
       we use it to search a scope of "all" in addition to personal and shared
       endpoints. Endpoints are organized
       by type (my-endpoints, shared-with-me, optionally all) and then id.

       Parameters
       ==========
       query: an endpoint search term to add to a scope "all" search. If not 
              defined, no searches are done with "all"

    ''' 
    self.endpoints = {}
    
    if not hasattr(self, 'transfer_client'):
        self._init_transfer_client()

    # We assume the user wants to always see owned and shared

    scopes = {'my-endpoints':None,
              'shared-with-me': None}

    # If the user provides query, add to search

    if query is not None:
        scopes.update({'all': query})

    for scope, q in scopes.items():  
        self.endpoints[scope] = {}      
        for ep in self.transfer_client.endpoint_search(q, filter_scope=scope):
            ep = ep.__dict__['_data']
            self.endpoints[scope][ep['id']] = ep

    # Alert the user not possible without personal lookup

    if len(self.endpoints['my-endpoints']) == 0:
        bot.warning('No personal endpoint found for local transfer.')
        bot.warning('https://www.globus.org/globus-connect-personal')

    return self.endpoints
