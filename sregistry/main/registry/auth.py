'''

auth.py: authorization functions for client

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.main.registry.utils import (
    generate_signature,
    generate_credential,
    generate_timestamp
)

from sregistry.logger import bot

def authorize(self, names, payload=None, request_type="push"):
    '''Authorize a client based on encrypting the payload with the client
       token, which should be matched on the receiving server'''

    self.username = self._get_and_update_setting('SREGISTRY_REGISTRY_USERNAME')

    if self.username is None:
        # backwards compatibility
        self.username = self._get_and_update_setting('username')

        if self.username is None:
            bot.exit('Failed to authorize: please set SREGISTRY_REGISTRY_USERNAME to an appropriate value')
        else:
            self._update_setting('SREGISTRY_REGISTRY_USERNAME', self.username)

    self.token = self._get_and_update_setting('SREGISTRY_REGISTRY_TOKEN')

    if self.token is None:
        # backwards compatibility
        self.token = self._get_and_update_setting('token')

        if self.token is None:
            bot.exit('Failed to authorize: please set SREGISTRY_REGISTRY_TOKEN to an appropriate value')
        else:
            self._update_setting('SREGISTRY_REGISTRY_TOKEN', self.token)


    # Use the payload to generate a digest   push|collection|name|tag|user
    timestamp = generate_timestamp()
    credential = generate_credential(self.username)
    credential = "%s/%s/%s" %(request_type,credential,timestamp)

    if payload is None:
        payload = "%s|%s|%s|%s|%s|" %(request_type,
            names['collection'],
            timestamp,
            names['image'],
            names['tag'])

    signature = generate_signature(payload, self.token)
    return "SREGISTRY-HMAC-SHA256 Credential=%s,Signature=%s" %(credential,signature)
