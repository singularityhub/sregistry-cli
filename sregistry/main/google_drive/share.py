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
import sys
import os



def share(self, query, share_to):
    '''share will use the client to get an image based on a query, and then
       the link with an email or endpoint (share_to) of choice.
    '''

    images = self._container_query(query, quiet=True)
    if len(images) == 0:
        bot.error('Cannot find a remote image matching %s' %query)
        sys.exit(0)

    image = images[0]

    def callback(request_id, response, exception):
        if exception:
            # Handle error
            print(exception)
        else:
            share_id = response.get('id')
            bot.info('Share to %s complete: %s!' %(share_to, share_id))

    batch = self._service.new_batch_http_request(callback=callback)
    user_permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': share_to
    }

    batch.add(self._service.permissions().create(
        fileId=image['id'],
        body=user_permission,
        fields='id',
    ))

    batch.execute()
    return image
