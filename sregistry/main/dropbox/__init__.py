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

from dropbox import Dropbox
from dropbox.exceptions import ( ApiError, AuthError )
from sregistry.logger import bot
from sregistry.main import ApiConnection
import sys
import datetime

from .pull import pull
from .push import push
from .record import record
from .query import ( search, search_all, container_query )
from .share import share

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        # update token from the environment
        name = self._update_secrets()
        super(ApiConnection, self).__init__(**kwargs)

    def _speak(self):
        '''if you want to add an extra print (of a parameter, for example)
           for the user when the client initalizes, write it here, eg:
           bot.info('[setting] value')
        '''
        if hasattr(self, 'account'):
            bot.info('connected to %s' %self.account.name.display_name)


    def _get_metadata(self, image_file=None, dbx_metadata=None):
        '''this is a wrapper around the main client.get_metadata to first parse
           a Dropbox FileMetadata into a dicionary, then pass it on to the 
           primary get_metadata function.

           Parameters
           ==========
           image_file: the full path to the image file that had metadata
                       extracted
           metadata: the Dropbox FileMetadata to parse.

        '''
        metadata = dict()

        if dbx_metadata is not None:
            for key in dbx_metadata.__dir__():
                value = getattr(dbx_metadata, key)
                if type(value) in [str, datetime.datetime, bool, int, float]:
                    metadata[key.strip('_')] = value
        
        return self.get_metadata(image_file, names=metadata)


    def _update_secrets(self):
        '''update secrets will look for a dropbox token in the environment at
           SREGISTRY_DROPBOX_TOKEN and if found, create a client. If not,
           an error message is returned and the client exits.
        '''

        # Retrieve the user token. Exit if not found 

        token = self._get_and_update_setting('SREGISTRY_DROPBOX_TOKEN')
        if token is None:
            bot.error('You must export SREGISTRY_DROPBOX_TOKEN to use client.')
            sys.exit(1)


        # Create the dropbox client
        self.dbx = Dropbox(token)

        # Verify that the account is valid
        try:
            self.account = self.dbx.users_get_current_account()
        except AuthError as err:
            bot.error('Account invalid. Exiting.')
            sys.exit(1)


    def __str__(self):
        return type(self)


    def exists(self, path):
        '''determine if a path exists, return False if not.'''
        try:
            self.dbx.files_get_metadata(path)
            return True
        except:
            return False


# Add your different functions imported at the top to the client here
Client.pull = pull
Client.push = push
Client.record = record
Client.share = share

# Query functions
Client.search = search
Client._search_all = search_all
Client._container_query = container_query
