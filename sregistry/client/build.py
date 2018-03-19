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
import json
import sys
import os


def main(args,parser,subparser):
    from sregistry.main import get_client, Client as cli
    
    # No commands provided, show help
    if len(args.commands) == 0:
        subparser.print_help()
        sys.exit(0)

    # Does the user want to save the image?    
    command = args.commands.pop(0)

    # Option 1: The user wants to kill an instance
    if command == "kill":
        cli.destroy(args.name)
        sys.exit(0) 

    # Option 2: Just list running instances
    elif command == "instances":
        cli.list_builders()
        sys.exit(0)

    # Option 3: The user wants to list templates
    elif 'template' in command:
        template_name = None
        if len(args.commands) > 0:
            template_name = args.commands.pop(0)
        cli.list_templates(template_name)
        sys.exit(0)


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
        

