'''

ls: search and query functions for client

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
from sregistry.utils import parse_image_name
from globus_sdk import TransferAPIError
from dateutil import parser

import json
import sys
import os



def search(self, query=None):
    '''search is the main entrypoint for a remote globus endpoint. There
       are two levels of search:

       Parameters
       ==========
       query: a globus endpoint id (or default None lists them)

       1. query is None: returns a list of endpoints
       2. query is not None: query is assumed to be an endpoint to list
    '''

    if not query:
        return self._list_endpoints()
    return self._list_endpoint_contents(query)


def list_endpoints(self):
    '''use a transfer client to list endpoints for the user. This function
       maps onto the search for an endpoint, given no query parameters.
       If the user provides query parameters, we should instead be using
       the list_endpoint_contents function called from search above.
    '''
    if not hasattr(self, '_transfer_client'):
        self._get_transfer_client()

    if not hasattr(self, '_endpoints'):
        self._endpoints = []

    # Trust that user might be calling to refresh
    if len(self._endpoints) == 0:
        self._update_endpoints()

    # Information we want to show the user
    for count,ep in enumerate(self._endpoints):
        ep_name = ep['display_name']
        ep_id = ep['id']
        ep_owner = ep['owner_string']
        # Print tabular
        bot.custom(prefix="%s %s" %(count, ep_name), color="CYAN")
        print("%s\n%s\n%s\n" %(ep_name, ep_id, ep_owner))
        
    return self._endpoints


def list_endpoint_contents(self, endpoint_id):
    '''get a particular endpoint container list for a user based on 
       an endpoint ID, meaning 
       the list of singularity images included. This also
       will initialize a singularity registry directory structure
    '''
    if not hasattr(self, '_transfer_client'):
        self._get_transfer_client()
    try:
        containers = self._transfer_client.operation_ls(self._endpoint_id)
    except TransferAPIError:
        bot.error('Endpoint connection failed.')


def sync_endpoints(self, remote_endpoint):
    '''not yet written - we would want some kind of transfer to be possible
       between endpoints
    '''
    if not hasattr(self, '_transfer_client'):
        self._get_transfer_client()

    tdata = globus_sdk.TransferData(self._transfer_client, self.endpoint_id,
                                    remote_endpoint,
                                    label="Singularity Registry Transfer",
                                    sync_level="checksum")

    #TODO: need to get images here... call an image source
    containers = []
    for container in containers:
        tdata.add_item(container, container)
    transfer_result = client.submit_transfer(tdata)
    return transfer_result


##################################################################
# Search Helpers
##################################################################

def update_endpoints()
    '''if endpoints not defined, get a list. If already defined, update it.
    '''
    # We can't be sure being called from list_endpoints
    if not hasattr(self, '_endpoints'):
        self._endpoints = []

    for scope in ['my-endpoints', 'shared-with-me']:
        for ep in self._transfer_client.endpoint_search(filter_scope=scope):
            self._endpoints.append(ep.__dict__['_data'])

    return self._endpoints
