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

from sregistry.utils import ( mkdir_p, get_image_hash )
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

def ls(self, query):
    '''List local images
    '''
    print("write me")

def rmi(self, image_name):
    '''Remove an image from the database and filesystem.
    '''
    print("write me")


def rm(self, image_name):
    '''Remove an image from the database, akin to untagging the image. This
    does not delete the file from the cache.
    '''
    print("write me")


def add(self, image_path=None, names=None, url=None, metadata=None, save=True):
    '''get or create a container, including the collection to add it to.
    This function can be used from a file on the local system, or via a URL
    that has been downloaded. Either way, if one of url, version, or image_file
    is not provided, the model is created without it. If a version is not
    provided but a file path is, then the file hash is used.

    Parameters
    ==========
    image_path: full path to image file
    metadata: any extra metadata to keep for the image (dict)
    save: if True, move the image to the cache if it's not there
    names: a dictionary with extracted names for the container and collection
    {'collection': 'vsoch',
     'image': 'hello-world',
     'storage': 'vsoch/hello-world-latest.img',
     'tag': 'latest',
     'uri': 'vsoch/hello-world:latest'}

    After running add, the user will take some image in a working
    directory, add it to the database, and have it available for search
    and use under SREGISTRY_STORAGE/<collection>/<container>

    If the container was retrieved from a webby place, it should have version
    If no version is found, the file hash is used.
    '''

    from sregistry.database.models import (
        Container,
        Collection
    )

    if names is None:
        names = parse_image_name( remove_uri(image_name) )

    bot.info('Adding %s to registry' % names['uri'])    

    # If Singularity is installed, inspect image for metadata
    if check_install() is True and metadata is None:
        from singularity.cli import Singularity
        cli = Singularity()
        metadata = cli.inspect(image_path, quiet=True)

    # Fall back to just include the manifest
    if metadata is None:
        metadata = names

    # Retrieve collection based on name
    c = Collection.query.filter(Collection.name == names['collection']).first()

    # If it doesn't exist, create it
    if c is None:
        c = Collection(name=names['collection'])

    # If save, move to registry storage first
    if save is True:
        storage_folder = os.path.dirname(names['storage'])
        storage_folder = "%s/%s" %(self.storage, storage_folder)
        mkdir_p(storage_folder)
        storage_path = "%s/%s" %(self.storage, names['storage'])
        os.rename(image_path, storage_path)
        image_path = storage_path

    # Get a hash of the file for the version, or use provided
    version = names.get('version')
    if version is None:
        version = get_image_hash(image_path)

    container = Container(metrics=metadata,
                          name=names['image'],
                          image=image_path,
                          client=self.client_name,
                          tag=names['tag'],
                          version=version,
                          url=url,
                          collection_id=c.id)


    self.session.add(container)
    c.containers.append(container)
    self.session.commit()

    bot.info("Collection: %s" %c)
    bot.info("Container: %s" %container)
    return container
