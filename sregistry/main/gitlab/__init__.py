'''

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
from sregistry.main import ApiConnection
import sys
import re

from .pull import pull
from .query import ( search, search_all, container_query )

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self._reset_headers()
        self._update_secrets()
        self._update_base()
        super(ApiConnection, self).__init__(**kwargs)

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
        self.token = self._get_and_update_setting('SREGISTRY_GITLAB_TOKEN')
        if self.token is None:
            bot.exit('You must export SREGISTRY_GITLAB_TOKEN to authenticate.')
        self.headers["Private-Token"] = self.token

    def __str__(self):
        return type(self)

    def get_metadata(self):
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

# Add your different functions imported at the top to the client here
Client.pull = pull

# Query functions
Client.search = search
Client._search_all = search_all
Client._container_query = container_query
