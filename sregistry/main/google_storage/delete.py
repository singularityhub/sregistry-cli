'''

Copyright (C) 2017-2018 Vanessa Sochat.

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
from retrying import retry
import json
import sys
import os


@retry(wait_exponential_multiplier=1000, 
       wait_exponential_max=10000,
       stop_max_attempt_number=3)


def delete_object(service, bucket_name, object_name):
    '''delete object will delete a file from a bucket

       Parameters
       ==========
       storage_service: the service obtained with get_storage_service
       bucket_name: the name of the bucket
       object_name: the "name" parameter of the object.

    '''
    try:
        operation = service.objects().delete(bucket=bucket_name,
                                             object=object_name).execute()
    except HttpError as e:
        pass
        operation = e
    return operation


def delete(self, name):
    '''delete an image from Google Storage.

       Parameters
       ==========
       name: the name of the file (or image) to delete

    '''

    bot.debug("DELETE %s" % name)

    for file_object in files:
        if isinstance(file_object, dict):
            if "kind" in file_object:
                if file_object['kind'] == "storage#object":
                    object_name = "/".join(file_object['id'].split('/')[:-1])
                    object_name = re.sub('%s/' %self._bucket['name'],'', object_name,1)

                    delete_object(service=self._bucket_service,
                                  bucket_name=bucket['name'],
                                  object_name=object_name)



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
