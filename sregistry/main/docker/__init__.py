'''

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

from sregistry.logger import bot
from sregistry.auth import basic_auth_header
from sregistry.utils import read_json
from sregistry.main import ApiConnection
import json
import os

# here you should import the functions from the files in this
# folder that you add to your client (at the bottom)
from .api import ( create_metadata_tar, download_layers, get_manifest_selfLink,
                   get_config, get_digests, get_layer, get_layerLink, 
                   get_manifest, get_manifests, get_download_cache, get_size,
                   extract_env, extract_labels, extract_runscript,
                   update_token, get_environment_tar )
from .pull import ( _pull, pull )

class Client(ApiConnection):

    def __init__(self, secrets=None, **kwargs):
        '''to work with docker hub, we do the following:

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
        super(ApiConnection, self).__init__(**kwargs)

    def _speak(self):
        '''if you want to add an extra print (of a parameter, for example)
           for the user when the client initalizes, write it here, eg:
           bot.info('[setting] value')
        '''
        pass


    def _reset_headers(self):
        '''reset headers is called from update_headers, and will update the
           headers based on what is found with the client secrets.

           Note: that Docker expects different headers depending on the 
                 manifest desired. See:
                 https://docs.docker.com/registry/spec/manifest-v2-2/

        '''        
        self.headers = {"Accept": 'application/json',
                        'Content-Type': 'application/json; charset=utf-8'}

    def _update_base(self, image):
        ''' update a base based on an image name, meaning detecting a particular
            registry and if necessary, updating the self.base. When the image
            name is parsed, the base will be given to remove the registry.
        '''
        base = None

        # Google Container Cloud
        if "gcr.io" in image:
            base = 'gcr.io'
            self._set_base(default_base=base)
            self._update_secrets()

        return base


    def _set_base(self, default_base=None):
        '''set the API base or default to use Docker Hub. The user is able
           to set the base, api version, and protocol via a settings file
           of environment variables:
 
           SREGISTRY_DOCKERHUB_BASE: defaults to index.docker.io
           SREGISTRY_DOCKERHUB_VERSION: defaults to v1
           SREGISTRY_DOCKERHUB_NO_HTTPS: defaults to not set (so https)

        '''

        base = self._get_setting('SREGISTRY_DOCKERHUB_BASE')
        version = self._get_setting('SREGISTRY_DOCKERHUB_VERSION')

        # If we re-set the base after reading the image
        if base is None:
            if default_base is None:
                base = "index.docker.io"
            else:
                base = default_base

        if version is None:
            version = "v2"

        nohttps = self._get_setting('SREGISTRY_DOCKERHUB_NOHTTPS')
        if nohttps is None:
            nohttps = "https://"
        else:
            nohttps = "http://"

        # <protocol>://<base>/<version>

        self._base = "%s%s" %(nohttps, base)
        self._version = version
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
        credentials = self._get_setting('SREGISTRY_DOCKERHUB_SECRETS')

        # First try for SINGULARITY exported, then try sregistry
        username = self._get_setting('SINGULARITY_DOCKER_USERNAME')
        password = self._get_setting('SINGULARITY_DOCKER_PASSWORD')
        username = self._get_setting('SREGISTRY_DOCKERHUB_USERNAME', username)
        password = self._get_setting('SREGISTRY_DOCKERHUB_PASSWORD', password)

        # Option 1: the user exports username and password
        if username is not None and password is not None:
            auth = basic_auth_header(username, password)
            self.headers.update(auth)
        
        # Option 2: look in .docker config file
        if credentials is not None and auth is None:
            if os.path.exists(credentials):
                credentials = read_json(credentials)

                # Find a matching auth in .docker config
                if "auths" in credentials:
                    for auths, params in credentials['auths'].items():
                        if self._base in auths:
                            if 'auth' in params:
                                auth = "Basic %s" % params['auth']
                                self.headers['Authorization'] = auth


                # Also update headers
                if 'HttpHeaders' in credentials:
                    for key, value in credentials['HttpHeaders'].items():
                        self.headers[key] = value

            else:
                bot.warning('Credentials file set to %s, but does not exist.')



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
