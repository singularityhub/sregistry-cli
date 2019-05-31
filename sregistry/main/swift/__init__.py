'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

import swiftclient
from sregistry.logger import bot
from sregistry.main import ApiConnection
import sys

from .pull import pull
from .push import push
from .query import (search, search_all, container_query)

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self.config = dict()
        self._update_secrets()
        self.name = self.config.get('SREGISTRY_SWIFT_URL', 'Swift Client Storage')
        super(Client, self).__init__(**kwargs)

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

        # Get the swift authentication type first.  That will determine what we
        # will need to collect for proper authentication
        self.config['SREGISTRY_SWIFT_AUTHTYPE'] = self._required_get_and_update(
                                                     'SREGISTRY_SWIFT_AUTHTYPE')

        # Check what auth version is requested and setup the connection
        if self.config['SREGISTRY_SWIFT_AUTHTYPE'] == 'preauth':

            # Pre-Authenticated Token/URL - Use OS_AUTH_TOKEN/OS_STORAGE_URL
            # Retrieve the user token, user, and base. Exit if not found 
            for envar in ['SREGISTRY_SWIFT_OS_AUTH_TOKEN',
                          'SREGISTRY_SWIFT_OS_STORAGE_URL' ]:
                self.config[envar] = self._required_get_and_update(envar)

            self.conn = swiftclient.Connection(
                preauthurl=self.config['SREGISTRY_SWIFT_OS_STORAGE_URL'],
                preauthtoken=self.config['SREGISTRY_SWIFT_OS_AUTH_TOKEN']
            )
        elif self.config['SREGISTRY_SWIFT_AUTHTYPE'] == 'keystonev3':

            # Keystone v3 Authentication
            # Retrieve the user token, user, and base. Exit if not found 
            for envar in ['SREGISTRY_SWIFT_USER',
                          'SREGISTRY_SWIFT_TOKEN',
                          'SREGISTRY_SWIFT_URL']:
                self.config[envar] = self._required_get_and_update(envar)

            auth_url = '%s/v3' % self.config['SREGISTRY_SWIFT_URL']
            # Setting to default as a safety.  No v3 environment to test
            # May require ENV vars for real use. - M. Moore
            _os_options = {
                'user_domain_name': 'Default',
                'project_domain_name': 'Default',
                'project_name': 'Default'
            }

            # Save the connection to use for some command
            self.conn = swiftclient.Connection(
                user=self.config['SREGISTRY_SWIFT_USER'],
                key=self.config['SREGISTRY_SWIFT_TOKEN'],
                os_options=_os_options,
                authurl=auth_url,
                auth_version='3'
            )

        elif self.config['SREGISTRY_SWIFT_AUTHTYPE'] == 'keystonev2':

            # Keystone v2 Authentication
            # Retrieve the user token, user, and base. Exit if not found 
            for envar in ['SREGISTRY_SWIFT_USER',
                          'SREGISTRY_SWIFT_TOKEN',
                          'SREGISTRY_SWIFT_TENANT',
                          'SREGISTRY_SWIFT_REGION',
                          'SREGISTRY_SWIFT_URL']:
                self.config[envar] = self._required_get_and_update(envar)

            # More human friendly to interact with
            auth_url = '%s/v2.0/' % self.config['SREGISTRY_SWIFT_URL']
            # Set required OpenStack options for tenant/region
            _os_options = {
                'tenant_name': self.config['SREGISTRY_SWIFT_TENANT'],
                'region_name': self.config['SREGISTRY_SWIFT_REGION']
            }

            # Save the connection to use for some command
            self.conn = swiftclient.Connection(
                user=self.config['SREGISTRY_SWIFT_USER'],
                key=self.config['SREGISTRY_SWIFT_TOKEN'],
                os_options=_os_options,
                authurl=auth_url,
                auth_version='2'
            )
        else:

            # Legacy Authentication
            # Retrieve the user token, user, and base. Exit if not found 
            for envar in ['SREGISTRY_SWIFT_USER',
                          'SREGISTRY_SWIFT_TOKEN',
                          'SREGISTRY_SWIFT_URL']:
                self.config[envar] = self._required_get_and_update(envar)

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
