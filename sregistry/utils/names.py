'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
import re


# Regular expressions to parse registry, collection, repo, tag and version
_docker_uri = re.compile(
    "(?:(?P<registry>[^/@]+[.:][^/@]*)/)?"
    "(?P<collection>(?:[^:@/]+/)+)?"
    "(?P<repo>[^:@/]+)"
    "(?::(?P<tag>[^:@]+))?"
    "(?:@(?P<version>.+))?"
    "$")

# Reduced to match registry:port/repo or registry.com/repo
_reduced_uri = re.compile(
    "(?:(?P<registry>[^/@]+[.:][^/@]*)/)?"
    "(?P<repo>[^:@/]+)"
    "(?::(?P<tag>[^:@]+))?"
    "(?:@(?P<version>.+))?"
    "$"
    "(?P<collection>.)?")

# Default
_default_uri = re.compile(
    "(?:(?P<registry>[^/@]+)/)?"
    "(?P<collection>(?:[^:@/]+/)+)"
    "(?P<repo>[^:@/]+)"
    "(?::(?P<tag>[^:@]+))?"
    "(?:@(?P<version>.+))?"
    "$")


def set_default(item, default, use_default):
    '''if an item provided is None and boolean use_default is set to True,
       return the default. Otherwise, return the item.
    '''
    if item is None and use_default:
        return default
    return item


def parse_image_name(image_name,
                     tag=None,
                     version=None, 
                     defaults=True, 
                     ext="sif",
                     default_collection="library",
                     default_tag="latest",
                     base=None,
                     lowercase=True):

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
    lowercase: turn entire URI to lowercase (default is True)
    '''

    # Save the original string
    original = image_name
    
    if base is not None:
        image_name = image_name.replace(base,'').strip('/')

    # If a file is provided, remove extension
    image_name = re.sub('[.](img|simg|sif)','', image_name)

    # Parse the provided name
    uri_regexes = [ _reduced_uri,
                    _default_uri,
                    _docker_uri ]

    for r in uri_regexes:
        match = r.match(image_name)
        if match:
            break

    if not match:
        bot.exit('Could not parse image "%s"! Exiting.' % image_name)

    # Get matches
    registry = match.group('registry')
    collection = match.group('collection')
    repo_name = match.group('repo')
    repo_tag = tag or match.group('tag')
    version = version or match.group('version')
    
    # A repo_name is required
    assert repo_name

    # If a collection isn't provided
    collection = set_default(collection, default_collection, defaults)
    repo_tag = set_default(repo_tag, default_tag, defaults)

    # The collection, name must be all lowercase
    if lowercase:
        collection = collection.lower().rstrip('/')
        repo_name = repo_name.lower()
        repo_tag = repo_tag.lower()
    else:
        collection = collection.rstrip('/')

    if version is not None:
        version = version.lower()
    
    # Piece together the uri base
    if registry is None:
        uri = "%s/%s" % (collection, repo_name)    
    else:
        uri = "%s/%s/%s" % (registry, collection, repo_name)    

    url = uri

    # Tag is defined
    if repo_tag is not None:
        uri = "%s:%s" % (url, repo_tag) 

    # Version is defined
    storage_version = None
    if version is not None:
        uri = "%s@%s" % (uri, version)
        storage_version = "%s.%s" % (uri, ext)

    # A second storage URI honors the tag (:) separator

    storage = "%s.%s" %(uri, ext)
    result = {"collection": collection,
              "original": original,
              "registry": registry,
              "image": repo_name,
              "url": url,
              "tag": repo_tag,
              "version": version,
              "storage": storage_version or storage,
              "uri": uri}

    return result

def get_uri(image, validate=True):
    '''get the uri for an image, if within acceptable
 
       Parameters
       ==========
       image: the image uri, in the format <uri>://<registry>/<namespace>:<tag>
       validate: if True, check if uri is in list of supported (default True)

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
                         'http', 'https', # Must be allowed for pull
                         'dropbox',
                         'gitlab',
                         'globus',
                         'google-build',
                         'google-storage',
                         'google-drive',
                         'hub',
                         'nvidia', 
                         'registry',
                         's3', 
                         'swift']

        # Allow for Singularity compatability
        if "shub" in uri: uri = "hub"

        if validate is True and uri not in accepted_uris:
            bot.warning('%s is not a recognized uri.' % uri)
            uri = None

    return uri


def remove_uri(image):
    '''remove_uri will remove the uri from the image path, if provided.
 
       Parameters
       ==========
       image: the image uri, in the format <uri>://<registry>/<namespace>:<tag>

    '''
    return re.sub('^.+://','', image)


def get_recipe_tag(path):
    '''get a recipe tag (the extension of a Singularity file). The extension
       determines the tag. If no extension is found, latest is used.

       Parameters
       ==========
       path: the path to the recipe file (e.g. /opt/Singularity.tag)

    '''
    tag = None
    if re.search("Singularity", path):
        tag = re.sub('(.+)?Singularity[.]?','', path)
        if tag in ['', None]:
            tag = 'latest'
    return tag
