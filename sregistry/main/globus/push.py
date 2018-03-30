'''

push.py: push functions for sregistry client

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

from spython.main import Client as Singularity
from sregistry.logger import bot
from sregistry.defaults import SREGISTRY_STORAGE
from sregistry.utils import parse_image_name
import globus_sdk
from globus_sdk.exc import TransferAPIError
import json
import sys
import os


def push(self, path, name, tag=None):
    '''push an image to Globus endpoint. In this case, the name is the
       globus endpoint id and path.

       --name <endpointid>:/path/for/image

    '''

    # Split the name into endpoint and rest

    endpoint, remote = self._parse_endpoint_name(name)

    path = os.path.abspath(path)
    image = os.path.basename(path)
    bot.debug("PUSH %s" % path)

    # Flatten image uri into image name

    q = parse_image_name(image)

    if not os.path.exists(path):
        bot.error('%s does not exist.' %path)
        sys.exit(1)

    # Ensure we have a transfer client
    if not hasattr(self, 'transfer_client'):
        self._init_transfer_client()

    # The user must have a personal endpoint

    endpoints = self._get_endpoints()

    if len(endpoints['my-endpoints']) == 0:
        bot.error('You must have a personal endpoint to transfer the container')
        sys.exit(1) 

    # Take the first endpoint that is active

    source_endpoint = None
    for eid,contender in endpoints['my-endpoints'].items():
       if contender['gcp_connected'] is True:
           source_endpoint = contender
           break

    # Exit if none are active, required!

    if source_endpoint is None:
        bot.error('No activated local endpoints online! Go online to transfer')
        sys.exit(1)


    # The destination endpoint should have an .singularity/shub folder set
    self._create_endpoint_cache(endpoint)

    # SREGISTRY_STORAGE must be an endpoint
    # if the image isn't already there, add it first

    added = self.add(image_path=path, 
                     image_uri=q['uri'],
                     copy=True)
    
    label = "Singularity Registry Transfer for %s" %added.name
    tdata = globus_sdk.TransferData(self.transfer_client, 
                                    source_endpoint['id'],
                                    endpoint,
                                    label=label,
                                    sync_level="checksum")
    image = ".singularity/shub/%s" %image
    tdata.add_item(added.image, image)
    bot.info('Requesting transfer from local %s to %s:%s' %(SREGISTRY_STORAGE,
                                                            endpoint, image))
    transfer_result = self.transfer_client.submit_transfer(tdata)
    bot.info(transfer_result['message'])
    return transfer_result
