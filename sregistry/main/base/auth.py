'''

sregistry.api: base template for making a connection to an API

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


def require_secrets(self, params=None):
    '''require secrets ensures that the client has the secrets file, and
       specifically has one or more parameters defined. If params is None,
       only a check is done for the file.

       Parameters
       ==========
       params: a list of keys to lookup in the client secrets, eg:
 
         secrets[client_name][params1] should not be in [None,''] or not set

    '''
    name = self.client_name                

    # Check 1: the client must have secrets, period
    has_secrets = True

    # Secrets file not asked for (incorrectly) but still wanted
    # The client shouldn't be calling this function if didn't init secrets
    if not hasattr(self,'secrets'):
        has_secrets = False

    # Secret file was not found, period
    elif hasattr(self,'secrets'):
        if self.secrets is None: 
            has_secrets = False

    # The client isn't defined in the secrets file
    elif self.client_name not in self.secrets: 
        has_secrets = False

    # Missing file or client secrets, fail
    if has_secrets is False:
        message = '%s requires client secrets.' %name
        bot.error(message)
        sys.exit(1)

    # Check 2: we have secrets and lookup, do we have all needed params?
    if params is not None:

        # Assume list so we can always parse through
        if not isinstance(params,list):
            params = [params]

        for param in params:

            # The parameter is not a key for the client
            if param not in self.secrets[name]: 
                has_secrets = False

            # The parameter is a key, but empty or undefined
            elif self.secrets[name][param] in [None,'']: 
                has_secrets=False

        # Missing parameter, exit on fail
        if has_secrets is False:
            message = 'Missing %s in client secrets.' %param
            bot.error(message)
            sys.exit(1)


def auth_flow(self, url):
    '''auth flow is a function to present the user with a url to retrieve
       some token/code, and then copy paste it back in the terminal.

        Parameters
        ==========
        url should be a url that is generated for the user to go to and accept
        getting a credential in the browser.
    
    '''
    print('Please go to this URL and login: {0}'.format(url))
    get_input = getattr(__builtins__, 'raw_input', input)
    message = 'Please enter the code you get after login here: '
    code = get_input(message).strip()
    return code
