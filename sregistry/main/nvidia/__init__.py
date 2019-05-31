'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.auth import basic_auth_header
from sregistry.main import ApiConnection
import json
import sys
import os

# The core of nvidia is actually docker
from sregistry.main.docker.api import ( 
    create_metadata_tar, 
    download_layers, 
    get_manifest_selfLink,
    get_config, 
    get_digests,
    get_environment_tar, 
    get_layer,
    get_layerLink,
    get_manifest,
    get_manifests,
    get_download_cache,
    get_size,
    extract_env,
    extract_labels,
    extract_runscript,
    update_token
)

from sregistry.main.docker.pull import _pull
from .pull import pull

class Client(ApiConnection):

    def __init__(self, secrets=None, **kwargs):
        '''to work with nvidia container registry, we do the following:

        1. set the base to index.docker.io, or defined in environment 
        2. assume starting with v2 schema, we won't reverse layers 
        3. set headers to ask for version 2 schema first
        4. update secrets, 1st priority environment, then .docker/config.json 
        5. update headers based on secrets
 
        '''
        self._set_base()
        self.reverseLayers = False
        self._reset_headers()
        self._update_secrets()
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
                        'Content-Type': 'application/json; charset=utf-8'}

    def _set_base(self):
        '''set the API base or default to use Docker Hub. The user is able
           to set the base, api version, and protocol via a settings file
           of environment variables:
 
           SREGISTRY_NVIDIA_BASE: defaults to nvcr.io
           SREGISTRY_NVIDIA_TOKEN: defaults to $oauthtoken
           SREGISTRY_NVIDIA_VERSION: defaults to v2
           SREGISTRY_NVIDIA_NO_HTTPS: defaults to not set (so https)

        '''
        base = self._get_setting('SREGISTRY_NVIDIA_BASE')
        version = self._get_setting('SREGISTRY_NVIDIA_VERSION')

        if base is None:
            base = "nvcr.io"

        if version is None:
            version = "v2"

        nohttps = self._get_setting('SREGISTRY_NVIDIA_NOHTTPS')
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
        # If the user has defined secrets, use them
        token = self._required_get_and_update('SREGISTRY_NVIDIA_TOKEN')
        username = self._get_and_update_setting('SREGISTRY_NVIDIA_USERNAME')

        if username is None:
            username = "$oauthtoken"

        # Option 1: the user exports username and password
        if token is not None:
            auth = basic_auth_header(username, token)
            self.headers.update(auth)

    def __str__(self):
        return type(self)


# Functions exposed to the client
Client.pull = pull
Client._pull = _pull

# Api functions for image layers and manifests (hidden)
Client._create_metadata_tar = create_metadata_tar
Client._download_layers = download_layers
Client._extract_runscript = extract_runscript
Client._extract_labels = extract_labels
Client._extract_env = extract_env
Client._get_config = get_config
Client._get_digests = get_digests
Client._get_download_cache = get_download_cache
Client._get_layer = get_layer
Client._get_layerLink = get_layerLink
Client._get_manifest = get_manifest
Client._get_manifests = get_manifests
Client._get_size = get_size
Client._update_token = update_token
Client._get_manifest_selfLink = get_manifest_selfLink
Client._get_environment_tar = get_environment_tar
