'''

pull.py: pull function for singularity registry

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import parse_image_name
import globus_sdk
import os


def pull(self, images, file_name=None, save=True, **kwargs):
    '''pull an image from a Globus endpoint. The user must have the default
       local endpoint set up. For example:

       6881ae2e-db26-11e5-9772-22000b9da45e:.singularity/shub/sherlock_vep.simg

    Parameters
    ==========
    images: refers to the globus endpoint id and image path.
    file_name: the user's requested name for the file. It can 
               optionally be None if the user wants a default.
    save: if True, you should save the container to the database
          using self.add(). For globus this is the only option, and
          we don't have control over when this happens.
    
    Returns
    =======
    finished: a single container path, or list of paths
    '''

    # Ensure we have a transfer client
    if not hasattr(self, 'transfer_client'):
        self._init_transfer_client()

    if not isinstance(images,list):
        images = [images]

    bot.debug('Execution of PULL for %s images' %len(images))

    finished = []
    for image in images:

        # Split the name into endpoint and rest

        endpoint, remote = self._parse_endpoint_name(image)
        source = self.transfer_client.get_endpoint(endpoint)

        name = os.path.basename(remote)
        q = parse_image_name(name, default_collection=source['name'])

        # The user must have a personal endpoint

        endpoints = self._get_endpoints()

        if len(endpoints['my-endpoints']) == 0:
            bot.exit('You must have a personal endpoint to transfer the container')

        # Take the first endpoint that is active

        dest = None
        for _, contender in endpoints['my-endpoints'].items():
            if contender['gcp_connected'] is True:
                dest = contender
                break

        # Exit if none are active, required!

        if dest is None:
            bot.exit('No activated local endpoints online! Start to transfer')

        # We need to know the full path of the endpoint

        base = self._get_endpoint_path(dest['id'])
        storage_folder = '%s/%s' %(base, q['collection'])
        self._create_endpoint_folder(dest['id'], storage_folder)

        label = "Singularity Registry Pull"
        tdata = globus_sdk.TransferData(self.transfer_client, 
                                        source['id'],
                                        dest['id'],
                                        label=label,
                                        sync_level="checksum")

        image = os.path.join(base, q['storage'])
        tdata.add_item(remote, image)
        bot.info('Requesting transfer to %s' %q['storage'])
        transfer_result = self.transfer_client.submit_transfer(tdata)
        bot.info(transfer_result['message'])
        finished.append(transfer_result)

    if len(finished) == 1:
        finished = finished[0]
    return finished
