'''

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

from sregistry.logger import bot
from sregistry.main import ApiConnection
import json
import sys
import os

from .pull import pull
from .query import (
    ls, search, collection_search
)

base = 'https://www.singularity-hub.org/api'

class Client(ApiConnection):

    def __init__(self, **kwargs):
 
        super(ApiConnection, self).__init__()
        if "base" in kwargs:
            self.base = kwargs['base']

    def __str__(self):
        return "hub.client.%s" %(self.base)
    
Client.pull = pull
Client.search = search
Client.collection_search = collection_search
Client.ls = ls
