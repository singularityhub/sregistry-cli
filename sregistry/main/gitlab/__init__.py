'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.main import ApiConnection
import re

from .pull import pull
from .query import ( search, search_all )

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self._reset_headers()
        self._update_secrets()
        self._update_base()
        super(Client, self).__init__(**kwargs)

    def _update_base(self):
        '''update the base, including the URL for GitLab and the API endpoint.
        '''
        self.base = self._get_and_update_setting('SREGISTRY_GITLAB_BASE',
                                                 "https://gitlab.com/")
        self.api_base = "%s/api/v4" % self.base.strip('/')
        self.artifacts = self._get_and_update_setting('SREGISTRY_GITLAB_FOLDER',
                                                      'build')

        self.job = self._get_and_update_setting('SREGISTRY_GITLAB_JOB', 'build')

        bot.debug('      Api: %s' % self.api_base)
        bot.debug('Artifacts: %s' % self.artifacts)
        bot.debug('      Job: %s' % self.job)

    def _update_secrets(self):
        '''update secrets will update metadata needed for pull and search
        '''
        self.token = self._required_get_and_update('SREGISTRY_GITLAB_TOKEN')
        if self.headers is None:
            self.headers = {}
        self.headers["Private-Token"] = self.token

    def __str__(self):
        return type(self)

    def _get_metadata(self):
        '''since the user needs a job id and other parameters, save this
           for them.
        '''
        metadata = {'SREGISTRY_GITLAB_FOLDER': self.artifacts,
                    'api_base': self.api_base,
                    'SREGISTRY_GITLAB_BASE': self.base,
                    'SREGISTRY_GITLAB_JOB': self.job }
        return metadata

    def artifact_to_tag(self, filename):
        '''since the artifacts represent tags in GitLab (e.g., Singularity 
           converts to latest, others in format Singularity.<tag>.simg
           convert to <tag> this function provides a consistent means to do
           that conversion across the library. 

           Parameters
           ==========
           filename: the filename in storage to return
        '''
        if filename == "Singularity.simg":
            return "latest"
        return re.sub('.*Singularity[.]', '',filename).replace('.simg', '')

    def _parse_image_name(self, image, retry=True):
        '''starting with an image string in either of the following formats:
           job_id|collection
           job_id|collection|job_name
 
           Parse the job_name, job_id, and collection uri from it. If the user
           provides the first option, we use the job_name set by the client
           (default is build).
 
           Parameters
           ==========
           image: the string to parse, with values separated by |
           retry: the client can call itself recursively once, providing the
                  default job_name if the user doesn't.
        '''
        try:
            job_id, collection, job_name = image.split(',')
        except:
            # Retry and add job_name
            if retry:
                return self._parse_image_name("%s,%s" %(image, self.job),
                                              retry=False)

            # Or fail
            bot.exit('''Malformed image string! Please provide:
                        job_id,collection           (or)
                        job_id,collection,job_name''')

        return job_id, collection, job_name

# Add your different functions imported at the top to the client here
Client.pull = pull

# Query functions
Client.search = search
Client._search_all = search_all
