'''

ls: search and query functions for client

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import remove_uri
import sys


def search(self, query=None, args=None):
    '''query a Singularity registry for a list of images. 
     If query is None, collections are listed. 

    '''

    if query is not None:

        # Here you might do a function that is a general list
        # Note that this means adding the function Client in __init__
        return self._container_query(query)

    # or default to listing (searching) all things.
    return self._search_all()



def search_all(self):
    '''a "show all" search that doesn't require a query'''

    results = []

    # Parse through folders (collections):
    for entry in self.dbx.files_list_folder('').entries:

        # Parse through containers
        for item in self.dbx.files_list_folder(entry.path_lower).entries:
            name = item.name.replace('.simg','')
            results.append([ "%s/%s" % (entry.name, name) ])
   

    if len(results) == 0:
        bot.info("No container collections found.")
        sys.exit(0)

    bot.info("Collections")
    bot.table(results)
    return results


def container_query(self, query):
    '''search for a specific container.
    This function would likely be similar to the above, but have different
    filter criteria from the user (based on the query)
    '''

    results = []

    query = remove_uri(query)

    # Parse through folders (collections):
    for entry in self.dbx.files_list_folder('').entries:

        # Parse through containers
        for item in self.dbx.files_list_folder(entry.path_lower).entries:
            name = item.name.replace('.simg','')
            name = "%s/%s" % (entry.name, name)
            if query in name:
                results.append([ name ])
   
    if len(results) == 0:
        bot.info("No container collections found.")
        sys.exit(0)

    bot.info("Collections")
    bot.table(results)
    return results
