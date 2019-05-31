'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import confirm_delete
from retrying import retry

def delete(self, image, force=False):
    '''delete an image from Google Storage.

       Parameters
       ==========
       name: the name of the file (or image) to delete

    '''

    bot.debug("DELETE %s" % image)
    files = self._container_query(image)

    for file_object in files:
        if confirm_delete(file_object.name, force):
            file_object.delete()


@retry(wait_exponential_multiplier=1000, 
       wait_exponential_max=10000,
       stop_max_attempt_number=3)


def destroy(self, name):
    '''destroy an instance, meaning take down the instance and stop the build.
       Parameters
       ==========
       name: the name of the instance to stop building.
    '''

    instances = self._get_instances()
    project = self._get_project()
    zone = self._get_zone()
    found = False

    if 'items' in instances:
        for instance in instances['items']:
            if instance['name'] == name:
                found = True
                break

    if found:        
        bot.info('Killing instance %s' %name)
        return self._compute_service.instances().delete(project=project, 
                                                        zone=zone, 
                                                        instance=name).execute()
