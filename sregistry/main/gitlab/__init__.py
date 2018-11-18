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

from .pull import pull
from .query import ( search, search_all, container_query )

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        # update token from the environment
        name = self._update_secrets()
        self._reset_headers()
        super(ApiConnection, self).__init__(**kwargs)

    def _update_secrets(self):
        '''update secrets will update metadata needed for pull and search
        '''

        self.base = self._get_and_update_setting('SREGISTRY_GITLAB_BASE',
                                                 'https://gitlab.com')

        self.artifacts = self._get_and_update_setting('SREGISTRY_GITLAB_FOLDER',
                                                      'build')

        self.job = self._get_and_update_setting('SREGISTRY_GITLAB_TEST', 'test')
        self.branch = self._get_and_update_setting('SREGISTRY_GITLAB_BRANCH',
                                                   'master')

        bot.debug('   Hosted: %s' % self.base)
        bot.debug('Artifacts: %s' % self.artifacts)
        bot.debug('   Branch: %s' % self.branch)
        bot.debug('      Job: %s' % self.job)

    def __str__(self):
        return type(self)


# Add your different functions imported at the top to the client here
Client.pull = pull

# Query functions
Client.search = search
Client._search_all = search_all
Client._container_query = container_query
