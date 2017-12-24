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

from sregistry.logger import bot
from sregistry.utils import parse_image_name

import requests
import shutil
import sys
import os


def pull(self, images, file_name=None):

    if not isinstance(images,list):
        images = [images]

    bot.debug('Execution of PULL for %s images' %len(images))

    finished = []
    for image in images:

        q = parse_image_name(image, ext='simg')

        # Verify image existence, and obtain id
        url = "%s/container/%s/%s:%s" %(self.base, q['collection'], q['image'], q['tag'])
        bot.debug('Retrieving manifest at %s' %url)

        manifest = self.get(url)
        
        if file_name is None:
            file_name = q['storage'].replace('/','-')

        image_file = self.download(url=manifest['image'],
                                   file_name=file_name,
                                   show_progress=True)

        if os.path.exists(image_file):
            bot.debug('Retrieved image file %s' %image_file)
            bot.custom(prefix="Success!", message=image_file)
            finished.append(image_file)

        # Reset file name back to None in case of multiple downloads
        file_name = None

    # If the user is only asking for one image
    if len(finished) == 1:
        finished = finished[0]
    return finished
