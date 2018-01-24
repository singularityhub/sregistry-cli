'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
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

