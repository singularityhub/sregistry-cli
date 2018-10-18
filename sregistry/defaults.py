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
from sregistry.utils import ( get_userhome, read_json )
import tempfile
import os
import sys

################################################################################
# environment / options
################################################################################

def convert2boolean(arg):
    '''convert2boolean is used for environmental variables
       that must be returned as boolean

       Parameters
       ==========
       arg: the argument to convert to boolean. Must be a string given
       grabbed from environment.
    '''
    if not isinstance(arg, bool):
        return arg.lower() in ("yes", "true", "t", "1", "y")
    return arg


def getenv(variable_key, default=None, required=False, silent=True):
    '''getenv will attempt to get an environment variable. If the variable
       is not found, None is returned.
 
       Parameters
       ==========   
       variable_key: the variable name
       required: exit with error if not found
        silent: Do not print debugging information for variable
    '''
    variable = os.environ.get(variable_key, default)
    if variable is None and required:
        bot.error("Cannot find environment variable %s, exiting." %variable_key)
        sys.exit(1)

    if not silent and variable is not None:
            bot.verbose("%s found as %s" %(variable_key,variable))

    return variable


################################################################################
# SRegistry


#########################
# Global Settings
#########################

USERHOME = get_userhome()
DISABLE_CACHE = convert2boolean(getenv("SINGULARITY_DISABLE_CACHE", False))
DISABLE_DATABASE = convert2boolean(getenv("SREGISTRY_DISABLE", False))
DISABLE_SSL_CHECK = convert2boolean(getenv("SREGISTRY_HTTPS_NOVERIFY", False))

_secrets = os.path.join(USERHOME, ".sregistry")
SREGISTRY_CLIENT_SECRETS = getenv('SREGISTRY_CLIENT_SECRETS', _secrets)

# If the client secrets exist, use the default as first priority
_client = 'hub'
if os.path.exists(SREGISTRY_CLIENT_SECRETS):
    secrets = read_json(SREGISTRY_CLIENT_SECRETS)   
    _client = secrets.get('SREGISTRY_CLIENT', 'hub')
SREGISTRY_CLIENT = getenv("SREGISTRY_CLIENT", _client)


#########################
# Fun Settings
#########################

# None defaults to robot. Path must exist, and ensure image < 2MB and min 220px
SREGISTRY_THUMBNAIL = getenv('SREGISTRY_THUMBNAIL')


#########################
# Multiprocessing
#########################

SREGISTRY_WORKERS = int(getenv("SREGISTRY_PYTHON_THREADS", 9))

#########################
# Database and Storage
#########################

# Database folder, inside where we put storage and credentials folder
_database = os.path.join(USERHOME, ".singularity")
SREGISTRY_DATABASE = None
SREGISTRY_STORAGE = None
SREGISTRY_BASE = None

# If sqlalchemy isn't installed, user doesn't have support for database
try:
    from sqlalchemy import or_
except ImportError:
    bot.warning('Database disabled. Install sqlalchemy for full functionality')
    DISABLE_DATABASE = True


# If the user didn't disable caching or the database
if not DISABLE_CACHE and DISABLE_DATABASE is False:

    # First priority goes to database path set in environment,
    # and if it's not set, default to home folder
    SREGISTRY_BASE = getenv("SREGISTRY_DATABASE", _database)

    # Storage defaults to a subfolder of the database, shub
    _storage = os.path.join(_database, "shub")
    SREGISTRY_STORAGE = getenv("SREGISTRY_STORAGE", _storage)
    SREGISTRY_DATABASE = "%s/sregistry.db" % SREGISTRY_BASE


#########################
# Caches
#########################

# Credentials and client secrets
DISABLE_CREDENTIAL_CACHE = getenv('SREGISTRY_DISABLE_CREDENTIAL_CACHE', False)
DISABLE_CREDENTIAL_CACHE = convert2boolean(DISABLE_CREDENTIAL_CACHE)
CREDENTIAL_CACHE = None

# Download Cache for Singularity layers (not complete images)
_cache = os.path.join(USERHOME, ".singularity")
SINGULARITY_CACHE = getenv("SINGULARITY_CACHEDIR", default=_cache)

#########################
# Temporary Storage
#########################

SREGISTRY_TMPDIR = os.environ.get('SREGISTRY_TMPDIR', tempfile.gettempdir())

# We only use the credential cache if user didn't disable it
# and if the entire sregistry database isn't disabled for use.
if not DISABLE_CREDENTIAL_CACHE and SREGISTRY_DATABASE is not None:
    _credentials = os.environ.get('SREGISTRY_CREDENTIALS_CACHE', _database)
    CREDENTIAL_CACHE = '%s/.sregistry' %_credentials
