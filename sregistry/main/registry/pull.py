'''

pull.py: pull function for singularity registry

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
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
from requests.models import Response
from sregistry.utils import ( parse_image_name, remove_uri )
import requests
import os
import sys

def pull(self, images, file_name=None, save=True, **kwargs):
    '''pull an image from a singularity registry
 
    Parameters
    ==========
    images: refers to the uri given by the user to pull in the format
    <collection>/<namespace>. You should have an API that is able to 
    retrieve a container based on parsing this uri.
    file_name: the user's requested name for the file. It can 
               optionally be None if the user wants a default.
    save: if True, you should save the container to the database
          using self.add()
    
    Returns
    =======
    finished: a single container path, or list of paths
    '''

    if not isinstance(images,list):
        images = [images]

    # Interaction with a registry requires secrets
    self.require_secrets()

    bot.debug('Execution of PULL for %s images' %len(images))

    finished = []
    for image in images:

        q = parse_image_name(remove_uri(image))

        # Verify image existence, and obtain id
        url = "%s/container/%s/%s:%s" %(self.base, q['collection'], q['image'], q['tag'])
        bot.debug('Retrieving manifest at %s' %url)
        manifest = self._get(url)

        # Private container collection
        if isinstance(manifest, Response):

            # Requires token
            if manifest.status_code == 403:

                SREGISTRY_EVENT = self.authorize(request_type="pull",
                                                 names=q)
                headers = {'Authorization': SREGISTRY_EVENT }
                self._update_headers(headers)
                manifest = self._get(url)

                # Still denied
                if manifest.status_code == 403:
                    manifest = 403

        if isinstance(manifest, int):
            if manifest == 400:
                bot.error('Bad request (400). Is this a private container?')
            elif manifest == 404:
                bot.error('Container not found (404)')
            elif manifest == 403:
                bot.error('Unauthorized (403)')
            sys.exit(1)


        # Successful pull
        if "image" in manifest:

            # Add self link to manifest
            manifest['selfLink'] = url

            if file_name is None:
                file_name = q['storage'].replace('/','-')
    
            image_file = self.download(url=manifest['image'],
                                       file_name=file_name,
                                       show_progress=True)

            # If the user is saving to local storage
            if save is True:
                image_uri = "%s/%s:%s" %(manifest['collection'], 
                                         manifest['name'],
                                         manifest['tag'])
                container = self.add(image_path = image_file,
                                     image_uri = image_uri,
                                     metadata = manifest,
                                     url = manifest['image'])
                image_file = container.image

            if os.path.exists(image_file):
                bot.debug('Retrieved image file %s' %image_file)
                bot.custom(prefix="Success!", message=image_file)
                finished.append(image_file)

        if len(finished) == 1:
            finished = finished[0]
        return finished


    upload_to = os.path.basename(names['storage'])

    encoder = MultipartEncoder(fields={'collection': names['collection'],
                                       'name':names['image'],
                                       'metadata':metadata,
                                       'tag': names['tag'],
                                       'datafile': (upload_to, open(upload_from, 'rb'), 'text/plain')})

    progress_callback = create_callback(encoder)
    monitor = MultipartEncoderMonitor(encoder, progress_callback)
    headers = {'Content-Type': monitor.content_type,
               'Authorization': SREGISTRY_EVENT }

    try:
        r = requests.post(url, data=monitor, headers=headers)
        message = self._read_response(r)

        print('\n[Return status {0} {1}]'.format(r.status_code, message))

    except KeyboardInterrupt:
        print('\nUpload cancelled.')

