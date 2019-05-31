'''

search and query functions for client

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import ( parse_image_name, remove_uri )

import sys


def search(self, query=None, args=None):
    '''query a Singularity registry for a list of images. 
     If query is None, collections are listed. 

    EXAMPLE QUERIES:

    [empty]             list all collections in registry
    vsoch               do a general search for the expression "vsoch"
    vsoch/              list all containers in collection vsoch
    /dinosaur           list containers across collections called "dinosaur"
    vsoch/dinosaur      list details of container vsoch/dinosaur
                          tag "latest" is used by default, and then the most recent
    vsoch/dinosaur:tag  list details for specific container
    
    '''

    if query is not None:

        # List all containers in collection query/
        if query.endswith('/'):  # collection search
            return self._collection_search(query)

        # List containers across collections called /query
        elif query.startswith('/'):  
            return self._container_search(query, across_collections=True)

        # List details of a specific collection container
        elif "/" in query or ":" in query:
            return self._container_search(query)

        # Search collections across all fields
        return self._collection_search(query=query)


    # Search collections across all fields
    return self._search_all()



##################################################################
# Search Helpers
##################################################################

def search_all(self):
    '''a "show all" search that doesn't require a query'''

    url = '%s/collections/' %self.base

    results = self._paginate_get(url)
   
    if len(results) == 0:
        bot.info("No container collections found.")
        sys.exit(1)

    bot.info("Collections")

    rows = []
    for result in results:
        if "containers" in result:
            for c in result['containers']:
                rows.append([ c['uri'],
                              c['detail'] ])

    bot.table(rows)
    return rows


def collection_search(self, query):
    '''collection search will list all containers for a specific
    collection. We assume query is the name of a collection'''

    query = query.lower().strip('/')
    url = '%s/collection/%s' %(self.base, query)

    result = self._get(url)
    if len(result) == 0:
        bot.info("No collections found.")
        sys.exit(1)

    bot.custom(prefix="COLLECTION", message=query)

    rows = []
    for container in result['containers']:
        rows.append([ container['uri'],
                      container['detail'] ])

    bot.table(rows)
    return rows

def label_search(self, key=None, value=None):
    '''search across labels'''

    if key is not None:
        key = key.lower()

    if value is not None:
        value = value.lower()

    show_details = True
    if key is None and value is None:
        url = '%s/labels/search' % (self.base)
        show_details = False

    elif key is not None and value is not None:
        url = '%s/labels/search/%s/key/%s/value' % (self.base, key, value)

    elif key is None:
        url = '%s/labels/search/%s/value' % (self.base, value)

    else:
        url = '%s/labels/search/%s/key' % (self.base, key)

    result = self._get(url)
    if len(result) == 0:
        bot.info("No labels found.")
        sys.exit(0)

    bot.info("Labels\n")

    rows = []
    for l in result:        
        if show_details is True:
            entry = ["%s:%s" %(l['key'],l['value']),
                     "\n%s\n\n" %"\n".join(l['containers'])]
        else:
            entry = ["N=%s" %len(l['containers']),
                    "%s:%s" %(l['key'],l['value']) ]
        rows.append(entry)
    bot.table(rows)
    return rows


def container_search(self, query, across_collections=False):
    '''search for a specific container. If across collections is False,
    the query is parsed as a full container name and a specific container
    is returned. If across_collections is True, the container is searched
    for across collections. If across collections is True, details are
    not shown'''

    query = query.lower().strip('/')

    q = parse_image_name(remove_uri(query), defaults=False)

    if q['tag'] is not None:
        if across_collections is True:
            url = '%s/container/search/name/%s/tag/%s' % (self.base, q['image'], q['tag'])
        else:
            url = '%s/container/search/collection/%s/name/%s/tag/%s' % (self.base, q['collection'], q['image'], q['tag'])

    elif q['tag'] is None: 
        if across_collections is True:
            url = '%s/container/search/name/%s' % (self.base, q['image'])
        else:
            url = '%s/container/search/collection/%s/name/%s' % (self.base, q['collection'], q['image'])

    result = self._get(url)
    if "containers" in result:
        result = result['containers']

    if len(result) == 0:
        bot.info("No containers found.")
        sys.exit(1)

    bot.info("Containers %s" %query)

    rows = []
    for c in result:        

        rows.append([ '%s/%s' %(c['collection'], c['name']),
                      c['tag'] ])

    bot.table(rows)
    return rows
