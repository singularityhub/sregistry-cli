'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

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
from sregistry.auth import read_client_secrets
from sregistry.main import ApiConnection
import json
import sys
import os

# here you should import the functions from the files in this
# folder that you add to your client (at the bottom)
# from .pull import pull
# from .push import push
# from .record import record
# from .query import search

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        # You probably want to think about where  your base is coming from!
        self.base = base
        self._update_secrets()
        self._update_headers()
        super(ApiConnection, self).__init__(**kwargs)

    def _update_secrets(self):
        '''update secrets will take a secrets credential file
        either located at .sregistry or the environment variable
        SREGISTRY_CLIENT_SECRETS and update the current client 
        secrets as well as the associated API base. This is where you
        should do any customization of the secrets flie, or using
        it to update your client, if needed.
        '''
        self.secrets = read_client_secrets()
        if self.secrets is not None:
            if "base" in self.secrets:
                self.base = self.secrets['base']
                self._update_base()

    def __str__(self):
        return type(self)


# Add your different functions imported at the top to the client here
# Client.pull = pull
# Client.push = push
# Client.record = record
# Client.search = search
