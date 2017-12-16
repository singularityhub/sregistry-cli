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

    # Switch based on client secrets set or found
    if os.environ.get('SREGISTRY_CLIENT_SECRETS') is None:
        from .hub import Client
        cli = Client
    else:
        from .registry import Client
        cli = Client

    return cli

Client = get_client()
