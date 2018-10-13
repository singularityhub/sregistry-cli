'''

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
import hashlib
import os
import re


def get_image_hash(image_path):
    '''return an md5 hash of the file based on a criteria level. This
    is intended to give the file a reasonable version.
    :param image_path: full path to the singularity image
    '''
    hasher = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()



def parse_image_name(image_name,
                     tag=None,
                     version=None, 
                     defaults=True, 
                     ext="simg",
                     default_collection="library",
                     default_tag="latest",
                     base=None):

    '''return a collection and repo name and tag
    for an image file.
    
    Parameters
    =========
    image_name: a user provided string indicating a collection,
                image, and optionally a tag.
    tag: optionally specify tag as its own argument
         over-rides parsed image tag
    defaults: use defaults "latest" for tag and "library"
              for collection. 
    base: if defined, remove from image_name, appropriate if the
          user gave a registry url base that isn't part of namespace.

    '''
    if base is not None:
        image_name = image_name.replace(base,'').strip('/')

    result = dict()
    image_name = re.sub('[.](img|simg)','',image_name)
    image_name = re.split('/', image_name, 1)

    # User only provided an image
    if len(image_name) == 1:
        collection = ''
        if defaults is True:
            collection = default_collection
        image_name = image_name[0]

    # Collection and image provided
    elif len(image_name) >= 2:
        collection = image_name[0].lower()
        image_name = image_name[1]
    
    # Is there a version?
    image_name = image_name.split('@')
    if len(image_name) > 1: 
        version = image_name[1].lower()
    image_name = image_name[0]

    # Is there a tag?
    image_name = image_name.split(':')

    # No tag in provided string
    if len(image_name) > 1: 
        tag = image_name[1]
    image_name = image_name[0].lower()
    
    # If still no tag, use default or blank
    if tag is None and defaults is True:
        tag = default_tag

    # Piece together the filename
    uri = "%s/%s" % (collection, image_name)    
    url = uri
    if tag is not None:
        uri = "%s-%s" % (uri, tag)
    if version is not None:
        uri = "%s@%s" % (uri, version)

    storage = "%s.%s" %(uri, ext)
    result = {"collection": collection,
              "image": image_name,
              "url": url,
              "tag": tag,
              "version": version,
              "storage": storage,
              "uri": uri}

    return result

def format_container_name(name, special_characters=None):
    '''format_container_name will take a name supplied by the user,
    remove all special characters (except for those defined by "special-characters"
    and return the new image name.
    '''
    if special_characters is None:
        special_characters = []
    return ''.join(e.lower()
                   for e in name if e.isalnum() or e in special_characters)


def get_uri(image):
    '''get the uri for an image, if within acceptable
 
       Parameters
       ==========
       image: the image uri, in the format <uri>://<registry>/<namespace>:<tag>

    '''
    # Ensure we have a string
    image = image or ''

    # Find uri prefix, including ://
    regexp = re.compile('^.+://')
    uri = regexp.match(image)

    if uri is not None:
        uri = (uri.group().lower()
                          .replace('_','-')
                          .replace('://',''))
 
        accepted_uris = ['aws',
                         'docker', 
                         'dropbox',
                         'hub',
                         'globus',
                         'registry', 
                         'nvidia', 
                         'google-storage',
                         'google-drive']

        # Allow for Singularity compatability
        if uri == "shub": uri = "hub"

        if uri not in accepted_uris:
            bot.warning('%s is not a recognized uri.' %uri)
            uri = None

    return uri


def remove_uri(image):
    '''remove_uri will remove the uri from the image path, if provided.
 
       Parameters
       ==========
       image: the image uri, in the format <uri>://<registry>/<namespace>:<tag>

    '''
    return re.sub('^.+://','', image)
