'''

search and query functions for client

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
from sregistry.utils import ( parse_image_name, remove_uri )
import sys


def search(self, query=None, args=None):
    '''query a Singularity registry for a list of images. 
     If query is None, collections are listed. 

    EXAMPLE QUERIES:    
    '''

    # You can optionally better parse the image uri (query), but not
    # necessary
    # names = parse_image_name(remove_uri(query))

    if query is not None:

        # Here you might do a function that is a general list
        # Note that this means adding the function Client in __init__
        return self._container_query(query)


    # or default to listing (searching) all things.
    return self._search_all()


# These functions are added in __init__.py like so:
# from .query import search_all, container_query
# Client._search_all = search_all
# Client._container_query = container_query


def search_all(self):
    '''a "show all" search that doesn't require a query'''

    # This should be your apis url for a search
    url = '...'

    # paginte get is what it sounds like, and what you want for multiple
    # pages of results
    results = self._paginate_get(url)
   
    if len(results) == 0:
        bot.info("No container collections found.")
        sys.exit(1)

    bot.info("Collections")

    # Here is how to create a simple table. You of course must parse your
    # custom result and form the fields in the table to be what you think
    # are important!
    rows = []
    for result in results:
        if "containers" in result:
            for c in result['containers']:
                rows.append([ c['uri'],
                              c['detail'] ])

    bot.table(rows)
    return rows



def container_query(self, query):
    '''search for a specific container.
    This function would likely be similar to the above, but have different
    filter criteria from the user (based on the query)
    '''
    # Write your functions here (likely a derivation of search_all) to do
    # a more specific search. The entrypoint to both these last functions
    # is via the main search function.
    rows = ['','','']
    bot.table(rows)
    return rows
