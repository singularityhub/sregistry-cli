'''

Copyright (C) 2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2018 Vanessa Sochat.

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

from sregistry.logger import bot, ProgressBar
from sregistry.utils import (
    get_image_hash,
    get_installdir,
    get_recipe_tag,
    parse_image_name,
    remove_uri
)

from sregistry.main.google_storage.utils import get_build_template

from retrying import retry
import json
import sys
import os

    

def build(self, repo, 
                config=None,
                name=None, 
                recipe='Singularity',
                preview=False):

    '''trigger a build on Google Cloud (storage then compute) given a name
       recipe, and Github URI where the recipe can be found.
    
       Parameters
       ==========
       name: should be the complete uri that the user has requested to push.
       repo: should correspond to a Github URL or (if undefined) used local repo.
       config: The local config file to use. If the file doesn't exist, then
               we attempt looking up the config based on the name.
       recipe: If defined, limit builder to build a single recipe

    '''

    bot.debug("BUILD %s" % repo)

    # Ensure that repo exists (200 response)
    if not self._healthy(repo):
        sys.exit(1)

    config = self._load_build_config(config)

    # If name not provided, parse name based on repository
    if name is None:
        name = '/'.join(repo.split('/')[-2:])

    # This returns a data structure with collection, container, based on uri
    names = parse_image_name(remove_uri(name))

    # If the user hasn't provided a tag with the name, check recipe
    if names['tag'] == "latest" and recipe != "Singularity":
        tag = get_recipe_tag(recipe)
        names = parse_image_name(remove_uri(name), tag=tag)

    # Setup the build
    config = self.setup_build(names['url'], config)

    # Add the chosen recipe as metadata
    bot.info('Adding recipe %s to config %s' %recipe)
    entry = {'key': 'SINGULARITY_RECIPE', 'value': recipe}
    config['metadata']['items'].append(entry)

    # The user only wants to preview the configuration
    if preview is True:
        print(json.dumps(config, indent=4, sort_keys=True))
        sys.exit(0)

    # Otherwise, run the build!
    self.run_build(config)



def list_builders(self, project=None, zone='us-west1-a'):
    '''list builders, or instances for the project. They should start with
       sregistry-builder

       Parameters
       ==========
       project: specify a project, will default to environment first
       zone: the zone to use, defaults to us-west1-a if environment not set

    '''
    builders = []
    instances = self._get_instances(project, zone)

    for instance in instances['items']:
        builders.append([instance['name'], instance['status']])

    bot.info("[google-compute] Found %s instances" %(len(builders)))
    bot.table(builders)
    bot.newline()
    


def list_templates(self, name=None):
    '''list templates in the builder bundle library. If a name is provided,
       look it up

       Parameters
       ==========
       name: the name of a template to look up
    '''
    configs = self._get_templates()
    rows = []

    # DETAIL: The user wants to retrieve a particular configuration
    if name:
        matches = self._load_templates(name)
        bot.info('Found %s matches for %s' %(len(matches), name))
        for match in matches:
            print(json.dumps(match, indent=4, sort_keys=True))

    # LISTING: If we don't have a specific name, just show all
    else:
        for config in configs['data']:
            rows.append([config['name']])
        bot.table(rows)



def get_templates(self):
    '''list templates in the builder bundle library. If a name is provided,
       look it up

    '''

    base = 'https://singularityhub.github.io/builders'
    base = self._get_and_update_setting('SREGISTRY_BUILDER_REPO', base)
    base = "%s/configs.json" %base
    return self._get(base)



def load_templates(self, name):
    '''load a particular template based on a name. We look for a name IN data,
       so the query name can be a partial string of the full name.

       Parameters
       ==========
       name: the name of a template to look up
    '''
    configs = self._get_templates()
    templates = []

    # The user wants to retrieve a particular configuration
    matches = [x for x in configs['data'] if name in x['name']]
    if len(matches) > 0:
        for match in matches:
            response = self._get(match['id'])
            templates.append(response)
        return templates

    bot.info('No matches found for %s' %name)


def get_instances(self, project=None, zone='us-west1-a'):
    '''get instances will return the (unparsed) list of instances, for
       functions for the user. This is primarily used by get_builders
       to print a list of builder instances.

       Parameters
       ==========
       project: specify a project, will default to environment first
       zone: the zone to use, defaults to us-west1-a if environment not set

    '''
    project = self._get_project(project)
    zone = self._get_zone(zone)

    return self._compute_service.instances().list(project=project, 
                                                  zone=zone).execute()


def load_build_config(self, config=None):
    '''load a google compute config, meaning that we have the following cases:

       1. the user has not provided a config file directly, we look in env.
       2. the environment is not set, so we use a reasonable default
       3. if the final string is not found as a file, we look for it in library
       4. we load the library name, or the user file, else error

       Parameters
       ==========
       config: the config file the user has provided, or the library URI

    '''

    # if the config is not defined, look in environment, then choose a default

    if config is None:
        config = self._get_and_update_setting('SREGISTRY_COMPUTE_CONFIG',
                                     'google/compute/ubuntu/securebuild-2.4.3')

    # If the config is a file, we read it
    if os.path.exists(config):
        return read_json(config)

    # otherwise, try to look it up in library
    configs = self._load_templates(config)
    if configs is None:
        bot.error('%s is not a valid config. %s' %name)
        sys.exit(1)

    bot.info('Found config %s in library!' %config)
    config = configs[0]
    return config
                


def setup_build(self, name, config, startup_script=None):
    '''setup the build based on the selected configuration file, meaning
       producing the configuration file filled in based on the user's input
 
       Parameters
       ==========
       config: the complete configuration file provided by the client
       template: an optional custom start script to use
       start_script: the start script to use, if not defined 
                     defaults to apt (or manager) base in main/templates/build

    '''

    manager = self._get_and_update_setting('SREGISTRY_BUILDER_MANAGER', 'apt')
    startup_script = get_build_template(startup_script, manager)

    # Read in the config to know what we can edit
    if not os.path.exists(config):
        bot.error('Cannot find %s' %config)
        sys.exit(1)

    config = read_json(config)

    # Compute settings that are parsed into runscript via metadata
    defaults = config['data']['metadata']
    config = config['data']['config']

    # Config settings from the environment, fall back to defaults
    image_project = defaults.get('GOOGLE_COMPUTE_PROJECT', 'debian-cloud')
    image_family = defaults.get('GOOGLE_COMPUTE_IMAGE_FAMILY', 'debian-8')
    instance_name = "%s-builder" %name.replace('/','-')
    project = self._get_project()
    zone = self._get_zone()

    # Machine Type
    machine_type = defaults.get('SREGISTRY_BUILDER_machine_type', 'n1-standard-1')
    machine_type = "zones/%s/machineTypes/%s" %(zone, machine_type)

    # Get the image type
    image_response = self._compute_service.images().getFromFamily(
                              project=image_project, 
                              family=image_family).execute()
    source_disk_image = image_response['selfLink']
    storage_bucket = self._bucket_name


    # Add the machine parameters to the config
    config['name'] = instance_name
    config['machine_type'] = machine_type
    config['disks']['initializeParams']['sourceImage'] = source_disk_image

    # Parse through adding metadata values
    metadata = {'items': 
                    [{ 'key': 'startup-script',
                       'value': startup_script }] }

    # Storage Settings from Host
    metadata['BUILDER_STORAGE_BUCKET'] = self._bucket_name

    for key, value in defaults.items():
        if value not in ['', None]:
            entry = { "key": key, 'value': value }
            metadata['items'].append(entry)

    config['metadata'] = metadata

    for key,value in metadata.items():
        entry = {"key":key,'value':value}
        config['metadata']['items'].append(entry)

    return config



@retry(wait_exponential_multiplier=1000,
       wait_exponential_max=10000,
       stop_max_attempt_number=3)

def run_build(self, config):
    '''run a build, meaning inserting an instance. Retry if there is failure

       Parameters
       ==========
       config: the configuration dictionary generated by setup_build

    '''
    project = self._get_project()
    zone = self._get_zone()

    return self._compute_service.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
