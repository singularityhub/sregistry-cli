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
import tempfile
import os
import pwd
import sys

################################################################################
# environment / options
################################################################################

def convert2boolean(arg):
    '''
    convert2boolean is used for environmental variables
    that must be returned as boolean
    '''
    if not isinstance(arg, bool):
        return arg.lower() in ("yes", "true", "t", "1", "y")
    return arg


def getenv(variable_key, default=None, required=False, silent=True):
    '''
    getenv will attempt to get an environment variable. If the variable
    is not found, None is returned.

    :param variable_key: the variable name
    :param required: exit with error if not found
    :param silent: Do not print debugging information for variable
    '''
    variable = os.environ.get(variable_key, default)
    if variable is None and required:
        bot.error("Cannot find environment variable %s, exiting." %variable_key)
        sys.exit(1)

    if not silent and variable is not None:
            bot.verbose("%s found as %s" %(variable_key,variable))

    return variable


#######################################################################
# SRegistry
#######################################################################

USERHOME = pwd.getpwuid(os.getuid())[5]
DISABLE_CACHE = convert2boolean(getenv("SINGULARITY_DISABLE_CACHE", False))
DISABLE_DATABASE = convert2boolean(getenv("SREGISTRY_DISABLE", False))

# If the user isn't caching images, don't save
if DISABLE_CACHE is True or DISABLE_DATABASE is True:
    SREGISTRY_DATABASE = None

# If the user is caching...
else:
    # First priority goes to database path set in environment,
    # and if it's not set, default to home folder
    _database = os.path.join(USERHOME, ".singularity")
    SREGISTRY_DATABASE = getenv("SREGISTRY_DATABASE", _database)
    SREGISTRY_DATABASE = "%s/sregistry.db" %SREGISTRY_DATABASE

_secrets = os.path.join(USERHOME, ".sregistry")
SREGISTRY_CLIENT_SECRETS = getenv('SREGISTRY_CLIENT_SECRETS', _secrets)
