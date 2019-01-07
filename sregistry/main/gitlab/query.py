'''

Copyright (C) 2018-2019 Vanessa Sochat.

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
from sregistry.utils import remove_uri
from dateutil import parser
import requests

import json
import sys
import os

try:
    from urllib.parse import quote_plus # python 3.*
except:
    from urllib import quote_plus  # python 2.*


def search(self, query=None, args=None):
    '''query a GitLab artifacts folder for a list of images. 
     If query is None, collections are listed. 
    '''
    if query is None:
        bot.exit('You must include a collection query, <collection>/<repo>')

    # or default to listing (searching) all things.
    return self._search_all(query)


def search_all(self, collection, job_id=None):
    '''a "show all" search that doesn't require a query
       the user is shown URLs to 
    '''

    results = [['job_id', 'browser']]
 
    url = "%s/projects/%s/jobs" %(self.api_base, 
                                  quote_plus(collection.strip('/')))

    response = requests.get(url, headers=self.headers) 
    if response.status_code == 200:
        jobs = response.json()

        # We can't get a listing of artifacts
        # https://gitlab.com/gitlab-org/gitlab-ce/issues/51515
        # Parse through jobs (each can have different tags for a collection):
        for job in jobs:

            # Only show jobs that are successful
            if job['status'] == 'success':
                name = job['name']

                for artifact in job['artifacts']:
                    if artifact['filename'].endswith('zip'):
                        
                        # The user must browse to see the names
                        artifact_url = ("%s/%s/-/jobs/%s/artifacts/browse/%s" 
                                        %(self.base , 
                                          collection, 
                                          job['id'],
                                          name))
                        results.append([str(job['id']), artifact_url])   

    if len(results) == 1:
        bot.info("No potential archives found in artifacts.")
        sys.exit(0)

    bot.info("Artifact Browsers (you will need path and job id for pull)")
    bot.table(results)
    return results
