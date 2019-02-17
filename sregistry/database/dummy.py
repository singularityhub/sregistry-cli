'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
