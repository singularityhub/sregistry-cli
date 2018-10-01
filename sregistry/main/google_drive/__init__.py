'''

Copyright (C) 2017-2018 Vanessa Sochat.

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
from oauth2client.file import Storage
from oauth2client import tools

import httplib2
import sys
import os

from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client import client as oclient

from .utils import ( create_folder, get_or_create_folder )
from .pull import pull
from .push import push
from .share import share
from .query import ( container_query, list_containers, search, search_all )

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self._update_secrets()
        self._update_headers()
        self._init_client()
        super(ApiConnection, self).__init__(**kwargs)


    def _speak(self):
        '''add the bucket name to be printed to the user at appropriate times
        '''
        bot.info('[folder][%s]' %self._base)


    def _update_secrets(self):
        '''The user is required to have an application secrets file in his
           or her environment. The client exists with error 
           if the variable isn't found.
        '''
        env = 'SREGISTRY_GOOGLE_DRIVE_CREDENTIALS'
        self._secrets = self._get_and_update_setting(env)
        self._base = self._get_and_update_setting('SREGISTRY_GOOGLE_DRIVE_ROOT')

        if self._base is None:
            self._base = 'sregistry'

        if self._secrets is None:
            bot.error('You must export %s to use Google Drive client' %env)
            bot.info("https://singularityhub.github.io/sregistry-cli/client-google-drive")
            sys.exit(1)


    def _init_client(self):
        '''init client will check if the user has defined a bucket that
           differs from the default, use the application credentials to 
           get the bucket, and then instantiate the client.
        '''
        self._scope = 'https://www.googleapis.com/auth/drive'
        self._service = self._get_service()


    def _get_service(self, version='v3'):
        '''get service client for the google drive API
        :param version: version to use (default is v3)
        '''
        invalid = True

        # The user hasn't disabled cache of credentials
        if self._credential_cache is not None:
            storage = Storage(self._credential_cache)

            # The store has never been used before
            if os.path.exists(self._credential_cache):
                credentials = storage.get()
                if not credentials.invalid:
                    invalid = False

        # If credentials are allowed but invalid, refresh
        if invalid is True:
            
            class flags:
                auth_host_name='localhost'
                auth_host_port=[8080]
                noauth_local_webserver=False
                logging_level='INFO'
            flow = oclient.flow_from_clientsecrets(self._secrets, self._scope)
            credentials = tools.run_flow(flow, storage, flags)

            # If the user is ok to cache them
            if self._credential_cache is not None:
                storage.put(credentials)

        # Either way, authenticate the user with credentials
        http = credentials.authorize(httplib2.Http())
        return build('drive', version, http=http)


# Add your different functions imported at the top to the client here
Client.pull = pull
Client.push = push
Client.share = share

Client._get_or_create_folder = get_or_create_folder
Client._create_folder = create_folder

Client.search = search
Client._search_all = search_all
Client._container_query = container_query
Client._list_containers = list_containers
