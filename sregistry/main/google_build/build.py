'''

Copyright (C) 2018-2019 Vanessa Sochat.

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
from googleapiclient.errors import HttpError
from sregistry.utils import (
    get_image_hash,
    get_installdir,
    get_recipe_tag,
    read_json,
    parse_image_name,
    remove_uri
)

from sregistry.main.google_build.utils import get_build_template

from sregistry.logger import RobotNamer
from retrying import retry
from time import sleep
import json
import sys
import os


def build(self, name,
                recipe="Singularity", 
                tag=None,
                preview=False):

    '''trigger a build on Google Cloud (builder then storage) given a name
       recipe, and Github URI where the recipe can be found.
    
       Parameters
       ==========
       recipe: the local recipe to build.
       name: should be the complete uri that the user has requested to push.
       tag: a custom tag (overrides recipe provided tag)
       preview: if True, preview but don't run the build

       Environment
       ===========
       SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION: the version of Singularity
           to use, defaults to 3.0.0

    '''
    bot.debug("BUILD %s" % recipe)

    # This returns a data structure with collection, container, based on uri
    names = parse_image_name(remove_uri(name), tag=tag)

    # Load the build configuration
    config = self._load_build_config(name=names['uri'], recipe=recipe)

    # The user only wants to preview the configuration
    if preview is True:
        return config

    # Otherwise, run the build!
    return self._run_build(config)


def load_build_config(self, name, recipe):
    '''load a google compute config, meaning that we start with a template,
       and mimic the following example cloudbuild.yaml:

        steps:
        - name: "singularityware/singularity:${_SINGULARITY_VERSION}"
          args: ['build', 'julia-centos-another.sif', 'julia.def']
        artifacts:
          objects:
            location: 'gs://sregistry-gcloud-build-vanessa'
            paths: ['julia-centos-another.sif']


        Parameters
        ==========
        recipe: the local recipe file for the builder.
        name: the name of the container, based on the uri

    '''
    version_envar = 'SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION'
    version = self._get_and_update_setting(version_envar, '3.0')
    config = get_build_template()

    # Name is in format 'dinosaur/container-latest'

    # The command to give the builder, with image name
    container_name = '%s.sif' % name.replace('/','-', 1)
    config['steps'][0]['name'] = 'singularityware/singularity:%s' % version
    config['steps'][0]['args'] = ['build', container_name, recipe]

    config["artifacts"]["objects"]["location"] = "gs://%s" % self._bucket_name
    config["artifacts"]["objects"]["paths"] = [container_name]

    return config
                

@retry(wait_exponential_multiplier=1000,
       wait_exponential_max=10000,
       stop_max_attempt_number=3)


def run_build(self, config):
    '''run a build, meaning creating a build. Retry if there is failure
    '''

    bot.custom(prefix='BUILD', message=config['name'], color="CYAN")
    project = self._get_project()

    response = self._build_service.projects().builds().create(body=config, projectId=project).execute()
    build_id = response['metadata']['build']['id']
    status = response['metadata']['build']['status']

    bot.log("build %s: %s" % (build_id, status))

    while status not in ['COMPLETE', 'FAILED']:
        sleep(30)
        response = self._build_service.projects().builds().get(id=build_id, 
                                                               projectId=project).execute()

        #TODO: need to figure out how to send recipe and other files
        build_id = response['id']
        status = response['status']
        bot.log("build %s: %s" % (build_id, status))
