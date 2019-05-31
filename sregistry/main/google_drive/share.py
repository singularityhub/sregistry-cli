'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
import sys


def share(self, query, share_to):
    '''share will use the client to get an image based on a query, and then
       the link with an email or endpoint (share_to) of choice.
    '''

    images = self._container_query(query, quiet=True)
    if len(images) == 0:
        bot.info('Cannot find a remote image matching %s' % query)
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
