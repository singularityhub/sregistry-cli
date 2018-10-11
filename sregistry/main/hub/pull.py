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
from sregistry.utils import ( parse_image_name, remove_uri )
import os
import sys

def pull(self, images, file_name=None, save=True, force=False, **kwargs):
    '''pull an image from an endpoint
 
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

    bot.debug('Execution of PULL for %s images' %len(images))

    finished = []
    for image in images:

        q = parse_image_name(remove_uri(image))

        # Verify image existence, and obtain id
        url = "%s/container/%s/%s:%s" %(self.base, q['collection'], 
                                                   q['image'],
                                                   q['tag'])

        bot.debug('Retrieving manifest at %s' %url)

        manifest = self._get(url)
        manifest['selfLink'] = url        

        # If the manifest reveals a version, update names 
        if "version" in manifest:
            q = parse_image_name('%s@%s' %(q['uri'], manifest['version']))

        if file_name is None:
            file_name = self._get_storage_name(q)
        file_name = os.path.abspath(file_name)

        # Determine if the user already has the image
        if os.path.exists(file_name) and force is False:
            bot.error('Image exists! Remove first, or use --force to overwrite')
            sys.exit(1)

        show_bar = not bool(self.quiet)
        image_file = self.download(url=manifest['image'],
                                   file_name=os.path.basename(file_name),
                                   show_progress=show_bar)

        # If the user is saving to local storage
        if save is True:
            image_uri = "%s:%s@%s" %(manifest['name'], manifest['tag'], manifest['version'])
            container = self.add(image_path=image_file,
                                 image_uri=image_uri,
                                 image_name=file_name,
                                 metadata=manifest,
                                 url=manifest['image'])
            image_file = container.image


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
