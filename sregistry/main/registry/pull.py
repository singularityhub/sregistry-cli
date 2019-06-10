'''

pull.py: pull function for singularity registry

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from requests.exceptions import SSLError
from requests.models import Response
from sregistry.utils import (parse_image_name, remove_uri)
from sregistry.logger import bot
import os


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

    bot.debug('Execution of PULL for %s images' % len(images))

    finished = []
    for image in images:

        q = parse_image_name(remove_uri(image))

        # If a custom registry is not set, use default base
        if q['registry'] is None:
            q['registry'] = self.base

        # Ensure https is added back to the registry  uri
        q = self._add_https(q)

        # All custom registries need api appended
        if not q['registry'].endswith('api'):
            q['registry'] = '%s/api' % q['registry']

        # Verify image existence, and obtain id
        url = "%s/container/%s/%s:%s" %(q['registry'], 
                                        q['collection'], 
                                        q['image'], 
                                        q['tag'])

        bot.debug('Retrieving manifest at %s' % url)

        try:
            manifest = self._get(url)
        except SSLError:
            bot.exit('Issue with %s, try exporting SREGISTRY_REGISTRY_NOHTTPS.' % url)

        # Private container collection
        if isinstance(manifest, Response):

            # Requires token
            if manifest.status_code in [403, 401]:

                SREGISTRY_EVENT = self.authorize(request_type="pull",
                                                 names=q)
                headers = {'Authorization': SREGISTRY_EVENT}
                self._update_headers(headers)
                manifest = self._get(url)

                # Still denied
                if isinstance(manifest, Response):
                    if manifest.status_code == 403:
                        manifest = 403

        if isinstance(manifest, int):
            if manifest == 400:
                bot.exit('Bad request (400). Is this a private container?')
            elif manifest == 404:
                bot.exit('Container not found (404)')
            elif manifest == 403:
                bot.exit('Unauthorized (403)')

        # Successful pull
        if "image" in manifest:

            # Add self link to manifest
            manifest['selfLink'] = url

            if file_name is None:
                file_name = q['storage'].replace('/','-')

            # Clear headers of previous token
            self._reset_headers()
    
            # Show progress if not quiet
            image_file = self.download(url=manifest['image'],
                                       file_name=file_name,
                                       show_progress=not self.quiet)

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
