'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.auth import get_credential_cache
from sregistry.defaults import SREGISTRY_DATABASE


def get_client(quiet=False, init=True, **kwargs):
    '''
       get the Google Build client.

       Parameters
       ==========
       quiet: if True, suppress most output about the client (e.g. speak)

    '''
    from . import Client
    Client.client_name = "google-build"
    Client.quiet = quiet

    # The user can provide environment variables via extra arguments here
    Client.envars = kwargs

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
    cli = Client(init=init)

    if hasattr(Client, '_init_db'):
        cli._init_db(SREGISTRY_DATABASE)
    return cli
