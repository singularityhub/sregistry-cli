'''

Copyright (C) 2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2018 Vanessa Sochat.

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
import tempfile


def download_layer_task(worker, image_id, repo_name, download_folder=None):
    '''download an image layer (.tar.gz) to a specified download folder.
       This task is done by a multiprocess worker that has inherited the
       core stream/download functions of the parent client.

       Parameters
       ==========
       image_id: the shasum id of the layer, already determined to not exist
       repo_name: the image name (library/ubuntu) to retrieve
       download_folder: download to this folder. If not set, uses temp.

    '''
    url = "%s/%s/blobs/%s" % (worker.base,
                              repo_name,
                              image_id)

    bot.verbose("Downloading layers from %s" % url)

    if download_folder is None:
        download_folder = tempfile.mkdtemp()

    download_folder = "%s/%s.tar.gz" % (download_folder, image_id)

    # Update user what we are doing
    bot.debug("Downloading layer %s" % image_id)

    # Step 1: Download the layer atomically
    file_name = "%s.%s" % (download_folder,
                           next(tempfile._get_candidate_names()))

    tar_download = worker.download(url, file_name)

    try:
        os.rename(tar_download, download_folder)
    except Exception:
        msg = "Cannot untar layer %s," % tar_download
        msg += " was there a problem with download?"
        bot.error(msg)
        sys.exit(1)

    worker._update_token()
    return download_folder
