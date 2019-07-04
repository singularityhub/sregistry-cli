'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

__version__ = "0.2.27"
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
    ('spython', {'min_version': '0.0.63'}),
    ('requests', {'min_version': '2.18.4'}),
    ('pygments', {'min_version': '2.1.3'}),
)

TESTS_REQUIRES = (
    ('pytest', {'min_version': '4.6.2'}),
)

################################################################################
# Submodule Requirements (no database, just client)


INSTALL_BASIC_REGISTRY = (
    ('requests-toolbelt', {'min_version': '0.8.0'}),
    ('python-dateutil', {'min_verison': "2.5.3"})
)

INSTALL_BASIC_AWS = (
    ('awscli', {'min_version': '1.16.19'}),
)

INSTALL_BASIC_SWIFT = (
    ('python-swiftclient', {'min_version': '3.6.0'}),
    ('python-keystoneclient', {'min_version': '3.5.0'}),
    ('oauth2client', {'min_version': '3.0'}),
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

INSTALL_BASIC_GOOGLE_BUILD = (
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

INSTALL_BASIC_S3 = (
    ('boto3', {'min_version': '1.7.83'}),
)

INSTALL_BASIC_ALL = (INSTALL_REQUIRES +
                     INSTALL_BASIC_S3 +
                     INSTALL_BASIC_AWS +
                     INSTALL_BASIC_SWIFT +
                     INSTALL_BASIC_DROPBOX +
                     INSTALL_BASIC_GLOBUS +
                     INSTALL_BASIC_REGISTRY +
                     INSTALL_BASIC_GOOGLE_STORAGE +
                     INSTALL_BASIC_GOOGLE_BUILD +
                     INSTALL_BASIC_GOOGLE_COMPUTE +
                     INSTALL_BASIC_GOOGLE_DRIVE)

################################################################################
# Submodule Requirements (versions that include database)


INSTALL_REQUIRES_REGISTRY = (
    ('requests-toolbelt', {'min_version': '0.8.0'}),
    ('python-dateutil', {'min_verison': "2.5.3"}),
    ('sqlalchemy', {'min_version': None})
)

INSTALL_REQUIRES_AWS = (
    ('awscli', {'min_version': '1.16.19'}),
    ('sqlalchemy', {'min_version': None})
)

INSTALL_REQUIRES_SWIFT = (
    ('python-swiftclient', {'min_version': '3.6.0'}),
    ('sqlalchemy', {'min_version': None}),
    ('oauth2client', {'min_version': '3.0'}),
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

INSTALL_REQUIRES_GOOGLE_BUILD = (
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

INSTALL_REQUIRES_S3 = (
    ('sqlalchemy', {'min_version': None}),
    ('boto3', {'min_version': '1.7.83'}),
)

INSTALL_REQUIRES_ALL = (INSTALL_REQUIRES +
                        INSTALL_REQUIRES_AWS +
                        INSTALL_REQUIRES_S3 +
                        INSTALL_REQUIRES_SWIFT +
                        INSTALL_REQUIRES_DROPBOX +
                        INSTALL_REQUIRES_REGISTRY +
                        INSTALL_REQUIRES_GOOGLE_COMPUTE +
                        INSTALL_REQUIRES_GOOGLE_STORAGE +
                        INSTALL_REQUIRES_GOOGLE_BUILD +
                        INSTALL_REQUIRES_GOOGLE_DRIVE)
