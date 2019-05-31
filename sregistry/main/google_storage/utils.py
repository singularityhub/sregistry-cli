'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import ( read_file, get_installdir )
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
