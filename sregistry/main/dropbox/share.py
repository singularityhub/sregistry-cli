'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.utils import (parse_image_name, remove_uri)
from sregistry.logger import bot


def share(self, query, share_to=None):
    '''share will use the client to get a shareable link for an image of choice.
       the functions returns a url of choice to send to a recipient.
    '''

    names = parse_image_name(remove_uri(query))

    # Dropbox path is the path in storage with a slash
    dropbox_path = '/%s' % names['storage']        

    # First ensure that exists
    if self.exists(dropbox_path) is True:

        # Create new shared link
        try:
            share = self.dbx.sharing_create_shared_link_with_settings(dropbox_path)

        # Already exists!
        except:
            share = self.dbx.sharing_create_shared_link(dropbox_path)

        bot.info(share.url)
    return share.url
