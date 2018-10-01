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
from sregistry.utils import ( 
    parse_image_name, 
    remove_uri
)
import os
import sys


def add(self, image_path=None,
              image_uri=None,
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

    if image_uri is None:
        bot.error('You must provide an image uri <collection>/<namespace>')
        sys.exit(1)
    names = parse_image_name( remove_uri(image_uri) )
    bot.debug('Added %s to filesystem' % names['uri'])    

    # Create a dummy container on the fly
    class DummyContainer:
        def __init__(self, image_path, client_name, url, names):
            self.image=image_path
            self.client=client_name
            self.url=url
            self.name=names['image']
            self.tag=names['tag']
            self.uri=names['uri']

    container = DummyContainer(image_path, self.client_name, url, names)

    bot.info("[container][%s] %s" % (action,names['uri']))
    return container


def init_db(self, db_path=None):
    '''initialize the database, meaning we just set the name to be dummy
    '''

    # Database Setup, use default if uri not provided
    self.database = 'dummy'
