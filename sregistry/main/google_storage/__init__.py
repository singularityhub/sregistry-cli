'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
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
import google
import json
import sys
import os

from retrying import retry
from google.cloud import storage
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

from .pull import pull
from .push import ( push, upload )
from .record import record
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
        bot.info('[bucket][%s]' %self._bucket_name)

    def _update_secrets(self):
        '''The user is required to have an application secrets file in his
           or her environment. The information isn't saved to the secrets
           file, but the client exists with error if the variable isn't found.
        '''
        env = 'GOOGLE_APPLICATION_CREDENTIALS'
        self._secrets = self._get_setting(env)
        if self._secrets is None:
            bot.error('You must export %s to use Google Storage client' %env)
            sys.exit(1)


    def _init_client(self):
        '''init client will check if the user has defined a bucket that
           differs from the default, use the application credentials to 
           get the bucket, and then instantiate the client.
        '''
        env = 'SREGISTRY_GOOGLE_STORAGE_BUCKET'
        self._bucket_name = self._get_and_update_setting(env)
        self._service = self._get_service()
        if self._bucket_name is None:
            self._bucket_name = 'sregistry-%s' %os.environ['USER']
        self._get_bucket()


    def _get_service(self, version='v1'):
        '''get version 1 of the google storage API
        :param version: version to use (default is v1)
        '''
        self._bucket_service = storage.Client()
        credentials = GoogleCredentials.get_application_default()
        return build('storage', version, credentials=credentials) 


    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def _get_bucket(self):
        '''get a bucket based on a bucket name. If it doesn't exist, create it.
        '''
        try:
            self._bucket = self._bucket_service.get_bucket(self._bucket_name)
        except google.cloud.exceptions.NotFound:
            self._bucket = self._bucket_service.create_bucket(self._bucket_name)
        return self._bucket



# Add your different functions imported at the top to the client here
Client.pull = pull
Client.push = push
Client._upload = upload
Client.record = record

Client.search = search
Client._search_all = search_all
Client._container_query = container_query
Client._list_containers = list_containers
