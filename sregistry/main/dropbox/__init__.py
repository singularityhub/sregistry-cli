'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from dropbox import Dropbox
from sregistry.logger import bot
from sregistry.main import ApiConnection
import datetime

from .pull import pull
from .push import push
from .query import (search, search_all, container_query)
from .share import share

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        # update token from the environment
        self._update_secrets()
        super(Client, self).__init__(**kwargs)

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
                if isinstance(value, (str, datetime.datetime, bool, int, float)):
                    metadata[key.strip('_')] = value
        
        return self.get_metadata(image_file, names=metadata)


    def _update_secrets(self):
        '''update secrets will look for a dropbox token in the environment at
           SREGISTRY_DROPBOX_TOKEN and if found, create a client. If not,
           an error message is returned and the client exits.
        '''

        # Retrieve the user token. Exit if not found 
        token = self._required_get_and_update('SREGISTRY_DROPBOX_TOKEN')

        # Create the dropbox client
        self.dbx = Dropbox(token)

        # Verify that the account is valid
        try:
            self.account = self.dbx.users_get_current_account()
        except:
            bot.exit('Account invalid. Exiting.')


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
Client.share = share

# Query functions
Client.search = search
Client._search_all = search_all
Client._container_query = container_query
