"""

sregistry.api: base template for making a connection to an API

Copyright (C) 2017-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from requests.exceptions import HTTPError
import requests

from sregistry.utils import get_tmpfile
from sregistry.logger import bot
import shutil
import json
import sys


def delete(self, url, headers=None, return_json=True, default_headers=True):

    """delete request, use with caution
    """
    bot.debug("DELETE %s" % url)
    return self._call(
        url,
        headers=headers,
        func=requests.delete,
        return_json=return_json,
        default_headers=default_headers,
    )


def head(self, url):
    """head request, typically used for status code retrieval, etc.
    """
    bot.debug("HEAD %s" % url)
    return self._call(url, func=requests.head)


def healthy(self, url):
    """determine if a resource is healthy based on an accepted response (200)
       or redirect (301)

       Parameters
       ==========
       url: the URL to check status for, based on the status_code of HEAD

    """
    response = requests.get(url)
    status_code = response.status_code
    if status_code != 200:
        bot.error("%s, response status code %s." % (url, status_code))
        return False
    return True


def put(self, url, headers=None, data=None, return_json=True, default_headers=True):

    """put request
    """
    bot.debug("PUT %s" % url)
    return self._call(
        url,
        headers=headers,
        func=requests.put,
        data=data,
        return_json=return_json,
        default_headers=default_headers,
    )


def post(self, url, headers=None, data=None, return_json=True, default_headers=True):

    """post will use requests to get a particular url
    """

    bot.debug("POST %s" % url)
    return self._call(
        url,
        headers=headers,
        func=requests.post,
        data=data,
        return_json=return_json,
        default_headers=default_headers,
    )


def get(
    self,
    url,
    headers=None,
    token=None,
    data=None,
    return_json=True,
    default_headers=True,
    quiet=False,
):

    """get will use requests to get a particular url
    """
    bot.debug("GET %s" % url)
    return self._call(
        url,
        headers=headers,
        func=requests.get,
        data=data,
        return_json=return_json,
        default_headers=default_headers,
        quiet=quiet,
    )


def paginate_get(self, url, headers=None, return_json=True, start_page=None):
    """paginate_call is a wrapper for get to paginate results
    """

    geturl = "%s&page=1" % (url)
    if start_page is not None:
        geturl = "%s&page=%s" % (url, start_page)

    results = []
    while geturl is not None:
        result = self._get(url, headers=headers, return_json=return_json)
        # If we have pagination:
        if isinstance(result, dict):
            if "results" in result:
                results = results + result["results"]
            geturl = result["next"]
        # No pagination is a list
        else:
            return result
    return results


def verify(self):
    """
       verify will return a True or False to determine to verify the
       requests call or not. If False, we should the user a warning message,
       as this should not be done in production!

    """
    from sregistry.defaults import DISABLE_SSL_CHECK

    if DISABLE_SSL_CHECK is True:
        bot.warning("Verify of certificates disabled! ::TESTING USE ONLY::")

    return not DISABLE_SSL_CHECK


def download(self, url, file_name, headers=None, show_progress=True):

    """stream to a temporary file, rename on successful completion

        Parameters
        ==========
        file_name: the file name to stream to
        url: the url to stream from
        headers: additional headers to add
        force: If the final image exists, don't overwrite
        show_progress: boolean to show progress bar
    """

    tmp_file = get_tmpfile(prefix="%s.tmp." % file_name)

    # Should we verify the request?
    verify = self._verify()

    # Check here if exists
    if requests.head(url, verify=verify).status_code in [200, 401]:
        response = self.stream(
            url, headers=headers, stream_to=tmp_file, show_progress=show_progress
        )

        if isinstance(response, HTTPError):
            bot.exit("Error downloading %s, exiting." % url)

        shutil.move(tmp_file, file_name)
    else:
        bot.error("Invalid url or permissions %s" % url)
    return file_name


def stream(
    self,
    url,
    headers=None,
    stream_to=None,
    retry=True,
    default_headers=True,
    show_progress=True,
):
    """
        stream is a get that will stream to file_name. This stream is intended
        to take a url and (optionally) a set of headers and file to stream to,
        and will generate a response with requests.get.

        Parameters
        ==========
        url: the url to do a requests.get to
        headers: any updated headers to use for the requets
        stream_to: the file to stream to
        show_progress: boolean to show progress bar
        retry: should the client retry? (intended for use after token refresh)
               by default we retry once after token refresh, then fail.
    """
    bot.debug("GET %s" % url)

    # Ensure headers are present, update if not
    if headers is None:
        if self.headers is None:
            self._reset_headers()
        headers = self.headers.copy()

    response = requests.get(url, headers=headers, verify=self._verify(), stream=True)

    # Deal with token if necessary
    if response.status_code == 401 and retry is True:
        if hasattr(self, "_update_token"):
            self._update_token(response)
            return self.stream(
                url, headers, stream_to, retry=False, show_progress=show_progress
            )

    if response.status_code == 200:
        return self._stream(response, stream_to=stream_to, show_progress=show_progress)

    bot.exit("Problem with stream, response %s" % (response.status_code))


def stream_response(self, response, stream_to=None, show_progress=True):
    """
       stream response is one level higher up than stream, starting with a 
       response object and then performing the stream without making the
       requests.get. The expectation is that the request was successful 
       (status code 20*).
       show_progress: boolean to show progress bar

       Parameters
       ==========
       response: a response that is ready to be iterated over to download in
                 streamed chunks
       stream_to: the file to stream to


    """
    if response.status_code == 200:

        if show_progress is False:
            bot.quiet = True

        # Keep user updated with Progress Bar, if not quiet
        content_size = None
        if "Content-Length" in response.headers:
            progress = 0
            content_size = int(response.headers["Content-Length"])
            bot.show_progress(progress, content_size, length=35)

        chunk_size = 1 << 20
        with open(stream_to, "wb") as filey:
            for chunk in response.iter_content(chunk_size=chunk_size):
                filey.write(chunk)
                if content_size is not None:
                    progress += chunk_size
                    bot.show_progress(
                        iteration=progress,
                        total=content_size,
                        length=35,
                        carriage_return=False,
                    )

        # Newline to finish download
        sys.stdout.write("\n")

        return stream_to

    bot.exit("Problem with stream, response %s" % (response.status_code))


def call(
    self,
    url,
    func,
    data=None,
    headers=None,
    return_json=True,
    stream=False,
    retry=True,
    default_headers=True,
    quiet=False,
):

    """call will issue the call, and issue a refresh token
       given a 401 response, and if the client has a _update_token function

       Parameters
       ==========
       func: the function (eg, post, get) to call
       url: the url to send file to
       headers: if not None, update the client self.headers with dictionary
       data: additional data to add to the request
       return_json: return json if successful
       default_headers: use the client's self.headers (default True)

    """

    if data is not None:
        if not isinstance(data, dict):
            data = json.dumps(data)

    heads = dict()
    if default_headers is True:
        heads = self.headers.copy()

    if headers is not None:
        if isinstance(headers, dict):
            heads.update(headers)

    response = func(
        url=url, headers=heads, data=data, verify=self._verify(), stream=stream
    )

    # Errored response, try again with refresh
    if response.status_code in [500, 502]:
        bot.exit("Beep boop! %s: %s" % (response.reason, response.status_code))

    # Errored response, try again with refresh
    if response.status_code == 404:

        # Not found, we might want to continue on
        if quiet is False:
            bot.exit("Beep boop! %s: %s" % (response.reason, response.status_code))

    # Errored response, try again with refresh
    if response.status_code == 401:

        # If client has method to update token, try it once
        if retry is True and hasattr(self, "_update_token"):

            # A result of None indicates no update to the call
            self._update_token(response)
            return self._call(
                url,
                func,
                data=data,
                headers=headers,
                return_json=return_json,
                stream=stream,
                retry=False,
            )

        bot.exit(
            "Your credentials are expired! %s: %s"
            % (response.reason, response.status_code)
        )

    elif response.status_code == 200:

        if return_json:

            try:
                response = response.json()
            except ValueError:
                bot.exit("The server returned a malformed response.")

    return response
