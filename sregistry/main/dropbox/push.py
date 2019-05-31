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

# see the registry push for example of how to do this
import dropbox
import sys
import os


def push(self, path, name, tag=None):
    '''push an image to your Dropbox
   
       Parameters
       ==========
       path: should correspond to an absolute image path (or derive it)
       name: should be the complete uri that the user has requested to push.
       tag: should correspond with an image tag. This is provided to mirror Docker

       if the image is less than 150MB, the standard file_upload is used. If
       larger, the image is uploaded in chunks with a progress bar.

    '''
    path = os.path.abspath(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.exit('%s does not exist.' % path)

    # here is an exampole of getting metadata for a container
    names = parse_image_name(remove_uri(name), tag=tag)

    # Get the size of the file
    file_size = os.path.getsize(path)
    chunk_size = 4 * 1024 * 1024
    storage_path = "/%s" %names['storage']

    # This is MB
    # image_size = os.path.getsize(path) >> 20

    # prepare the progress bar
    progress = 0
    bot.show_progress(progress, file_size, length=35)

    # If image is smaller than 150MB, use standard upload
    with open(path, 'rb') as F:
        if file_size <= chunk_size:
            self.dbx.files_upload(F.read(), storage_path)

        # otherwise upload in chunks
        else:

            start = self.dbx.files_upload_session_start(F.read(chunk_size))
            cursor = dropbox.files.UploadSessionCursor(session_id=start.session_id,
                                                       offset=F.tell())
            commit = dropbox.files.CommitInfo(path=storage_path)

            while F.tell() < file_size:

                progress+=chunk_size

                # Finishing up the file, less than chunk_size to go
                if file_size - F.tell() <= chunk_size:
                    self.dbx.files_upload_session_finish(F.read(chunk_size),
                                                         cursor,
                                                         commit)

                # Finishing up the file, less than chunk_size to go
                else:
                    self.dbx.files_upload_session_append(F.read(chunk_size),
                                                         cursor.session_id,
                                                         cursor.offset)
                    cursor.offset = F.tell()

                # Update the progress bar
                bot.show_progress(iteration=progress,
                                  total=file_size,
                                  length=35,
                                  carriage_return=False)


    # Finish up
    bot.show_progress(iteration=file_size,
                      total=file_size,
                      length=35,
                      carriage_return=True)

    # Newline to finish download
    sys.stdout.write('\n')
