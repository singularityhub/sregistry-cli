'''

auth.py: authorization functions for client

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.main.registry.utils import (
    generate_signature,
    generate_credential,
    generate_timestamp
)

def authorize(self, names, payload=None, request_type="push"):
    '''Authorize a client based on encrypting the payload with the client
       token, which should be matched on the receiving server'''

    if self.secrets is not None:

        if "registry" in self.secrets:

            # Use the payload to generate a digest   push|collection|name|tag|user
            timestamp = generate_timestamp()
            credential = generate_credential(self.secrets['registry']['username'])
            credential = "%s/%s/%s" %(request_type,credential,timestamp)

            if payload is None:
                payload = "%s|%s|%s|%s|%s|" %(request_type,
                                              names['collection'],
                                              timestamp,
                                              names['image'],
                                              names['tag'])

            signature = generate_signature(payload,self.secrets['registry']['token'])
            return "SREGISTRY-HMAC-SHA256 Credential=%s,Signature=%s" %(credential,signature)
