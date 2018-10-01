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

from dropbox.exceptions import ApiError
from sregistry.utils import ( parse_image_name, remove_uri )
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
        except ApiError as err:
            share = self.dbx.sharing_create_shared_link(dropbox_path)

        bot.info(share.url)
    return share.url
