'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
import requests


def logs(self, name=None):
    '''return logs for a particular container. The logs file is equivalent to
       the name, but with extension .log. If there is no name, the most recent
       log is returned.

       Parameters
       ==========
       name: the container name to print logs for.

    '''
    content = None
    results = self._list_logs()
    print(results)

    # If we are searching for a name
    if name is not None:
        for result in results:

            matches = False

            # Case 1: the name is in the storage path
            if name in result.name:
                matches=True

            # Case 2: match in metadata
            for _, val in result.metadata.items():
                if name in val:
                    matches = True

            if matches is True:
                content = self._print_log(result.name)  

    # Otherwise return the last
    else:

        if len(results) > 0:
            latest = results[0]
 
            # Get the most recent
            for result in results:
                if result.time_created >= latest.time_created:
                    latest = result                   
            content = self._print_log(latest.name)

    return content



def list_logs(self):
    '''return a list of logs. We return any file that ends in .log
    '''
    results = []
    for image in self._bucket.list_blobs():
        if image.name.endswith('log'):
            results.append(image)

    if len(results) == 0:
        bot.info("No containers found, based on extension .log")

    return results



def print_log(self, logname):
    '''helper function to retrieve a particular log, and print.
       
       Parameters
       ==========
       name: the name of the log to retrieve

    '''
    content = None

    # Try to retrieve the blob (log) if exists
    logfile = self._bucket.get_blob(logname)
    print(logname)
    if logfile:
        bot.info('[%s]' %logname)
        content = requests.get(logfile.media_link).text
        print(content)

    return content
