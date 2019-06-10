'''

ls: search and query functions for client

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot


def search(self, query=None, args=None):
    '''query a bucket for images that match a particular pattern. If no
       query is provided, all images in the bucket are listed that have type
       "container" in the metadata and client "sregistry"
    '''
    if query is not None:
        return self._container_query(query)
    return self._search_all()


def list_containers(self):
    '''return a list of containers, determined by finding the metadata field
       "type" with value "container." We alert the user to no containers 
       if results is empty, and exit

       {'metadata': {'items': 
                              [
                               {'key': 'type', 'value': 'container'}, ... 
                              ]
                    }
       }

    '''
    results = []
    for image in self._bucket.list_blobs():
        if image.metadata is not None:
            if "type" in image.metadata:
                if image.metadata['type'] == "container":
                    results.append(image)

    if len(results) == 0:
        bot.info("No containers found, based on metadata type:container")

    return results


def search_all(self):
    '''a "list all" search that doesn't require a query. Here we return to
       the user all objects that have custom metadata value of "container"

       IMPORTANT: the upload function adds this metadata. For a container to
       be found by the client, it must have the type as container in metadata.
    '''
 
    results = self._list_containers()

    bot.info("[gs://%s] Containers" %self._bucket_name)

    rows = []
    for i in results:
        size = round(i.size / (1024*1024.0))
        size = ("%s MB" %size).rjust(10)
        rows.append([size, i.name])

    bot.table(rows)
    return rows


def container_query(self, query, quiet=False):
    '''search for a specific container.
       This function would likely be similar to the above, but have different
       filter criteria from the user (based on the query)
    '''
    results = self._list_containers()

    matches = []
    for result in results:
        for _, val in result.metadata.items():
            if query in val and result not in matches:
                matches.append(result)
            elif query in result.name and result not in matches:
                matches.append(result)

    if not quiet:
        bot.info("[gs://%s] Found %s containers" %(self._bucket_name, len(matches)))
        for image in matches:
            size = round(image.size / (1024*1024.0))
            bot.custom(prefix=image.name, color="CYAN")
            bot.custom(prefix='id:     ', message=image.id)
            bot.custom(prefix='name:    ', message=image.name)
            bot.custom(prefix='updated:', message=image.updated)
            bot.custom(prefix='size:  ',  message=' %s MB' %(size))
            bot.custom(prefix='md5:    ', message=image.md5_hash)
            if "public_url" in image.metadata:
                public_url = image.metadata['public_url']
                bot.custom(prefix='url:    ', message=public_url)
            bot.newline()
    return matches
