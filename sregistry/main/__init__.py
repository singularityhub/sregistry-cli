'''

This is a base client that imports functions depending on the API it is 
    using. Currently, it supports singularity hub and registry, with default
    to use Singularity Hub.

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.main.base import ApiConnection

from sregistry.utils import ( 
    check_install, 
    get_uri 
)
from sregistry.auth import get_credential_cache
from sregistry.defaults import SREGISTRY_DATABASE
from sregistry.logger import bot
import os

def get_client(image=None, quiet=False, **kwargs):
    '''
       get the correct client depending on the driver of interest. The
       selected client can be chosen based on the environment variable
       SREGISTRY_CLIENT, and later changed based on the image uri parsed
       If there is no preference, the default is to load the singularity 
       hub client.

       Parameters
       ==========
       image: if provided, we derive the correct client based on the uri
       of an image. If not provided, we default to environment, then hub.
       quiet: if True, suppress most output about the client (e.g. speak)

    '''
    from sregistry.defaults import SREGISTRY_CLIENT

    # Give the user a warning:
    if not check_install():
        bot.warning('Singularity is not installed, function might be limited.')

    # If an image is provided, use to determine client
    client_name = get_uri(image)
    if client_name is not None:
        SREGISTRY_CLIENT = client_name

    # If no obvious credential provided, we can use SREGISTRY_CLIENT
    if   SREGISTRY_CLIENT == 'aws': from .aws import Client
    elif SREGISTRY_CLIENT == 'docker': from .docker import Client
    elif SREGISTRY_CLIENT == 'dropbox': from .dropbox import Client
    elif SREGISTRY_CLIENT == 'gitlab': from .gitlab import Client
    elif SREGISTRY_CLIENT == 'globus': from .globus import Client
    elif SREGISTRY_CLIENT == 'nvidia': from .nvidia import Client
    elif SREGISTRY_CLIENT == 'hub': from .hub import Client
    elif SREGISTRY_CLIENT == 'google-drive': from .google_drive import Client
    elif SREGISTRY_CLIENT == 'google-compute': from .google_storage import Client
    elif SREGISTRY_CLIENT == 'google-storage': from .google_storage import Client
    elif SREGISTRY_CLIENT == 'google-build': from .google_build import Client
    elif SREGISTRY_CLIENT == 'registry': from .registry import Client
    elif SREGISTRY_CLIENT == 's3': from .s3 import Client
    elif SREGISTRY_CLIENT == 'swift': from .swift import Client
    else: from .hub import Client

    Client.client_name = SREGISTRY_CLIENT
    Client.quiet = quiet

    # Create credentials cache, if it doesn't exist
    Client._credential_cache = get_credential_cache()

    # Add the database, if wanted
    if SREGISTRY_DATABASE is not None:

        # These are global functions used across modules
        from sregistry.database import (
            init_db, add, cp, get, mv, rm, 
            images, inspect,
            rename,
            get_container,
            get_collection, 
            get_or_create_collection 
        )

        # Actions
        Client._init_db = init_db
        Client.add = add
        Client.cp = cp
        Client.get = get
        Client.inspect = inspect
        Client.mv = mv
        Client.rename = rename
        Client.rm = rm
        Client.images = images

        # Collections
        Client.get_or_create_collection = get_or_create_collection
        Client.get_container = get_container
        Client.get_collection = get_collection

    # If no database, import dummy functions that return the equivalent
    else:
        from sregistry.database import ( add, init_db )
        Client.add = add
        Client._init_db = init_db        

    # Initialize the database
    cli = Client()

    if hasattr(Client, '_init_db'):
        cli._init_db(SREGISTRY_DATABASE)
    return cli
