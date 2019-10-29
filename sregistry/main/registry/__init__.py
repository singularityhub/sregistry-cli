'''

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.auth import read_client_secrets
from sregistry.main import ApiConnection
import json
import os

from .auth import authorize
from .build import build
from .pull import pull
from .push import push
from .delete import delete
from .query import (
    search,
    search_all,
    collection_search,
    label_search,
    container_search,
)

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self.base = base
        super(Client, self).__init__(**kwargs)
        self._update_secrets()
        self._update_headers()

    def _update_base(self):
        if self.base is not None:
            self.base = self.base.strip('/')
            if not self.base.endswith('api'):
                self.base = "%s/api" % self.base


    def _read_response(self,response, field="detail"):
        '''attempt to read the detail provided by the response. If none, 
        default to using the reason'''

        try:
            message = json.loads(response._content.decode('utf-8'))[field]
        except:
            message = response.reason
        return message


    def _add_https(self, q):
        '''for push, pull, and other api interactions, the user can optionally
           define a custom registry. If the registry name doesn't include http
           or https, add it.
 
           Parameters
           ==========
           q: the parsed image query (names), including the original
        '''

        # If image uses http or https, add back
        if not q['registry'].startswith('http'):

            if q['original'].startswith('http:'):
                q['registry'] = 'http://%s' % q['registry']

            elif q['original'].startswith('https:'):
                q['registry'] = 'https://%s' % q['registry']

            # Otherwise, guess from the user's environment
            else:

                prefix = 'https://'

                # The user can set an environment variable to specify nohttps
                nohttps = os.environ.get('SREGISTRY_REGISTRY_NOHTTPS')
                if nohttps is not None:
                    prefix = 'http://'
                q['registry'] = '%s%s' %(prefix, q['registry'])

        return q


    def _update_secrets(self):
        '''update secrets will use the SREGISTRY_REGISTRY_BASE to determine which API base url
           to use for the registry. If not present, the .sregistry secrets credential file
           either located at $HOME/.sregistry or the environment variable
           SREGISTRY_CLIENT_SECRETS will be used instead.
        '''
        self.base = self._get_and_update_setting('SREGISTRY_REGISTRY_BASE')

        if self.base is None:
            self.base = self._get_and_update_setting('base')

            if self.base is not None:
                self._update_setting('SREGISTRY_REGISTRY_BASE', self.base)

        self._update_base()

    def __str__(self):
        return type(self)



Client.authorize = authorize
Client.build = build
Client.delete = delete
Client.pull = pull
Client.push = push
Client.search = search
Client._search_all = search_all
Client._collection_search = collection_search
Client._container_search = container_search
Client._label_search = label_search
