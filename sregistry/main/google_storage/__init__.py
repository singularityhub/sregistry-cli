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
import google
import json
import sys
import os

from retrying import retry
from google.cloud import storage
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from googleapiclient.errors import HttpError

# from .pull import pull
from .push import ( push, upload )
# from .record import record
# from .query import search


# The name for the new bucket
bucket_name = 'my-new-bucket'

# Creates the new bucket
bucket = storage_client.create_bucket(bucket_name)

print('Bucket {} created.'.format(bucket.name))

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self._update_secrets()
        self._update_headers()
        self._init_client()
        super(ApiConnection, self).__init__(**kwargs)

    def _update_secrets(self):
        '''The user is required to have an application secrets file in his
           or her environment, which if found, gets exported to the secrets 
           file. If not, 
        '''
        env = 'GOOGLE_APPLICATION_CREDENTIALS'
        self.secrets = self._get_and_update_setting(env)
        if self.secrets is None:
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
        if self.bucket_name is None:
            self.bucket_name = 'sregistry-%s' %os.environ['USER']
        self._get_bucket()


    def _get_service(self):
        '''get version 1 of the google storage API
        :param version: version to use (default is v1)
        '''
        return storage.Client()


    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def _get_bucket(self):
        '''get a bucket based on a bucket name. If it doesn't exist, create it.
        '''
        try:
            self._bucket = self._service.get_bucket(self.bucket_name)
        except google.cloud.exceptions.NotFound:
            self._bucket = self._service.create_bucket(self.bucket_name)
        bot.info('[bucket][%s]' %self.bucket_name)
        return self._bucket


    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=10)
    def _delete(object_name):
        '''delete_file will delete a file from a bucket
            object_name: the "name" parameter of the object.
        '''
        try:
            operation = self._service.objects().delete(bucket=self.bucket,
                                                       object=object_name).execute()
        except HttpError as e:
            pass
            operation = e
        return operation



# Add your different functions imported at the top to the client here
# Client.pull = pull
Client.push = push
Client._upload = upload
# Client.record = record
# Client.search = search
