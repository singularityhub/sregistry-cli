'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot

def get_template(name):
    '''return a default template for some function in sregistry
       If there is no template, None is returned.

       Parameters
       ==========
       name: the name of the template to retrieve

    '''
    name = name.lower()
    templates = dict()

    templates['tarinfo'] = {"gid": 0,
                            "uid": 0,
                            "uname": "root",
                            "gname": "root",
                            "mode": 493}

    if name in templates:
        bot.debug("Found template for %s" % (name))
        return templates[name]
    else:
        bot.warning("Cannot find template %s" % (name))
