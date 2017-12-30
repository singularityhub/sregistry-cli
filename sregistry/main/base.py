'''

sregistry.api: base template for making a connection to an API

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

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

from requests.exceptions import HTTPError

from sregistry.logger import bot
from sregistry.defaults import SREGISTRY_DATABASE
from sregistry.auth import ( read_client_secrets, update_client_secrets )
import threading
import shutil
import requests
import tempfile
import json
import sys
import re
import os


class ApiConnection(object):

    def __init__(self):
 
        self.headers = None
        self.base = None
        self._reset_headers()

        # If client initialized with _init_db, do it
        if hasattr(self,"_init_db"):
            self._init_db(SREGISTRY_DATABASE)

        # TO DO: need to implement higher level functions that work with images
        # to do corresponding action in database.
        # we need a sort of call back for push, pull, delete, etc.


# Metadata

    def speak(self):
        '''a function for the client to announce him or herself, depending
           on the level specified.
        '''
        bot.info('[client|%s] [database|%s]' %(self.client_name,
                                               self.database))

    def __repr__(self):
        return "[client][%s]" %self.client_name

    def __str__(self):
        return "[client][%s]" %self.client_name

    def client_name(self):
        return self.__module__.split('.')[-1]


    def _get_setting(self, name):
        '''return a setting from the environment (first priority) and then
           secrets (second priority) if one can be found. If not, return None.
        ''' 

        # First priority is the environment
        setting = os.environ.get(name)

        # Second priority is the secrets file
        if setting is None:
            secrets = read_client_secrets()
            if self.client_name in secrets:
                secrets = secrets[self.client_name]
                if name in secrets:
                    setting = secrets[name]

        return setting


    def _get_and_update_setting(self, name):
        '''Look for a setting in the environment (first priority) and then
           the settings file (second). If something is found, the settings
           file is updated. The order of operations works as follows:

           1. The .sregistry settings file is used as a cache for the variable
           2. the environment variable always takes priority to cache, and if
              found, will update the cache.
           3. If the variable is not found and the cache is set, we are good
           5. If the variable is not found and the cache isn't set, return None

           So the user of the function can assume a return of None equates to
           not set anywhere, and take the appropriate action.
        ''' 

        setting = self._get_setting(name)

        # If the setting is found, update the client secrets
        if setting is not None:
            updates = {name : setting}
            setting = update_client_secrets(backend=self.client_name, 
                                            updates=updates)
        return setting


# Headers

    def _get_headers(self):
        return self.headers

    def _reset_headers(self):
        self.headers = {'Content-Type':"application/json"}

    def _update_headers(self,fields=None):
        '''update headers with a token & other fields
        '''
        reset_headers = True
        if hasattr(self, 'headers'):
            if self.headers is not None:
                reset_headers = False

        if reset_headers is True:
            self._reset_headers()

        if fields is not None:
            for key,value in fields.items():
                self.headers[key] = value

        header_names = ",".join(list(self.headers.keys()))
        bot.debug("Headers found: %s" %header_names)


# Requests


    def _delete(self,url,return_json=True):
        '''delete request, use with caution
        '''
        bot.debug('DELETE %s' %url)
        return self._call(url,
                          func=requests.delete,
                          return_json=return_json)


    def _put(self,url,data=None,return_json=True):
        '''put request
        '''
        bot.debug("PUT %s" %url)
        return self._call(url,
                          func=requests.put,
                          data=data,
                          return_json=return_json)



    def _post(self,url,data=None,return_json=True):
        '''post will use requests to get a particular url
        '''
        bot.debug("POST %s" %url)
        return self._call(url,
                          func=requests.post,
                          data=data,
                          return_json=return_json)




    def _get(self,url,headers=None,token=None,data=None,return_json=True):
        '''get will use requests to get a particular url
        '''
        bot.debug("GET %s" %url)
        return self._call(url,
                          func=requests.get,
                          data=data,
                          return_json=return_json)



    def _paginate_get(self, url, headers=None, return_json=True, start_page=None):
        '''paginate_call is a wrapper for get to paginate results
        '''
        get = '%s&page=1' %(url)
        if start_page is not None:
            get = '%s&page=%s' %(url,start_page)

        results = []
        while get is not None:
            result = self._get(url, headers=headers, return_json=return_json)
            # If we have pagination:
            if isinstance(result, dict):
                if 'results' in result:
                    results = results + result['results']
                get = result['next']
            # No pagination is a list
            else:
                return result
        return results
        

    def download(self, url, file_name, headers=None, show_progress=True):
        '''stream to a temporary file, rename on successful completion
        :param file_name: the file name to stream to
        :param url: the url to stream from
        :param headers: additional headers to add
        '''

        fd, tmp_file = tempfile.mkstemp(prefix=("%s.tmp." % file_name)) 
        os.close(fd)

        # Check here if exists
        if requests.head(url).status_code == 200:
            response = self._stream(url,headers=headers,stream_to=tmp_file)

            if isinstance(response, HTTPError):
                bot.error("Error downloading %s, exiting." %url)
                sys.exit(1)
            shutil.move(tmp_file, file_name)
        else:
            bot.error("Invalid URL %s" %url)
        return file_name


    def _stream(self, url, headers=None, stream_to=None):
        '''stream is a get that will stream to file_name
        '''

        bot.debug("GET %s" %url)

        if headers == None:
            headers = self._reset_headers()

        response = requests.get(url,         
                                headers=headers,
                                stream=True)

        if response.status_code == 200:

            # Keep user updated with Progress Bar?
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



    def _call(self,url,func,data=None,return_json=True, stream=False):
        '''call will issue the call, and issue a refresh token
        given a 401 response.
        :param func: the function (eg, post, get) to call
        :param url: the url to send file to
        :param data: additional data to add to the request
        :param return_json: return json if successful
        '''
 
        if data is not None:
            if not isinstance(data,dict):
                data = json.dumps(data)

        response = func(url=url,
                        headers=self.headers,
                        data=data,
                        stream=stream)

        # Errored response, try again with refresh
        if response.status_code in [500,502]:
            bot.error("Beep boop! %s: %s" %(response.reason,
                                            response.status_code))
            sys.exit(1)

        # Errored response, try again with refresh
        if response.status_code == 404:
            bot.error("Beep boop! %s: %s" %(response.reason,
                                            response.status_code))
            sys.exit(1)


        # Errored response, try again with refresh
        if response.status_code == 401:
            bot.error("Your credentials are expired! %s: %s" %(response.reason,
                                                               response.status_code))
            sys.exit(1)

        elif response.status_code == 200:

            if return_json:

                try:
                    response =  response.json()

                except ValueError:
                    bot.error("The server returned a malformed response.")
                    sys.exit(1)

        return response
