'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
import sys
import botocore


def search(self, query=None, args=None):
    '''query a s3 endpoint for an image based on a string

    EXAMPLE QUERIES:

    [empty]             list all container collections
    vsoch/dinosaur      look for containers with name vsoch/dinosaur
    
    '''

    if query is not None:
        return self._container_search(query)

    # Search collections across all fields
    return self._search_all()



################################################################################
# Search Helpers
################################################################################

def search_all(self, quiet=False):
    '''a "show all" search that doesn't require a query
       
       Parameters
       ==========
       quiet: if quiet is True, we only are using the function to return
              rows of results.
    '''

    results = []

    for obj in self.bucket.objects.all():
        subsrc = obj.Object()

        # Metadata bug will capitalize all fields, workaround is to lowercase
        # https://github.com/boto/boto3/issues/1709
        try:
            metadata = dict((k.lower(), v) for k, v in subsrc.metadata.items())
        except botocore.exceptions.ClientError as e:
            bot.warning("Could not get metadata for {}: {}".format(subsrc.key, str(e)))
            continue

        size = ''

        # MM-DD-YYYY
        datestr = "%s-%s-%s" %(obj.last_modified.month,
                               obj.last_modified.day,
                               obj.last_modified.year)

        if 'sizemb' in metadata:
            size = '%sMB' % metadata['sizemb']

        results.append([obj.key, datestr, size ])
   
    if len(results) == 0:
        bot.info("No container collections found.")
        sys.exit(1)

    if not quiet:
        bot.info("Containers")
        bot.table(results)
    return results


def container_search(self, query, across_collections=False):
    '''search for a specific container. If across collections is False,
    the query is parsed as a full container name and a specific container
    is returned. If across_collections is True, the container is searched
    for across collections. If across collections is True, details are
    not shown'''


    results = self._search_all(quiet=True)
    matches = []
    for result in results:

        # This is the container name
        if query in result[0]:
            matches.append(result)


    if len(matches) > 0:
        bot.info("Containers %s" % query)
        bot.table(matches)
    else:
        bot.info('No matches for %s found.' % query)

    return matches
