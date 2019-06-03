'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import (
    get_recipe_tag,
    read_json,
    parse_image_name,
    remove_uri
)
from sregistry.main.google_storage.utils import get_build_template
from sregistry.logger import RobotNamer

from retrying import retry
from time import sleep
import json
import sys
import os


def build(self, repo, 
                config=None,
                name=None, 
                commit=None,
                tag="latest",
                recipe="Singularity",
                preview=False):

    '''trigger a build on Google Cloud (storage then compute) given a name
       recipe, and Github URI where the recipe can be found.
    
       Parameters
       ==========
       name: should be the complete uri that the user has requested to push.
       commit: a commit to use, not required, and can be parsed from URI
       repo: should correspond to a Github URL or (if undefined) used local repo.
       tag: a user specified tag, to take preference over tag in name
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

    # First priority - user has provided a tag
    names['tag'] = tag or names['tag']

    # If we still don't have custom tag, check the recipe
    if names['tag'] == "latest" and recipe != "Singularity":
        tag = get_recipe_tag(recipe)
    names = parse_image_name(remove_uri(name), tag=tag)

    # The commit is the version (after the @)
    commit = commit or names['version']

    # Setup the build
    config = self._setup_build(name=names['url'], recipe=recipe,
                               repo=repo, config=config,
                               tag=tag, commit=commit)

    # The user only wants to preview the configuration
    if preview is True:
        return config

    # Otherwise, run the build!
    return self._run_build(config)



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
        bot.debug('Found %s matches for %s' %(len(matches), name))
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


def get_ipaddress(self, name, retries=3, delay=3):
    '''get the ip_address of an inserted instance. Will try three times with
       delay to give the instance time to start up.

       Parameters
       ==========
       name: the name of the instance to get the ip address for.
       retries: the number of retries before giving up
       delay: the delay between retry

       Note from @vsoch: this function is pretty nasty.

    '''
    for _ in range(retries):

        # Retrieve list of instances
        instances = self._get_instances()

        for instance in instances['items']:
            if instance['name'] == name:

                # Iterate through network interfaces
                for network in instance['networkInterfaces']:
                    if network['name'] == 'nic0':

                        # Access configurations
                        for subnet in network['accessConfigs']:
                            if subnet['name'] == 'External NAT':
                                if 'natIP' in subnet:
                                    return subnet['natIP']

        sleep(delay) 
    bot.warning('Did not find IP address, check Cloud Console!')



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
    # If the config is already a dictionary, it's loaded
    if isinstance(config, dict):
        bot.debug('Config is already loaded.')
        return config

    # if the config is not defined, look in environment, then choose a default
    if config is None:
        config = self._get_and_update_setting('SREGISTRY_COMPUTE_CONFIG',
                                     'google/compute/ubuntu/securebuild-2.4.3')

    # If the config is a file, we read it
    elif os.path.exists(config):
        return read_json(config)

    # otherwise, try to look it up in library
    configs = self._load_templates(config)
    if configs is None:
        bot.exit('%s is not a valid config. %s' % config)

    bot.info('Found config %s in library!' % config)
    config = configs[0]

    return config
                


def setup_build(self, name, repo, config, tag=None, commit=None,
                      recipe="Singularity", startup_script=None):

    '''setup the build based on the selected configuration file, meaning
       producing the configuration file filled in based on the user's input
 
       Parameters
       ==========
       config: the complete configuration file provided by the client
       template: an optional custom start script to use
       tag: a user specified tag for the build, derived from uri or manual
       recipe: a recipe, if defined, overrides recipe set in config.
       commit: a commit to check out, if needed
       start_script: the start script to use, if not defined 
                     defaults to apt (or manager) base in main/templates/build

    '''

    manager = self._get_and_update_setting('SREGISTRY_BUILDER_MANAGER', 'apt')
    startup_script = get_build_template(startup_script, manager)

    # Read in the config to know what we can edit
    config = self._load_build_config(config)
    if not config:
        bot.exit('Cannot find config, check path or URI.')

    # Ensure that the builder config is intended for the client
    self._client_tagged(config['data']['tags'])

    # Compute settings that are parsed into runscript via metadata
    defaults = config['data']['metadata']
    selfLink = config['links']['self']

    # Make sure the builder repository and folder is passed forward
    builder_repo = config['data']['repo']
    builder_bundle = config['data']['path']
    builder_id = config['data']['id']
    config = config['data']['config']

    # Config settings from the environment, fall back to defaults
    image_project = defaults.get('GOOGLE_COMPUTE_PROJECT', 'debian-cloud')
    image_family = defaults.get('GOOGLE_COMPUTE_IMAGE_FAMILY', 'debian-8')

    # Generate names, description is for repo, name is random
    instance_name = "%s-builder %s" %(name.replace('/','-'), selfLink)
    robot_name = RobotNamer().generate()

    zone = self._get_zone()

    # Machine Type
    machine_type = defaults.get('SREGISTRY_BUILDER_machine_type', 'n1-standard-1')
    machine_type = "zones/%s/machineTypes/%s" %(zone, machine_type)

    # Disk Size
    disk_size = defaults.get('SREGISTRY_BUILDER_disk_size', '100')

    # Get the image type
    image_response = self._compute_service.images().getFromFamily(
                              project=image_project, 
                              family=image_family).execute()
    source_disk_image = image_response['selfLink']

    # Add the machine parameters to the config
    config['name'] = robot_name
    config['description'] = instance_name
    config['machineType'] = machine_type
    config['disks'].append({
                    "autoDelete": True,
                    "boot": True,
                    "initializeParams": { 'sourceImage': source_disk_image,
                                          'diskSizeGb': disk_size }
                   })

    # Metadata base
    metadata = {'items': 

                    [{ 'key': 'startup-script',
                       'value': startup_script },

                    # Storage Settings from Host

                     { 'key':'SREGISTRY_BUILDER_STORAGE_BUCKET',
                       'value':self._bucket_name }]}


    # Runtime variables take priority over defaults from config
    # and so here we update the defaults with runtime
    # ([defaults], [config-key], [runtime-setting])

    # User Repository
    defaults = setconfig(defaults, 'SREGISTRY_USER_REPO', repo)
    
    # Container Namespace (without tag/version)
    defaults = setconfig(defaults, 'SREGISTRY_CONTAINER_NAME', name)

    # User Repository Commit
    defaults = setconfig(defaults, 'SREGISTRY_USER_COMMIT', commit)

    # User Repository Branch
    defaults = setconfig(defaults, 'SREGISTRY_USER_BRANCH', "master")

    # User Repository Tag
    defaults = setconfig(defaults, 'SREGISTRY_USER_TAG', tag)

    # Builder repository url
    defaults = setconfig(defaults, 'SREGISTRY_BUILDER_REPO', builder_repo)

    # Builder commit
    defaults = setconfig(defaults, 'SREGISTRY_BUILDER_COMMIT')

    # Builder default runscript
    defaults = setconfig(defaults, 'SREGISTRY_BUILDER_RUNSCRIPT', "run.sh")

    # Builder repository url
    defaults = setconfig(defaults, 'SREGISTRY_BUILDER_BRANCH', "master")

    # Builder id in repository
    defaults = setconfig(defaults, 'SREGISTRY_BUILDER_ID', builder_id)

    # Builder repository relative folder path
    defaults = setconfig(defaults, 'SREGISTRY_BUILDER_BUNDLE', builder_bundle)

    # Number of extra hours to debug
    defaults = setconfig(defaults, 'SREGISTRY_BUILDER_DEBUGHOURS', "4")

    # Hours to kill running job
    defaults = setconfig(defaults, 'SREGISTRY_BUILDER_KILLHOURS', "10")

    # Recipe set at runtime
    defaults = setconfig(defaults, 'SINGULARITY_RECIPE', recipe)

    # Branch of Singularity to install
    defaults = setconfig(defaults, 'SINGULARITY_BRANCH')

    # Singularity commit to use (if needed)
    defaults = setconfig(defaults, 'SINGULARITY_COMMIT')

    # Singularity Repo to Use
    defaults = setconfig(defaults,'SINGULARITY_REPO', 
                                  'https://github.com/cclerget/singularity.git')

    # Update metadata config object

    seen = ['SREGISTRY_BUILDER_STORAGE_BUCKET', 'startup-script']

    for key, value in defaults.items():

        # This also appends empty values, they are meaningful
        if value not in seen:
            entry = { "key": key, 'value': value }
            metadata['items'].append(entry)
            seen.append(key)

    config['metadata'] = metadata
    return config


def setconfig(lookup, key, value=None):
    '''setconfig will update a lookup to give priority based on the following:
 
       1. If both values are None, we set the value to None
       2. If the currently set (the config.json) is set but not runtime, use config
       3. If the runtime is set but not config.json, we use runtime
       4. If both are set, we use runtime

    '''
    lookup[key] = value or lookup.get(key)
    return lookup



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

    bot.custom(prefix='INSTANCE', message=config['name'], color="CYAN")
    bot.info(config['description'])

    response = self._compute_service.instances().insert(project=project,
                                                        zone=zone,
                                                        body=config).execute()

    # Direct the user to the web portal with log
    ipaddress = self._get_ipaddress(config['name'])
    bot.info('Robot Logger: http://%s' %ipaddress)
    bot.info('Allow a few minutes for web server install, beepboop!')
    return response
