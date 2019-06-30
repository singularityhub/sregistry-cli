'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import ( 
    copyfile,
    get_file_hash,
    parse_image_name, 
    remove_uri
)
from sqlalchemy import or_
import os
import json
import shutil


# COLLECTIONS ##################################################################

def get_or_create_collection(self, name):
    '''get a collection if it exists. If it doesn't exist, create it first.

       Parameters
       ==========
       name: the collection name parsed from parse_image_names()['collection']
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
    return Collection.query.filter(Collection.name==name).first()


def get_container(self, name,
                        collection_id,
                        tag="latest",
                        version=None):

    '''get a container, otherwise return None.
    '''
    from sregistry.database.models import Container
    if not version:
        container = Container.query.filter_by(collection_id=collection_id,
                                              name=name,
                                              tag=tag).first()
    else:
        container = Container.query.filter_by(collection_id=collection_id,
                                              name=name,
                                              tag=tag,
                                              version=version).first()
    return container


# ACTIONS ######################################################################

def get(self, name, quiet=False):
    '''Do a get for a container, and then a collection, and then return None
       if no result is found.
    Parameters
    ==========
    name: should coincide with either the collection name, or the container
          name with the collection. A query is done first for the collection,
          and then the container, and the path to the image file returned.
    '''
    names = parse_image_name(remove_uri(name))
 
    # First look for a collection (required)
    collection = self.get_collection(name=names['collection'])
    container = None

    if collection:
        container = self.get_container(collection_id=collection.id,
                                       name=names['image'], 
                                       tag=names['tag'],
                                       version=names['version'])

        if container and not quiet:

            # The container image file exists [local]
            if container.image:
                print(container.image)

            # The container has a url (but not local file)
            elif container.url:
                print(container.url)
            else:
                bot.info('No storage file found for %s' % name)

    return container


def images(self, query=None):
    '''List local images in the database, optionally with a query.

       Paramters
       =========
       query: a string to search for in the container or collection name|tag|uri
    '''
    from sregistry.database.models import Container

    rows = []
    if query is not None:   
        like = "%" + query + "%"
        containers = Container.query.filter(or_(Container.name == query,
                                                Container.tag.like(like),
                                                Container.uri.like(like),
                                                Container.name.like(like))).all() 
    else:
        containers = Container.query.all()

    if len(containers) > 0:
        message = "  [date]   [client]\t[uri]"
        bot.custom(prefix='Containers:', message=message, color="RED")
        for c in containers:
            uri = c.get_uri()
            created_at = c.created_at.strftime('%B %d, %Y')
            rows.append([created_at, "   [%s]" %c.client, uri])
        bot.table(rows) 
    return containers


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
        return fields
    bot.exit("image {} was not found in the database".format(name))


def rename(self, image_name, path):
    '''rename performs a move, but ensures the path is maintained in storage

       Parameters
       ==========
       image_name: the image name (uri) to rename to.
       path: the name to rename (basename is taken)
    '''
    container = self.get(image_name, quiet=True)

    if container:
        if container.image:

            # Derive a new filename and url in storage
            names = parse_image_name(remove_uri(path), version=container.version)
            storage = self._get_storage_name(names)
            dirname = os.path.dirname(storage)

            # This is the collection folder
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            container = self.cp(move_to=storage,
                                container=container,
                                command="rename")

            # On successful rename of file, update the uri
            if container is not None:

                # Create the collection if doesn't exist
                collection = self.get_or_create_collection(names['collection'])
                self.session.commit()
 
                # Then update the container
                container = update_container_metadata(container, collection, names)
                self.session.commit()
                return container

    bot.warning('%s not found' % image_name)


def update_container_metadata(container, collection, names):
    '''update container metadata, done for a move or rename. The session
       is not saved, and needs to be done so by the calling function.

       Parameters
       ==========
       container: the container object to update with names
       collection: the collection to move it to (might be the same)
       names: the result of parse_image_names
    '''
    # Update all metadata for the container
    container.uri=names['uri']
    container.name=names['image']
    container.tag=names['tag']
    container.collection_id=collection.id
    return container


def mv(self, image_name, path):
    '''Move an image from it's current location to a new path.
       Removing the image from organized storage is not the recommended approach
       however is still a function wanted by some.

       Parameters
       ==========
       image_name: the parsed image name.
       path: the location to move the image to
    '''
    container = self.get(image_name, quiet=True)

    if container is not None:

        image = container.image or ''

        # Only continue if image file exists
        if os.path.exists(image):

            # Default assume directory, use image name and path fully
            filename = os.path.basename(image)
            filedir = os.path.abspath(path)

            # If it's a file, use filename provided
            if not os.path.isdir(path):
                filename = os.path.basename(path)
                filedir = os.path.dirname(path)
        
            # If directory is empty, assume $PWD
            if filedir == '':
                filedir = os.getcwd()
       
            # Copy to the fullpath from the storage
            fullpath = os.path.abspath(os.path.join(filedir, filename))
            return self.cp(move_to=fullpath, 
                           container=container,
                           command="move")
    
    bot.warning('%s not found' % image_name)


def cp(self, move_to, image_name=None, container=None, command="copy"):
    '''_cp is the shared function between mv (move) and rename, and performs
       the move, and returns the updated container
    
       Parameters
       ==========
       image_name: an image_uri to look up a container in the database
       container: the container object to move (must have a container.image
       move_to: the full path to move it to
    '''
    if not container and not image_name:
        bot.exit('A container or image_name must be provided to %s' % command)

    # If a container isn't provided, look for it from image_uri
    if not container:
        container = self.get(image_name, quiet=True)

    image = container.image or ''

    if os.path.exists(image):

        filedir = os.path.dirname(move_to)

        # If the two are the same, doesn't make sense
        if move_to == image:
            bot.exit('%s is already the name.' % image)
       
        # Ensure directory exists
        if not os.path.exists(filedir):
            bot.exit('%s does not exist. Ensure exists first.' % filedir)

        # Ensure writable for user
        if not os.access(filedir, os.W_OK):
            bot.exit('%s is not writable' % filedir)

        original = os.path.basename(image)

        try:
            shutil.move(image, move_to)
            container.image = move_to
            self.session.commit()
            bot.info('[%s] %s => %s' %(command, original, move_to))
            return container
        except:
            bot.exit('Cannot %s %s to %s' %(command, original, move_to))

    bot.warning('''Not found! Please pull %s and then %s to the appropriate
                   location.''' %(container.uri, command))

    
def rm(self, image_name):
    '''Delete an image record and file from the database.
    '''
    container = self.get(image_name)
    if container is not None:
        name = container.uri or container.get_uri()
        image = container.image
        self.session.delete(container)
        self.session.commit()
        if image is not None:
            if os.path.exists(image):
                os.remove(image)
            else:
                bot.warning("image file {} does not exist on the file system!".format(image))
                return None
            return image
        bot.info("[rm] %s" % name)


def add(self, image_path=None,
              image_uri=None,
              image_name=None,
              url=None,
              metadata=None,
              save=True, 
              copy=False):

    '''get or create a container, including the collection to add it to.
       This function can be used from a file on the local system, or via a URL
       that has been downloaded. Either way, if one of url, version, or image_file
       is not provided, the model is created without it. If a version is not
       provided but a file path is, then the file hash is used.

       Parameters
       ==========
       image_path: full path to image file
       image_name: if defined, the user wants a custom name (and not based on uri)
       metadata: any extra metadata to keep for the image (dict)
       save: if True, move the image to the cache if it's not there
       copy: If True, copy the image instead of moving it.

       image_name: a uri that gets parsed into a names object that looks like:

       {'collection': 'vsoch',
        'image': 'hello-world',
        'storage': 'vsoch/hello-world-latest.img',
        'tag': 'latest',
        'version': '12345'
        'uri': 'vsoch/hello-world:latest@12345'}

       After running add, the user will take some image in a working
       directory, add it to the database, and have it available for search
       and use under SREGISTRY_STORAGE/<collection>/<container>

       If the container was retrieved from a webby place, it should have version
       If no version is found, the file hash is used.
    '''

    from sregistry.database.models import Container

    # We can only save if the image is provided
    if image_path is not None:
        if not os.path.exists(image_path) and save is True:
            bot.exit('Cannot find %s' % image_path)

    # An image uri is required for version, tag, etc.
    if image_uri is None:
        bot.exit('You must provide an image uri --name <collection>/<namespace>')

    names = parse_image_name(remove_uri(image_uri))
    bot.debug('Adding %s to registry' % names['uri'])    

    # If Singularity is installed, inspect image for metadata
    metadata = self.get_metadata(image_path, names=names)
    collection = self.get_or_create_collection(names['collection'])

    # Get a hash of the file for the version, or use provided
    version = names.get('version')
    if not version:
        if image_path:
            version = get_file_hash(image_path, "sha256")
        else:
            version = ''  # we can't determine a version, not in API/no file
        names = parse_image_name(remove_uri(image_uri), version=version)

    # If save, move to registry storage first
    if save and image_path:

        # If the user hasn't defined a custom name
        if image_name is None:      
            image_name = self._get_storage_name(names)
        if copy:
            copyfile(image_path, image_name)
        else:
            shutil.move(image_path, image_name)
        image_path = image_name

    # Just in case the client didn't provide it, see if we have in metadata
    if url is None and "url" in metadata:
        url = metadata['url']

    # First check that we don't have one already!
    container = self.get_container(name=names['image'],
                                   collection_id=collection.id, 
                                   tag=names['tag'],
                                   version=version)

    # The container did not exist, create it
    if not container:
        action = "new"
        container = Container(metrics=json.dumps(metadata),
                              name=names['image'],
                              image=image_path,
                              client=self.client_name,
                              tag=names['tag'],
                              version=version,
                              url=url,
                              uri=names['uri'],
                              collection_id=collection.id)

        self.session.add(container)
        collection.containers.append(container)

    # The container existed, update it.
    else:
        action="update"
        metrics=json.loads(container.metrics)
        metrics.update(metadata)
        container.url = url
        container.client = self.client_name
        if image_path is not None:
            container.image=image_path
        container.metrics=json.dumps(metrics)

    self.session.commit()
    bot.info("[container][%s] %s" % (action, names['uri']))
    return container
