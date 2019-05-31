'''

sregistry.api: base template for making a connection to an API

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.main.base.auth import (
    require_secrets,
    auth_flow
)

from sregistry.main.base.headers import (
    get_headers,
    reset_headers,
    update_headers
)

from sregistry.main.base.http import ( 
    call, delete, download, get, head, healthy, 
    paginate_get, post, put, stream, 
    stream_response, verify
)

from sregistry.main.base.inspect import (
    get_metadata
)

from sregistry.main.base.settings import (
    get_setting,
    get_settings,
    get_storage_name,
    get_and_update_setting,
    required_get_and_update,
    update_setting
)

from sregistry.logger import bot
from sregistry.defaults import SREGISTRY_DATABASE
import os

class ApiConnection(object):

# Setup

    def __init__(self):
 
        self.headers = None
        self.base = None
        self._reset_headers()

        # If client initialized with _init_db, do it
        if hasattr(self,"_init_db"):
            self._init_db(SREGISTRY_DATABASE)


# Metadata

    def _client_tagged(self, tags):
        '''ensure that the client name is included in a list of tags. This is
           important for matching builders to the correct client. We exit
           on fail.
            
           Parameters
           ==========
           tags: a list of tags to look for client name in

        '''

        # We must match the client to a tag
        name = self.client_name.lower()
        tags = [t.lower() for t in tags]

        if name not in tags:
            bot.exit('%s not found in %s, must match!' %(name, tags))

    def speak(self):
        '''
           a function for the client to announce him or herself, depending
           on the level specified. If you want your client to have additional
           announced things here, then implement the class `_speak` for your
           client.

        '''
        if self.quiet is False:
            bot.info('[client|%s] [database|%s]' %(self.client_name,
                                                   self.database))

            if hasattr(self, '_speak'):
                self._speak()

    def _speak(self):
        '''this function should be subclassed if the client has additional
           information to give the user, beyond it's name and the database
           location. Be careful about adding extra prints to various functions
           because with a command like "get" the expectation is to print a
           download url (and nothing else)
        '''
        pass # pylint: disable=unnecessary-pass

    def announce(self, command=None):
        '''the client will announce itself given that a command is not in a
           particular predefined list.
        '''
        if command is not None:
            if command not in ['get'] and self.quiet is False:
                self.speak()


    def __repr__(self):
        return "[client][%s]" %self.client_name

    def __str__(self):
        return "[client][%s]" %self.client_name

    def client_name(self):
        return self.__module__.split('.')[-1]

# Headers
ApiConnection._get_headers = get_headers
ApiConnection._reset_headers = reset_headers
ApiConnection._update_headers = update_headers

# Settings
ApiConnection.require_secrets = require_secrets
ApiConnection._get_setting = get_setting
ApiConnection._get_settings = get_settings
ApiConnection._get_and_update_setting = get_and_update_setting
ApiConnection._required_get_and_update = required_get_and_update
ApiConnection._get_storage_name = get_storage_name
ApiConnection._update_setting = update_setting

# Metadata
ApiConnection.get_metadata = get_metadata

# Auth
ApiConnection.require_secrets = require_secrets
ApiConnection._auth_flow = auth_flow

# Http and Requests
ApiConnection._call = call
ApiConnection._delete = delete
ApiConnection.download = download
ApiConnection._get = get
ApiConnection._head = head
ApiConnection._healthy = healthy
ApiConnection._paginate_get = paginate_get
ApiConnection._post = post
ApiConnection._put = put
ApiConnection.stream = stream
ApiConnection._stream = stream_response
ApiConnection._verify = verify
