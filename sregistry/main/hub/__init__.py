'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.main import ApiConnection

from .pull import pull
from .query import (
    search,
    list_all, 
    search_collection
)

class Client(ApiConnection):


    def __init__(self, secrets=None, **kwargs):
 
        self._update_headers()
        super(Client, self).__init__(**kwargs)
        self.base = 'https://www.singularity-hub.org/api'

Client.pull = pull
Client.search = search
Client.list = list_all
Client._search_collection = search_collection
