'''

ls: search and query functions for client

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

from globus_sdk.exc import TransferAPIError
from sregistry.logger import bot
import sys
import os


def search(self, query=None, args=None):
    '''query will show images determined by the extension of img
       or simg.

       Parameters
       ==========
       query: the container name (path) or uri to search for
       args.endpoint: can be an endpoint id and optional path, e.g.:

             --endpoint  6881ae2e-db26-11e5-9772-22000b9da45e:.singularity'
             --endpoint  6881ae2e-db26-11e5-9772-22000b9da45e'

       if not defined, we show the user endpoints to choose from

       Usage
       =====
       If endpoint is defined with a query, then we search the given endpoint
       for a container of interested (designated by ending in .img or .simg

       If no endpoint is provided but instead just a query, we use the query
       to search endpoints.
    
    '''

    # No query is defined
    if query is None:

        # Option 1: No query or endpoints lists all shared and personal
        if args.endpoint is None:
            bot.info('Listing shared endpoints. Add query to expand search.')
            return self._list_endpoints()

        # Option 2: An endpoint without query will just list containers there
        else:
            return self._list_endpoint(args.endpoint)

    # Option 3: A query without an endpoint will search endpoints for it
    if args.endpoint is None:
        bot.info('You must specify an endpoint id to query!')
        return self._list_endpoints(query)

    # Option 4: A query with an endpoint will search the endpoint for pattern
    return self._list_endpoint(endpoint=args.endpoint, 
                               query=query)




def list_endpoints(self, query=None):
    '''list all endpoints, providing a list of endpoints to the user to
       better filter the search. This function takes no arguments,
       as the user has not provided an endpoint id or query.
    '''
    bot.info('Please select an endpoint id to query from')
 
    endpoints = self._get_endpoints(query)
    
    # Iterate through endpoints to provide user a list

    bot.custom(prefix="Globus", message="Endpoints", color="CYAN")
    rows = []
    for kind,eps in endpoints.items():
        for epid,epmeta in eps.items():
            rows.append([epid, '[%s]' %kind, epmeta['name']])

    bot.table(rows)
    return rows


def list_endpoint(self, endpoint, query=None):
    '''An endpoint is required here to list files within. Optionally, we can
       take a path relative to the endpoint root.

       Parameters
       ==========
       endpoint: a single endpoint ID or an endpoint id and relative path.
                 If no path is provided, we use '', which defaults to scratch.

       query: if defined, limit files to those that have query match

    '''
    if not hasattr(self, 'transfer_client'):
        self._init_transfer_client()

    # Separate endpoint id from the desired path

    endpoint, path = self._parse_endpoint_name(endpoint)

    # Get a list of files at endpoint, under specific path
    try:
        result = self.transfer_client.operation_ls(endpoint, path=path)
    except TransferAPIError as err:

        # Tell the user what went wrong!
        bot.custom(prefix='ERROR', message=err, color='RED')
        sys.exit(1)

    rows = []

    for filey in result:

        # Highlight container contenders with purple
        name = filey['name']
        if query is None or query in name:
            if name.endswith('img'):
                name = bot.addColor('PURPLE',name)
        
            rows.append([filey['type'],
                         filey['permissions'],
                         str(filey['size']),
                         name ])
   
    if len(rows) > 0:
        rows = [["type","[perm]","[size]","[name]"]] + rows
        bot.custom(prefix="Endpoint Listing %s" %path, message='', color="CYAN")
        bot.table(rows)
    else:
        bot.info('No content was found at the selected endpoint.')
    return rows
