'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2017 Vanessa Sochat.

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

from sregistry.logger import bot
from sregistry.utils import (
    read_json,
    write_json
)

from sregistry.defaults import SREGISTRY_CLIENT_SECRETS
from datetime import datetime, timezone
import base64
import hashlib
import hmac
import json
import os
import pwd
import requests
import sys


def _default_client_secrets():
    '''return default client secrets, including singularity hub base
    '''
    client_secrets = { 'hub': { 'base': "https://singularity-hub.org/api" } }
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
    secrets.update(updates)

    # The update typically includes a save
    if save is True:
        secrets_file = _get_secrets_file()
        if secrets_file is not None:
            write_json(secrets,secrets_file)

    return secrets

def read_client_secrets():
    '''for private or protected registries, a client secrets file is required
       to be located at .sregistry. If no secrets are found, we use default
       of Singularity Hub, and return a dummy secrets.
    '''
    client_secrets = _default_client_secrets()

    # If token file not provided, check environment
    secrets = _get_secrets_file()

    if secrets is not None:
        client_secrets = read_json(secrets)
    return client_secrets


def _get_secrets_file():
    '''Sniff the environment and standard location for client
       secrets file. Otherwise, return None
    '''
    if os.path.exists(SREGISTRY_CLIENT_SECRETS):
        return SREGISTRY_CLIENT_SECRETS
