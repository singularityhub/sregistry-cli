'''

search and query functions for client

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
import os
import re
import sys


def search(self, query=None, **kwargs):
    '''query a Singularity registry for a list of images. 
     If query is None, collections are listed. 

    EXAMPLE QUERIES:

    [empty]             list all collections in singularity hub
    vsoch               do a general search for collection "vsoch"
    vsoch/dinosaur      list details of container vsoch/dinosaur
                          tag "latest" is used by default, and then the most recent
    vsoch/dinosaur:tag  list details for specific container
    
    '''

    if query is not None:
        return self._search_collection(query)

    # Search collections across all fields
    return self.list()



##################################################################
# Search Helpers
##################################################################

def list_all(self, **kwargs):
    '''a "show all" search that doesn't require a query'''

    quiet=False
    if "quiet" in kwargs:
        quiet = kwargs['quiet']

    bot.spinner.start()
    url = '%s/collections/' %self.base
    results = self._paginate_get(url)
    bot.spinner.stop()   

    if len(results) == 0:
        bot.info("No container collections found.")
        sys.exit(1)

    rows = []
    for result in results:
        if "containers" in result:
            if result['id'] not in [37,38,39]:
                for c in result['containers']:
                    rows.append([c['detail'],"%s:%s" %(c['name'],c['tag'])])

    if quiet is False:
        bot.info("Collections")
        bot.table(rows)

    return rows


def search_collection(self, query):
    '''collection search will list all containers for a specific
    collection. We assume query is the name of a collection'''

    query = query.lower().strip('/')
    q = parse_image_name(remove_uri(query), defaults=False)
    
    # Workaround for now - the Singularity Hub search endpoind needs fixing
    containers = self.list(quiet=True)

    rows = []
    for result in containers:
        if re.search(query, result[1]):
            rows.append(result)

    if len(rows) > 0:
        bot.table(rows)
    else:
        bot.info('No containers found.')    

    return rows
