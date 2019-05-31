'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import (
    mkdir_p,
    read_json,
    write_json
)

import os

def get_credential_cache():
    '''if the user has specified settings to provide a cache for credentials
       files, initialize it. The root for the folder is created if it doesn't
       exist. The path for the specific client is returned, and it's
       not assumed to be either a folder or a file (this is up to the
       developer of the client).
    '''
    from sregistry.defaults import (CREDENTIAL_CACHE, SREGISTRY_CLIENT)

    client_credential_cache = None

    # Check 1: user can disable a credential cache on the client level
    if CREDENTIAL_CACHE is not None:
        env = 'SREGISTRY_DISABLE_CREDENTIAL_%s' %SREGISTRY_CLIENT.upper()
        if os.environ.get(env) is not None:
            bot.debug('[%s] cache disabled' %SREGISTRY_CLIENT)
            CREDENTIAL_CACHE = None

    # Check 2: user can disable a credential cache on the client level
    if CREDENTIAL_CACHE is not None:
        if not os.path.exists(CREDENTIAL_CACHE):
            mkdir_p(CREDENTIAL_CACHE)
        client_credential_cache = '%s/%s' %(CREDENTIAL_CACHE, SREGISTRY_CLIENT)
    if client_credential_cache is not None:
        bot.debug('credentials cache')
    return client_credential_cache


def _default_client_secrets():
    '''return default client secrets, including singularity hub base
    '''
    client_secrets = {'hub': {'base': "https://singularity-hub.org/api" }}
    return client_secrets


def update_client_secrets(backend, updates, secrets=None, save=True):
    '''update client secrets will update the data structure for a particular
       authentication. This should only be used for a (quasi permanent) token
       or similar. The secrets file, if found, is updated and saved by default.
    '''
    if secrets is None:
        secrets = read_client_secrets()
    if backend not in secrets:
        secrets[backend] = {}
    secrets[backend].update(updates)

    # The update typically includes a save
    if save is True:
        secrets_file = get_secrets_file()
        if secrets_file is not None:
            write_json(secrets, secrets_file)

    return secrets

def read_client_secrets():
    '''for private or protected registries, a client secrets file is required
       to be located at .sregistry. If no secrets are found, we use default
       of Singularity Hub, and return a dummy secrets.
    '''
    client_secrets = _default_client_secrets()

    # If token file not provided, check environment
    secrets = get_secrets_file()

    # If exists, load
    if secrets is not None:
        client_secrets = read_json(secrets)

    # Otherwise, initialize
    else:
        from sregistry.defaults import SREGISTRY_CLIENT_SECRETS
        write_json(client_secrets, SREGISTRY_CLIENT_SECRETS)

    return client_secrets


def get_secrets_file():
    '''Sniff the environment and standard location for client
       secrets file. Otherwise, return None
    '''
    from sregistry.defaults import SREGISTRY_CLIENT_SECRETS
    if os.path.exists(SREGISTRY_CLIENT_SECRETS):
        return SREGISTRY_CLIENT_SECRETS
