'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
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
import pickle
import requests
import globus_sdk


def init_transfer_client(self):
    '''return a transfer client for the user''' 

    if self._tokens_need_update():
        self._update_tokens()

    access_token = self.transfer['access_token']
    #authorizer = globus_sdk.AccessTokenAuthorizer(access_token)
    #self.transfer_client = globus_sdk.TransferClient(authorizer=authorizer)

    authorizer = globus_sdk.RefreshTokenAuthorizer(
                                 self.transfer['refresh_token'],
                                 self._client, 
                                 access_token=self.transfer['access_token'], 
                                 expires_at=self.transfer['expires_at_seconds'])

    self.transfer_client = globus_sdk.TransferClient(authorizer=authorizer)



def get_endpoints(self, query=None):
    '''use a transfer client to get endpoints. If a search term is included,
       we use it to search a scope of "all" in addition to personal and shared
       endpoints. Endpoints are organized
       by type (my-endpoints, shared-with-me, optionally all) and then id.
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




def do_transfer(self, endpoint, container):

    if not hasattr(self, 'endpoints'):
        self.get_endpoints()

    if len(self.endpoints['my-endpoints']) > 0:

        # Use relative paths, we are in container and endpoint is mapped
        source = os.path.abspath(container)
        client = get_transfer_client(user)
        source_endpoint = settings.GLOBUS_ENDPOINT_ID
    tdata = globus_sdk.TransferData(client, source_endpoint,
                                    endpoint,
                                    label="Singularity Registry Transfer",
                                    sync_level="checksum")
    tdata.add_item(source, source)
    transfer_result = client.submit_transfer(tdata)
    return transfer_result


def globus_transfer(request, cid=None):
    ''' a main portal for working with globus. If the user has navigated
        here with a container id, it is presented with option to do a 
        transfer
    '''
    container = None
    if cid is not None:
        container = get_container(cid)
    endpoints = get_endpoints(request.user)
    context = {'user': request.user,
               'endpoints': endpoints,
               'container': container }

    return render(request, 'globus/transfer.html', context)


def submit_transfer(request, endpoint, cid):
    '''submit a transfer request for a container id to an endpoint, also
       based on id
    '''

    container = get_container(cid)
    if container is None:
        message = "This container could not be found."

    else:
        result = do_transfer(user=request.user,
                             endpoint=endpoint,
                             container=container)
        message = result['message']

    status = {'message': message }
    return JsonResponse(status)
