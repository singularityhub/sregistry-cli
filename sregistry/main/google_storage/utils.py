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
from sregistry.utils import ( read_file, get_installdir )
import sys
import os

def prepare_metadata(metadata):
    '''prepare a key/value list of metadata for the request. The metadata
       object that comes in is only parsed one level.
    '''
    pairs = {
        'metadata': {
            'items': [{
                'key': 'client',
                'value': 'sregistry'
            }
           ]
        }
    }
    for key,val in metadata.items():
        if not isinstance(val,dict) and not isinstance(val,list):
            pairs['metadata']['items'].append({'key':key,'value':val})
        elif isinstance(val,dict):            
            for k,v in val.items():
                if not isinstance(v,dict) and not isinstance(v,list):
                    pairs['metadata']['items'].append({'key':k,'value':v})

    return pairs


def get_build_template(name=None, manager='apt'):
    '''get a particular build template, by default we return templates
       that are based on package managers.

       Parameters
       ==========
       name: the full path of the template file to use.
       manager: the package manager to use in the template (yum or apt)

    '''
    base = get_installdir()
    if name is None:
        name = "%s/main/templates/build/singularity-builder-%s.sh" %(base,
                                                                     manager)

    if os.path.exists(name):
        bot.debug("Found template %s" %name)
        return ''.join(read_file(name)) 

    bot.warning("Template %s not found." %name)
