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
from sregistry.utils import ( 
    parse_image_name, 
    remove_uri
)
import os
import sys


def add(self, image_path=None,
              image_name=None,
              url=None,
              metadata=None,
              save=True, 
              copy=False):

    '''dummy add simple returns an object that mimics a database entry, so the
       calling function (in push or pull) can interact with it equally. Most 
       variables (other than image_path) are not used.'''

    # We can only save if the image is provided
    if image_path is not None:
        if not os.path.exists(image_path):
            bot.error('Cannot find %s' %image_path)
            sys.exit(1)

    if image_name is None:
        bot.error('You must provide an image uri <collection>/<namespace>')
        sys.exit(1)
    names = parse_image_name( remove_uri(image_name) )
    bot.debug('Added %s to filesystem' % names['uri'])    

    # First check that we don't have one already!
    class container:
        name=names['image']
        tag=names['tag']
        image=image_path
        client=self.client_name
        url=url
        uri=names['uri']

    bot.info("[container][%s] %s" % (action,names['uri']))
    return container


def init_db(self, db_path=None):
    '''initialize the database, meaning we just set the name to be dummy
    '''

    # Database Setup, use default if uri not provided
    self.database = 'dummy'
