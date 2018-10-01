'''

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

from sregistry.auth import ( get_secrets_file, read_client_secrets )
from sregistry.logger import bot
from sregistry.utils import write_json
import json
import sys
import os



def main(args,parser,subparser):
    
    # No commands provided, print help, show clients

    if len(args.commands) == 0:
        subparser.print_help()
        usage()
        sys.exit(0)

    # Get the chosen action
    command = args.commands.pop(0)
    backend = None

    # If still one more, there is a targeted backend
    if len(args.commands) > 0:
        backend = args.commands.pop(0)

    # Option 1: The user wants to list all or a specific command
    if command == "ls":
        list_backends(backend) 

    # Option 2: Remove a configuration
    elif command == "delete":
        delete_backend(backend)

    # Option 3: Activate a backend
    elif command == "activate":
        activate(backend)

    # Option 4: Deactivate a backend
    elif command == 'deactivate':
        deactivate()

    # Option 5: get a status

    elif command == "status":
        status(backend)

    # Option 6: add a config value 

    elif command == "add":
        if len(args.commands) > 1:
            variable = args.commands.pop(0)
            value = args.commands.pop(0)
            add(backend, variable, value, force=args.force)
        else:
            print('Usage: sregistry backend add <backend> <variable> <value>')

    # Option 7: Remove a config value
    elif command in ["remove", "rm"]:
        if len(args.commands) > 0:
            variable = args.commands.pop(0)
            remove(backend, variable)
        else:
            print('Usage: sregistry backend remove <backend> <variable>')


    else:

        subparser.print_help()

def usage():
    print('''
             sregistry backend ls:     list backends found in secrets
             sregistry backend ls hub
             sregistry backend status: get status
             sregistry backend rm <backend> remove a backend
             sregistry backend de|activate: activate or deactivate
             sregistry backend remove nvidia token
             sregistry backend add nvidia token 123455
               
             SREGISTRY_NVIDIA_TOKEN 123455
          ''')

def status(backend):
    '''print the status for all or one of the backends.
    '''
    print('[backend status]')
    settings = read_client_secrets()
    print('There are %s clients found in secrets.' %len(settings))
    if 'SREGISTRY_CLIENT' in settings:
        print('active: %s' %settings['SREGISTRY_CLIENT'])
        update_secrets(settings)
    else:
        print('There is no active client.')


def add(backend, variable, value, force=False):
    '''add the variable to the config
    '''
    print('[add]')
    settings = read_client_secrets()

    # If the variable begins with the SREGISTRY_<CLIENT> don't add it
    prefix = 'SREGISTRY_%s_' %backend.upper()
    if not variable.startswith(prefix):
        variable = '%s%s' %(prefix, variable)

    # All must be uppercase
    variable = variable.upper()
    bot.info("%s %s" %(variable, value))
    
    # Does the setting already exist?

    if backend in settings:
        if variable in settings[backend] and force is False:
            previous = settings[backend][variable]
            bot.error('%s is already set as %s. Use --force to override.' %(variable, previous))
            sys.exit(1)

    if backend not in settings:
        settings[backend] = {}

    settings[backend][variable] = value
    update_secrets(settings)
    


def remove(backend, variable):
    '''remove a variable from the config, if found.
    '''
    print('[remove]')
    settings = read_client_secrets()

    # If the variable begins with the SREGISTRY_<CLIENT> don't add it
    prefixed = variable
    prefix = 'SREGISTRY_%s_' %backend.upper()
    if not variable.startswith(prefix):
        prefixed = '%s%s' %(prefix, variable)

    # All must be uppercase
    variable = variable.upper()
    bot.info(variable)
    
    # Does the setting already exist?
    if backend in settings:
        if variable in settings[backend]:
            del settings[backend][variable]           
        if prefixed in settings[backend]:
            del settings[backend][prefixed]           
        update_secrets(settings)


def activate(backend):
    '''activate a backend by adding it to the .sregistry configuration file.
    '''
    settings = read_client_secrets()
    if backend is not None:
        settings['SREGISTRY_CLIENT'] = backend
        update_secrets(settings)
        print('[activate] %s' %backend)


def update_secrets(secrets):
    secrets_file = get_secrets_file()
    write_json(secrets, secrets_file)


def delete_backend(backend):
    '''delete a backend, and update the secrets file
    '''
    settings = read_client_secrets()
    if backend in settings:
        del settings[backend]

        # If the backend was the active client, remove too
        if 'SREGISTRY_CLIENT' in settings:
            if settings['SREGISTRY_CLIENT'] == backend:
                del settings['SREGISTRY_CLIENT']

        update_secrets(settings)
        print('[delete] %s' %backend)
    else:
        if backend is not None:
            print('%s is not a known client.' %backend)
        else:
            print('Please specify a backend to delete.')


def deactivate():    
    '''deactivate any active backend by removing it from the .sregistry
       configuration file
    '''
    settings = read_client_secrets()
    if "SREGISTRY_CLIENT" in settings:
        del settings['SREGISTRY_CLIENT']
        update_secrets(settings)
        print('[deactivated]')
    else:
        print('There is no active client')


def list_backends(backend=None):
    '''return a list of backends installed for the user, which is based on
       the config file keys found present
 
       Parameters
       ==========
       backend: a specific backend to list. If defined, just list parameters.

    '''
    settings = read_client_secrets()

    # Backend names are the keys
    backends = list(settings.keys())    
    backends = [b for b in backends if b!='SREGISTRY_CLIENT']

    if backend in backends:
        bot.info(backend)
        print(json.dumps(settings[backend], indent=4, sort_keys=True))
    else:
        if backend is not None:
            print('%s is not a known client.' %backend)
        bot.info("Backends Installed")
        print('\n'.join(backends))
