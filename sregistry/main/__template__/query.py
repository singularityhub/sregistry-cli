"""

Copyright (C) 2017-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from sregistry.logger import bot

# from sregistry.utils import (parse_image_name, remove_uri)
import sys


def search(self, query=None, args=None):
    """query a Singularity registry for a list of images. 
     If query is None, collections are listed. 

    EXAMPLE QUERIES:    
    """

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
    """a "show all" search that doesn't require a query"""

    # This should be your apis url for a search
    url = "..."

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
            for c in result["containers"]:
                rows.append([c["uri"], c["detail"]])

    bot.table(rows)
    return rows


def container_query(self, query):
    """search for a specific container.
    This function would likely be similar to the above, but have different
    filter criteria from the user (based on the query)
    """
    # Write your functions here (likely a derivation of search_all) to do
    # a more specific search. The entrypoint to both these last functions
    # is via the main search function.
    rows = ["", "", ""]
    bot.table(rows)
    return rows
