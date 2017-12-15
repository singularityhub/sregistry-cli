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
from dateutil import parser
import os
import re


def print_date(date, format='%b %d, %Y %I:%M%p'):
    datetime_object = parser.parse(date)
    return datetime_object.strftime(format)


def get_image_name(manifest, extension='simg', use_commit=False, use_hash=False):
    '''get_image_name will return the image name for a manifest. The user
       can name based on a hash or commit, or a name with the collection,
       namespace, branch, and tag.
    '''
    if use_hash:
        image_name = "%s.%s" %(manifest['version'], extension)

    elif use_commit:
        image_name = "%s.%s" %(manifest['commit'], extension)

    else:
        image_name = "%s-%s-%s.%s" %(manifest['name'].replace('/','-'),
                                     manifest['branch'].replace('/','-'),
                                     manifest['tag'].replace('/',''),
                                     extension)
            
    bot.info("Singularity Registry Image: %s" %image_name)
    return image_name




def parse_image_name(image_name, tag=None, defaults=True, ext="img"):
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
    '''
    result = dict()
    image_name = image_name.replace('.img', '').lower()
    image_name = re.split('/', image_name, 1)

    # User only provided an image
    if len(image_name) == 1:
        collection = ''
        if defaults is True:
            collection = "library"
        image_name = image_name[0]

    # Collection and image provided
    elif len(image_name) >= 2:
        collection = image_name[0]
        image_name = image_name[1]
    
    # Is there a tag?
    image_name = image_name.split(':')

    # No tag in provided string
    if len(image_name) > 1: 
        tag = image_name[1]
    image_name = image_name[0]
    
    # If still no tag, use default or blank
    if tag is None and defaults is True:
        tag = "latest"
    
    if tag is not None:
        uri = "%s/%s:%s" % (collection, image_name, tag)
        storage = "%s/%s-%s.%s" % (collection, image_name, tag, ext)
    else:
        uri = "%s/%s" % (collection, image_name)
        storage = "%s/%s.%s" % (collection, image_name, ext)

    result = {"collection": collection,
              "image": image_name,
              "tag": tag,
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


def remove_uri(container):
    '''remove_uri will remove docker:// or shub:// from the uri
    '''
    return container.replace('docker://', '').replace('shub://', '')
