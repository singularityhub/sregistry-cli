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

from sregistry.logger import bot
import json
import sys
import os


def main(args,parser,subparser):
    from sregistry.main import get_client
    
    # No commands provided, show help
    if len(args.commands) == 0:
        subparser.print_help()
        sys.exit(0)

    # Does the user want to save the image?    
    command = args.commands.pop(0)

    # Option 1: The user wants to kill an instance
    if command == "kill":
        kill(args)    

    # Option 2: Just list running instances
    elif command == "instances":
        instances()

    # Option 3: The user wants to list templates
    elif 'template' in command:
        templates(args)

    # Option 4: View a specific or latest log
    elif command == 'logs':
        list_logs(args)

    # Option 3: The user is providing a Github repo!
    recipe = "Singularity"

    if "github" in command:

        # One argument indicates a recipe
        if len(args.commands) == 1:
            recipe = args.commands.pop(0)       

    else:

        # If a command is provided, but not a Github repo
        bot.error('%s is not a recognized option.' %command)
        subparser.print_help()
        sys.exit(1)


    # Does the user want to specify a name for the collection?
    name = args.name

    # Does the user want to specify a specific config?
    config = args.config

    # No image is needed, we are creating in the cloud
    cli = get_client(quiet=args.quiet)
    cli.announce(args.command)

    response = cli.build(repo=command, 
                         name=name,
                         recipe=recipe,
                         config=config,
                         preview=args.preview)

    # If the client wants to preview, the config is returned
    if args.preview is True:
        print(json.dumps(response, indent=4, sort_keys=True))
        


def kill(args):
    '''kill is a helper function to call the "kill" function of the client,
       meaning we bring down an instance.
    '''
    from sregistry.main import Client as cli
    if len(args.commands) > 0:
        for name in args.commands:
            cli.destroy(name)
    sys.exit(0)

def instances():
    '''list running instances for a user, including all builders and report
       instance names and statuses.
    '''
    from sregistry.main import Client as cli
    cli.list_builders()
    sys.exit(0)


def templates(args, template_name=None):
    '''list a specific template (if a name is provided) or all templates
       available.

       Parameters
       ==========
       args: the argparse object to look for a template name
       template_name: if not set, show all

    '''
    from sregistry.main import get_client

    # We don't need storage/compute connections
    cli = get_client(init=False)

    if len(args.commands) > 0:
        template_name = args.commands.pop(0)
    cli.list_templates(template_name)
    sys.exit(0)


def list_logs(args, container_name=None):
    '''list a specific log for a builder, or the latest log if none provided

       Parameters
       ==========
       args: the argparse object to look for a container name
       container_name: a default container name set to be None (show latest log)

    '''
    from sregistry.main import Client as cli    
    if len(args.commands) > 0:
        container_name = args.commands.pop(0)
    cli.logs(container_name)
    sys.exit(0)
