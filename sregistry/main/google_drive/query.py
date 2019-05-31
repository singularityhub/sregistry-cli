'''

search and query functions for client

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
import sys


def search(self, query=None, args=None):
    '''query a bucket for images that match a particular pattern. If no
       query is provided, all images in the bucket are listed that have type
       "container" in the metadata and client "sregistry"
    '''

    if query is not None:
        return self._container_query(query)
    return self._search_all()


def list_containers(self):
    '''return a list of containers. Since Google Drive definitely has other
       kinds of files, we look for containers in a special sregistry folder,
       (meaning the parent folder is sregistry) and with properties of type
       as container.
    '''
    # Get or create the base
    folder = self._get_or_create_folder(self._base)

    next_page = None
    containers = []

    # Parse the base for all containers, possibly over multiple pages

    while True:
        query = "mimeType='application/octet-stream'"  # ensures container
        query += " and properties has { key='type' and value='container' }"
        query += " and '%s' in parents" %folder['id']   # ensures in parent folder
        response = self._service.files().list(q=query,
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name, properties)',
                                              pageToken=next_page).execute()
        containers += response.get('files', [])
            
        # If there is a next page, keep going!
        next_page = response.get('nextPageToken')
        if not next_page:
            break

    if len(containers) == 0:
        bot.info("No containers found, based on properties type:container")
        sys.exit(0)

    return containers


def search_all(self):
    '''a "list all" search that doesn't require a query. Here we return to
       the user all objects that have custom properties value type set to
       container, which is set when the image is pushed. 

       IMPORTANT: the upload function adds this metadata. For a container to
       be found by the client, it must have the properties value with type
       as container. It also should have a "uri" in properties to show the 
       user, otherwise the user will have to query / download based on the id
    '''
 
    results = self._list_containers()
    matches = []

    bot.info("[drive://%s] Containers" %self._base)

    rows = []
    for i in results:

        # Fallback to the image name without the extension
        uri = i['name'].replace('.simg','')

        # However the properties should include the uri
        if 'properties' in i:
            if 'uri' in i['properties']:
                uri = i['properties']['uri']
        rows.append([i['id'],uri])

        # Give the user back a uri
        i['uri'] = uri
        matches.append(i)

    bot.custom(prefix="   [drive://%s]" %self._base, 
               message="\t\t[id]\t[uri]", 
               color="PURPLE")

    bot.table(rows)
    return matches



def container_query(self, query, quiet=False):
    '''search for a specific container.
    This function is the same as the search all, but instead of showing all
    results, filters them down based on user criteria (the query)
    '''

    results = self._list_containers()

    matches = []
    for result in results:
 
        is_match = False
        if query in result['id']:
            is_match = True

        elif query in result['name']:
            is_match = True

        else:
            for key,val in result['properties'].items():
                if query in val and is_match is False:
                    is_match = True
                    break

        if is_match is True:
            matches.append(result)


    if not quiet:
        bot.info("[drive://%s] Found %s containers" %(self._base,len(matches)))
        for image in matches:

            # If the image has properties, show to the user
            if 'properties' in image:
                image.update(image['properties'])

            bot.info(image['uri'])

            for key in sorted(image, key=len):
                val = image[key]
                if isinstance(val,str):
                    bot.custom(prefix=key.ljust(10), message=val, color="CYAN")
            bot.newline()
    return matches
