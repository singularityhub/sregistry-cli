'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.auth import basic_auth_header
from sregistry.main import ApiConnection
import json
import os

# The core of nvidia is actually docker
from sregistry.main.docker.api import ( 
    get_config, 
    get_environment_tar, 
    get_download_cache,
    get_size
)
from sregistry.main.aws.api import (
    download_layers,
    update_token,
    get_digests,
    get_manifest
)
from .pull import (
    pull, _pull
)

class Client(ApiConnection):

    def __init__(self, secrets=None, **kwargs):
        '''to work with nvidia container registry. If you need help with
           their API, the best reference is:

           https://docs.aws.amazon.com/AmazonECR/latest/APIReference/ecr-api.pdf
 
        '''
        self.reverseLayers = False
        self._reset_headers()
        self._update_secrets()
        self._set_base()
        self._update_headers()
        super(Client, self).__init__(**kwargs)


    def _reset_headers(self):
        '''reset headers is called from update_headers, and will update the
           headers based on what is found with the client secrets
        '''

        # specify wanting version 2 schema
        # meaning the correct order of digests
        # returned (base to child)
        accept = 'application/vnd.docker.distribution.manifest.v2+json,'
        accept += 'application/vnd.docker.distribution.manifest.list.v2+json,'
        accept += 'application/json'

        self.headers = {"Accept": accept,
                        "Accept-Encoding": "identity",
                        'Content-Type': 'application/x-amz-json-1.1; application/json; charset=utf-8'}

    def _set_base(self, zone=None):
        '''set the API base or default to use Docker Hub. The user is able
           to set the base, api version, and protocol via a settings file
           of environment variables:
        '''
        if hasattr(self.aws._client_config, 'region_name'):
            zone = self.aws._client_config.region_name

        aws_id = self._required_get_and_update('SREGISTRY_AWS_ID')
        aws_zone = self._required_get_and_update('SREGISTRY_AWS_ZONE', zone)
        version = self._get_setting('SREGISTRY_AWS_VERSION', 'v2')
        base = self._get_setting('SREGISTRY_AWS_BASE')

        if base is None:
            base = "%s.dkr.ecr.%s.amazonaws.com" % (aws_id, aws_zone)

        nohttps = self._get_setting('SREGISTRY_AWS_NOHTTPS')
        if nohttps is None:
            nohttps = "https://"
        else:
            nohttps = "http://"

        # <protocol>://<base>/<version>
        self.base = "%s%s/%s" %(nohttps, base.strip('/'), version)

    def _update_secrets(self):
        '''update secrets will take a secrets credential file
           either located at .sregistry or the environment variable
           SREGISTRY_CLIENT_SECRETS and update the current client 
           secrets as well as the associated API base. For the case of
           using Docker Hub, if we find a .docker secrets file, we update
           from there.
        '''
        bot.debug('Creating aws client...')
        try:
            from awscli.clidriver import create_clidriver
        except:
            bot.exit('Please install pip install sregistry[aws]')

        driver = create_clidriver()
        self.aws = driver.session.create_client('ecr')
        

    def __str__(self):
        return type(self)


# Functions exposed to the client
Client.pull = pull
Client._pull = _pull

# Api functions for image layers and manifests (hidden)
Client._download_layers = download_layers
Client._get_digests = get_digests
Client._get_download_cache = get_download_cache
Client._get_manifest = get_manifest
Client._get_size = get_size
Client._update_token = update_token
Client._get_environment_tar = get_environment_tar
