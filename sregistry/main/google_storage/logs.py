'''

Copyright (C) 2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2018 Vanessa Sochat.

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
import requests
import sys
import re
import os



def logs(self, name=None):
    '''return logs for a particular container. The logs file is equivalent to
       the name, but with extension .log. If there is no name, the most recent
       log is returned.

       Parameters
       ==========
       name: the container name to print logs for.

    '''
    content = None
    results = self._list_containers()
    print(results)

    # If we are searching for a name
    if name is not None:
        for result in results:

            matches = False

            # Case 1: the name is in the storage path
            if name in result.name:
                matches=True

            # Case 2: match in metadata
            for key,val in result.metadata.items():
                if name in val:
                    matches = True

            if matches is True:
                logname = re.sub('[.]simg$','.log', result.name)
                content = self._print_log(logname)                

    # Otherwise return the last
    else:

        if len(results) > 0:
            latest = results[0]
 
            # Get the most recent
            for result in results:
                if result.time_created >= latest.time_created:
                    latest = result                   
            logname = re.sub('[.]simg$','.log', latest.name)
            content = self._print_log(logname)                


    return content


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


