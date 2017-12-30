'''

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

from sregistry.client import Singularity
from sregistry.logger import bot, ProgressBar
from sregistry.utils import (
    parse_image_name,
    parse_header
)

# see the registry push for example of how to do this
from googleapiclient.http import MediaFileUpload
from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

from retrying import retry
import requests
import six
import json
import sys
import os



def push(self, path, name, tag=None):
    '''push an image to Google Cloud Storage, meaning uploading it
    
    path: should correspond to an absolte image path (or derive it)
    name: should be the complete uri that the user has requested to push.
    tag: should correspond with an image tag. This is provided to mirror Docker
    '''
    path = os.path.abspath(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.error('%s does not exist.' %path)
        sys.exit(1)

    # here is an exampole of getting metadata for a container
    cli = Singularity()
    metadata = cli.inspect(image_path=path, quiet=True)

    # This returns a data structure with collection, container, based on uri
    names = parse_image_name(name,tag=tag)
    
    bot.spinner.start()
    result = self._upload(path, names['storage'])
    bot.spinner.stop()



@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def upload(self, source, destination):
    '''get_folder will return the folder with folder_name, and if create=True,
    will create it if not found. If folder is found or created, the metadata is
    returned, otherwise None is returned
    :param storage_service: the drive_service created from get_storage_service
    :param bucket: the bucket object from get_bucket
    :param file_name: the name of the file to upload
    :param bucket_path: the path to upload to
    '''

    blob = self._bucket.blob(destination)
    blob.upload_from_filename(filename=source, 
                              content_type="application/zip",
                              client=self._service)

    url = blob.public_url
    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')

    return url
