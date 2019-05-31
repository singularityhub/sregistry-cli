'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.utils import confirm_delete


def delete(self, image, force=False):
    '''delete an image from Google Storage.

       Parameters
       ==========
       name: the name of the file (or image) to delete

    '''

    bot.debug("DELETE %s" % image)
    files = self._container_query(image)

    for file_object in files:
        if confirm_delete(file_object.name, force):
            file_object.delete()
