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

__version__ = "0.01.00"
AUTHOR = 'Vanessa Sochat'
AUTHOR_EMAIL = 'vsochat@stanford.edu'
NAME = 'sregistry'
PACKAGE_URL = "http://www.github.com/singularityhub/sregistry-cli"
KEYWORDS = 'singularity containers registry hub'
DESCRIPTION = "Command line tool for working with container storage"
LICENSE = "LICENSE"

################################################################################
# Global requirements


INSTALL_REQUIRES = (
    ('spython', {'min_version': '0.0.34'}),
    ('requests', {'min_version': '2.18.4'}),
    ('pygments', {'min_version': '2.1.3'}),
)

################################################################################
# Submodule Requirements (no database, just client)


INSTALL_BASIC_REGISTRY = (
    ('requests-toolbelt', {'min_version': '0.8.0'}),
    ('dateutils', {'min_version': "0.6.6"}),
    ('python-dateutil', {'min_verison': "2.5.3"})
)

INSTALL_BASIC_AWS = (
    ('awscli', {'min_version': '1.16.19'}),
)

INSTALL_BASIC_DROPBOX = (
    ('dropbox', {'min_version': '8.5.1'}),
)

INSTALL_BASIC_GLOBUS = (
    ('oauth2client', {'min_version': '3.0'}),
    ('globus_sdk[jwt]', {'min_version': '1.5.0'})
)

INSTALL_BASIC_GOOGLE_STORAGE = (
    ('oauth2client', {'min_version': '3.0'}),
    ('google-cloud-storage', {'min_version': '1.4.0'}),
    ('retrying', {'min_version': '1.3.3'})
)

INSTALL_BASIC_GOOGLE_DRIVE = (
    ('oauth2client', {'min_version': '3.0'}),
    ('google-api-python-client', {'min_version': '1.6.4'})
)

INSTALL_BASIC_GOOGLE_COMPUTE = (
    ('oauth2client', {'min_version': '3.0'}),
    ('google-api-python-client', {'min_version': '1.6.4'}),
    ('google-cloud-storage', {'min_version': '1.4.0'})
)

INSTALL_BASIC_ALL = (INSTALL_REQUIRES +
                     INSTALL_BASIC_AWS +
                     INSTALL_BASIC_DROPBOX +
                     INSTALL_BASIC_GLOBUS +
                     INSTALL_BASIC_REGISTRY +
                     INSTALL_BASIC_GOOGLE_STORAGE +
                     INSTALL_BASIC_GOOGLE_COMPUTE +
                     INSTALL_BASIC_GOOGLE_DRIVE)

################################################################################
# Submodule Requirements (versions that include database)


INSTALL_REQUIRES_REGISTRY = (
    ('requests-toolbelt', {'min_version': '0.8.0'}),
    ('dateutils', {'min_version': "0.6.6"}),
    ('python-dateutil', {'min_verison': "2.5.3"}),
    ('sqlalchemy', {'min_version': None})
)

INSTALL_REQUIRES_AWS = (
    ('awscli', {'min_version': '1.16.19'}),
    ('sqlalchemy', {'min_version': None})
)

INSTALL_REQUIRES_DROPBOX = (
    ('dropbox', {'min_version': '8.5.1'}),
    ('sqlalchemy', {'min_version': None})
)

INSTALL_REQUIRES_GLOBUS = (
    ('oauth2client', {'min_version': '3.0'}),
    ('globus_sdk[jwt]', {'min_version': '1.5.0'}),
    ('sqlalchemy', {'min_version': None}),
)

INSTALL_REQUIRES_GOOGLE_STORAGE = (
    ('oauth2client', {'min_version': '3.0'}),
    ('google-cloud-storage', {'min_version': '1.4.0'}),
    ('retrying', {'exact_version': '1.3.3'}),
    ('sqlalchemy', {'min_version': None})
)

INSTALL_REQUIRES_GOOGLE_DRIVE = (
    ('oauth2client', {'min_version': '3.0'}),
    ('sqlalchemy', {'min_version': None}),
    ('google-api-python-client', {'min_version': '1.6.4'})
)

INSTALL_REQUIRES_GOOGLE_COMPUTE = (
    ('oauth2client', {'min_version': '3.0'}),
    ('sqlalchemy', {'min_version': None}),
    ('google-api-python-client', {'min_version': '1.6.4'}),
    ('google-cloud-storage', {'min_version': '1.4.0'})
)

INSTALL_REQUIRES_ALL = (INSTALL_REQUIRES +
                        INSTALL_REQUIRES_AWS +
                        INSTALL_REQUIRES_DROPBOX +
                        INSTALL_REQUIRES_REGISTRY +
                        INSTALL_REQUIRES_GOOGLE_COMPUTE +
                        INSTALL_REQUIRES_GOOGLE_STORAGE +
                        INSTALL_REQUIRES_GOOGLE_DRIVE)
