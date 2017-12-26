'''

This is a base client that imports functions depending on the API it is 
    using. Currently, it supports singularity hub and registry, with default
    to use Singularity Hub.

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

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

from .base import ApiConnection
from sregistry.utils import check_install
from sregistry.defaults import (
    SREGISTRY_DATABASE, 
    SREGISTRY_CLIENT
)
from sregistry.logger import bot
import os


def get_client():
    '''get the correct client depending on the driver of interest. If 
       a secrets file for a particular storage is found in the environment
       we load and check client secrets. If not, we default 
       to the singularity hub client. If a user has a conflict with
       multiple secrets active, we can add another kind of logic.
    '''
    # Give the user a warning:
    if not check_install():
        bot.warning('Singularity is not installed, function might be limited.')

    # If no obvious credential provided, we can use SREGISTRY_CLIENT
    if SREGISTRY_CLIENT == 'globus':
        from .globus import Client

    elif SREGISTRY_CLIENT == 'hub':
        from .hub import Client

    elif SREGISTRY_CLIENT == 'registry':
        from .registry import Client

    # Fall back to singularity hub (should never hit this)
    else:
        from .hub import Client

    Client.client_name = SREGISTRY_CLIENT

    # Add the database, if wanted
    if SREGISTRY_DATABASE is not None:

        # These are global functions used across modules
        from sregistry.database import (
            init_db, add, get, rm, rmi, ls, inspect,
            get_container,
            get_collection, 
            get_or_create_collection 
        )
        bot.info('[client|%s] [database|%s]' %(SREGISTRY_CLIENT,
                                               SREGISTRY_DATABASE))

        # Actions
        Client._init_db = init_db
        Client.add = add
        Client.get = get
        Client.inspect = inspect
        Client.rm = rm
        Client.rmi = rmi
        Client.ls = ls

        # Collections
        Client.get_or_create_collection = get_or_create_collection
        Client.get_container = get_container
        Client.get_collection = get_collection

    return Client()

Client = get_client()

# Initialize the database
if hasattr(Client, '_init_db'):
    Client._init_db(SREGISTRY_DATABASE)
