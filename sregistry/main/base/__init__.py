'''

sregistry.api: base template for making a connection to an API

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
    call, delete, download, get, paginate_get, 
    post, put, stream, stream_response, verify
)

from sregistry.main.base.inspect import (
    get_metadata
)

from sregistry.main.base.settings import (
    get_setting,
    get_storage_name,
    get_and_update_setting
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

            self._speak()


    def _speak(self):
        '''this function should be subclassed if the client has additional
           information to give the user, beyond it's name and the database
           location. Be careful about adding extra prints to various functions
           because with a command like "get" the expectation is to print a
           download url (and nothing else)
        '''
        pass

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
ApiConnection._get_and_update_setting = get_and_update_setting
ApiConnection._get_storage_name = get_storage_name

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
ApiConnection._paginate_get = paginate_get
ApiConnection._post = post
ApiConnection._put = put
ApiConnection.stream = stream
ApiConnection._stream = stream_response
ApiConnection._verify = verify
