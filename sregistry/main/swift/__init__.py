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

import swiftclient
from sregistry.logger import bot
from sregistry.main import ApiConnection
import sys

from .pull import pull
from .push import push
from .query import ( search, search_all, container_query )

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self.config = dict()
        self._update_secrets()
        self.name = self.config.get('SREGISTRY_SWIFT_URL', 'Swift Client Storage')
        super(ApiConnection, self).__init__(**kwargs)

    def _speak(self):
        '''if you want to add an extra print (of a parameter, for example)
           for the user when the client initalizes, write it here, eg:
           bot.info('[setting] value')
        '''
        if hasattr(self, 'account'):
            bot.info('connected to %s' % self.name)

    def get_collections(self):
        '''get a listing of collections that the user has access to.
        '''
        collections = []
        for container in self.conn.get_account()[1]:
            collections.append(container['name'])
        return collections

    def _get_collection(self, name):
        '''get a collection name, which corresponds to an upper level 
           "container" in ceph storage. If we find and get it, return it.
           If it doesn't exist, return None. To get and create, use
           get_and_create_collection()
        '''
        return self.conn.get_container(name)

    def _get_or_create_collection(self, name):
        '''get or create a collection, meaning that if the get returns
           None, create and return the response to the user.
 
           Parameters
           ==========
           name: the name of the collection to get (and create)
        '''
        try:     
            collection = self._get_collection(name)
        except:
            bot.info('Creating collection %s...' % name)
            collection = self.conn.put_container(name)
        return collection


    def _update_secrets(self):
        '''update secrets will look for a user and token in the environment
           If we find the values, cache and continue. Otherwise, exit with error
        '''

        # Retrieve the user token, user, and base. Exit if not found 
        for envar in ['SREGISTRY_SWIFT_USER',
                      'SREGISTRY_SWIFT_TOKEN',
                      'SREGISTRY_SWIFT_URL']:
            self.config[envar] = self._get_and_update_setting(envar)

            # All variables are required
            if self.config[envar] is None:
                bot.error('You must export %s to use client.' % envar)
                sys.exit(1)

        # More human friendly to interact with
        auth_url = '%s/auth/' % self.config['SREGISTRY_SWIFT_URL']

        # Save the connection to use for some command
        self.conn = swiftclient.Connection(
            user=self.config['SREGISTRY_SWIFT_USER'],
            key=self.config['SREGISTRY_SWIFT_TOKEN'],
            authurl=auth_url,
        )

    def __str__(self):
        return type(self)


# Add your different functions imported at the top to the client here
Client.pull = pull
Client.push = push

# Query functions
Client.search = search
Client._search_all = search_all
Client._container_query = container_query
