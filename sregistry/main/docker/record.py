'''

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
from sregistry.utils import ( parse_image_name, remove_uri )
import os

def record(self, images, action='add'):
    '''record an image from an endpoint. This function is akin to a pull,
       but without retrieving the image. We only care about the list of images
       (uris) to look up, and then the action that the user wants to take
 
    Parameters
    ==========
    images: refers to the uri given by the user to pull in the format
    <collection>/<namespace>. You should have an API that is able to 
    retrieve metadata for a container based on this url.
    action: the action to take with the record. By default we add it, meaning
            adding a record (metadata and file url) to the database. It is
            recommended to place the URL for the image download under the 
            container.url field, and the metadata (the image manifest) should
            have a selfLink to indicate where it came from.
    '''
    
    # Take a look at pull for an example of this logic.
    if not isinstance(images,list):
        images = [images]

    bot.debug('Execution of RECORD[%s] for %s images' %(action, len(images)))

    # If used internally we want to return a list to the user.
    for image in images:

        # 0. Update the base in case we aren't working with default
        base = self._update_base(image)
        q = parse_image_name(remove_uri(image), base=base)

        digest = q['version'] or q['tag']

        # This is the Docker Hub namespace and repository
        manifests = self._get_manifests(q['url'], digest)

        # This is the url where the manifests were obtained
        url = self._get_manifest_selfLink(q['url'], digest)

        # We again use the "add" function, but we don't give an image path
        # so it's just added as a record
        container = self.add(image_uri=q['uri'],
                             metadata=manifests,
                             url=url)

