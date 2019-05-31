'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import (read_json, get_installdir)
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
