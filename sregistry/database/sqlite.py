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
from sregistry.utils import ( 
    write_json, 
    check_install, 
    parse_image_name, 
    remove_uri 
)
from sregistry.defaults import (
    SREGISTRY_DATABASE
)
from glob import glob
import os
import json
import sys


# SQLITE3 FILE #################################################################


def add(self, image_path, image_name, metadata=None, save=False):
    '''add an image to the database based ona path and name

    Parameters
    ==========
    image_path: full path to image file
    metadata: any extra metadata to keep for the image (dict)
    save: if True, move the image to the cache if it's not there
    '''
    from sregistry.database.models import (
        Container,
        Collection
    )
    names = parse_image_name( remove_uri(image_name) )

    bot.info('Adding %s to registry' % names['uri'])    

    # If Singularity is installed, inspect image for metadata
    if check_install() is True and metadata is None:
        from singularity.cli import Singularity
        cli = Singularity()
        metadata = cli.inspect(image_path)

    # Fall back to just include the manifest
    if metadata is None:
        metadata = names

    # Retrieve collection based on name
    c = Collection.query.filter(Collection.name == names['collection']).first()

    # If save, move to registry storage first
    if save is True:
        print('MOVE FILE HERE')

    container = Container(metrics=metadata,
                          image=image_path,
                          tag=names['tag'],
                          version=names['version'],
                          collection_id=c.id)

    self.session.add(container)
    c.containers.append(container)
    self.session.commit()

    bot.info("Collection: %s" %c)
    bot.info("Container: %s" %container)


def ls(self, session, query):
    '''List local images
    '''
    print("write me")

def rmi(self, session, image_name):
    '''Remove an image from the database and filesystem.
    '''
    print("write me")


def rm(self, session, image_name):
    '''Remove an image from the database, akin to untagging the image.
    '''
    print("write me")

