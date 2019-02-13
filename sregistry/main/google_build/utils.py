'''

Copyright (C) 2017-2019 Vanessa Sochat.

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
from sregistry.utils import ( read_json, get_installdir )
import sys
import os


def get_build_template():
    '''get default build template.
    '''
    base = get_installdir()
    name = "%s/main/templates/build/singularity-cloudbuild.json" % base

    if os.path.exists(name):
        bot.debug("Found template %s" %name)
        return read_json(name)

    bot.warning("Template %s not found." % name)
