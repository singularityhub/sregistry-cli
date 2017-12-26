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
    check_install, 
    get_image_hash,
    mkdir_p,
    parse_image_name, 
    remove_uri,
    write_json
)
from sregistry.defaults import (
    SREGISTRY_DATABASE
)
from glob import glob
import os
import json
import sys


# COLLECTIONS ##################################################################

def get_or_create_collection(self, name):
    '''get a collection if it exists. If it doesn't exist, create it first.

    Parameters
    ==========
    name: the collection name, usually parsed from get_image_names()['name']

    '''
    from sregistry.database.models import Collection
    collection = self.get_collection(name)

    # If it doesn't exist, create it
    if collection is None:
        collection = Collection(name=name)
        self.session.add(collection)
        self.session.commit()

    return collection


def get_collection(self, name):
    '''get a collection, if it exists, otherwise return None.
    '''
    from sregistry.database.models import Collection
    return Collection.query.filter(Collection.name == name).first()


def get_container(self, name, collection_id, tag="latest", version=None):
    '''get a container, otherwise return None.
    '''
    from sregistry.database.models import Container
    return Container.query.filter(Container.collection_id == collection_id,
                                  Container.name == name,
                                  Container.tag == tag).first()


# ACTIONS ######################################################################

def get(self, name):
    '''Do a get for a container, and then a collection, and then return None
       if no result is found.
    Parameters
    ==========
    name: should coincide with either the collection name, or the container
          name with the collection. A query is done first for the collection,
          and then the container, and the path to the image file returned.
    '''
    from sregistry.database.models import Collection, Container
    names = parse_image_name( remove_uri (name) )
 
    # First look for a collection (required)
    collection = self.get_collection(name=names['collection'])
    container = None

    if collection is None:
        bot.error('Collection %s does not exist.' %names['collection'])
    else:
        container = self.get_container(collection_id=collection.id,
                                       name=names['image'], 
                                       tag=names['tag'])
        if container is not None:
            print(container.image)
    return container


def ls(self, query):
    '''List local images
    '''
    print("write me")


def inspect(self, name):
    '''Inspect a local image in the database, which typically includes the
       basic fields in the model.
    '''
    container = self.get(name)
    if container is not None:
        collection = container.collection.name
        fields = container.__dict__.copy()
        fields['collection'] = collection        
        fields['metrics'] = json.loads(fields['metrics'])
        del fields['_sa_instance_state']
        fields['created_at'] = str(fields['created_at'])
        print(json.dumps(fields, indent=4, sort_keys=True))


def rmi(self, image_name):
    '''Remove an image from the database and filesystem.
    '''
    print("write me")


def rm(self, image_name):
    '''Remove an image from the database, akin to untagging the image. This
    does not delete the file from the cache.
    '''
    print("write me")


def add(self, image_path=None, image_name=None, names=None, url=None, metadata=None, save=True):
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

    if not os.path.exists(image_path):
        bot.error('Cannot find %s' %image_path)
        sys.exit(1)

    if image_name is None:
        bot.error('You must provide an image uri <collection>/<namespace>')
        sys.exit(1)
    names = parse_image_name( remove_uri(image_name) )
    bot.debug('Adding %s to registry' % names['uri'])    

    # If Singularity is installed, inspect image for metadata
    if check_install() is True and metadata is None and image_path is not None:
        from singularity.cli import Singularity
        cli = Singularity()
        metadata = cli.inspect(image_path, quiet=True)

    # Fall back to just include the manifest
    if metadata is None:
        metadata = names

    collection = self.get_or_create_collection(names['collection'])

    # If save, move to registry storage first
    if save is True and image_path is not None:
        storage_folder = os.path.dirname(names['storage'])
        storage_folder = "%s/%s" %(self.storage, storage_folder)
        mkdir_p(storage_folder)
        storage_path = "%s/%s" %(self.storage, names['storage'])
        os.rename(image_path, storage_path)
        image_path = storage_path

    # Get a hash of the file for the version, or use provided
    version = names.get('version')
    if version is None and image_path is not None:
        version = get_image_hash(image_path)

    container = Container(metrics=json.dumps(metadata),
                          name=names['image'],
                          image=image_path,
                          client=self.client_name,
                          tag=names['tag'],
                          version=version,
                          url=url,
                          collection_id=collection.id)


    self.session.add(container)
    collection.containers.append(container)
    self.session.commit()

    bot.info("[container] %s" % names['uri'])
    return container
