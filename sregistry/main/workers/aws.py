'''

Copyright (C) 2018 Vanessa Sochat.

These are aws tasks.

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

from sregistry.defaults import DISABLE_SSL_CHECK
from requests.exceptions import HTTPError

from sregistry.logger import bot
import json
import os
import re
import requests
import shutil
import sys
import tempfile


################################################################################
## Shared Tasks for the Worker
################################################################################

def download_task(url, headers, download_to, download_type='layer'):
    '''download an image layer (.tar.gz) to a specified download folder.
       This task is done by using local versions of the same download functions
       that are used for the client.
       core stream/download functions of the parent client.

       Parameters
       ==========
       image_id: the shasum id of the layer, already determined to not exist
       repo_name: the image name (library/ubuntu) to retrieve
       download_to: download to this folder. If not set, uses temp.
 

    '''
    # Update the user what we are doing
    bot.verbose("Downloading %s from %s" % (download_type, url))

    # Step 1: Download the layer atomically
    file_name = "%s.%s" % (download_to,
                           next(tempfile._get_candidate_names()))

    tar_download = download(url, file_name, headers=headers)

    try:
        shutil.move(tar_download, download_to)
    except Exception:
        msg = "Cannot untar layer %s," % tar_download
        msg += " was there a problem with download?"
        bot.error(msg)
        sys.exit(1)

    return download_to


################################################################################
## Base Functions for Tasks
##
##  These basic tasks are intended for the worker to use, without needing
##  to pickle them for multiprocessing. It works because they don't belong
##  to a client (which we cannot pickle) and are imported by the worker
##  functions directly.
##
################################################################################
        

def download(url, file_name, headers=None, show_progress=True):
    '''stream to a temporary file, rename on successful completion

        Parameters
        ==========
        file_name: the file name to stream to
        url: the url to stream from
        headers: additional headers to add
    '''

    fd, tmp_file = tempfile.mkstemp(prefix=("%s.tmp." % file_name)) 
    os.close(fd)

    if DISABLE_SSL_CHECK is True:
        bot.warning('Verify of certificates disabled! ::TESTING USE ONLY::')

    verify = not DISABLE_SSL_CHECK
    response = stream(url, headers=headers, stream_to=tmp_file)
    shutil.move(tmp_file, file_name)
    return file_name


def stream(url, headers, stream_to=None, retry=True):
    '''stream is a get that will stream to file_name. Since this is a worker
       task, it differs from the client provided version in that it requires
       headers.
    '''
    bot.debug("GET %s" % url)

    if DISABLE_SSL_CHECK is True:
        bot.warning('Verify of certificates disabled! ::TESTING USE ONLY::')

    # Ensure headers are present, update if not
    response = requests.get(url,  
                            headers=headers,
                            verify=not DISABLE_SSL_CHECK,
                            stream=True)

    # If we get permissions error, one more try with updated token
    if response.status_code in [401, 403]:
        headers = update_token(headers)
        return stream(url, headers, stream_to, retry=False)

    # Successful Response
    elif response.status_code == 200:

        # Keep user updated with Progress Bar
        content_size = None
        if 'Content-Length' in response.headers:
            progress = 0
            content_size = int(response.headers['Content-Length'])
            bot.show_progress(progress,content_size,length=35)

        chunk_size = 1 << 20
        with open(stream_to,'wb') as filey:
            for chunk in response.iter_content(chunk_size=chunk_size):
                filey.write(chunk)
                if content_size is not None:
                    progress+=chunk_size
                    bot.show_progress(iteration=progress,
                                      total=content_size,
                                      length=35,
                                      carriage_return=False)

        # Newline to finish download
        sys.stdout.write('\n')

        return stream_to 

    bot.error("Problem with stream, response %s" %(response.status_code))
    sys.exit(1)



def update_token(headers):
    '''update_token uses HTTP basic authentication to attempt to authenticate
    given a 401 response. We take as input previous headers, and update 
    them.

    Parameters
    ==========
    response: the http request response to parse for the challenge.
    
    '''
    try:
        from awscli.clidriver import create_clidriver
    except:
        bot.exit('Please install pip install sregistry[aws]')

    driver = create_clidriver()
    aws = driver.session.create_client('ecr')
    tokens = aws.get_authorization_token()
    token = tokens['authorizationData'][0]['authorizationToken']    

    try:
        token = {"Authorization": "Basic %s" % token}
        headers.update(token)

    except Exception:
        bot.error("Error getting token.")
        sys.exit(1)

    return headers
