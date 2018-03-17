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
import pwd
import os


def main(args,parser,subparser):
    from sregistry.main import get_client, Client as cli
    
    # Does the user want to save the image?    
    repo = args.repo.pop(0)

    # Actions include kill, templates
    if len(args.repo) > 0:
        action = args.repo.pop(0)       

    # Does the user want to specify a name for the collection?
    name = args.name

    # Does the user want to specify a specific recipe?
    recipe = args.recipe

    # No image is needed, we are creating in the cloud
    cli = get_client(quiet=args.quiet)
    cli.announce(args.command)

    # Does the user just want to list?
    if args.ls is True:
        cli.list_builders()
        sys.exit(0)

    # Does the user want to kill an instance?
    if action == 'kill':
        cli.destroy(args.name)
        sys.exit(0) 

    # Does the user want to see builder template options?
    template_name = None
    if 'template' in action:
        if len(args.repo) > 0:
            template_name = args.repo.pop(0)
        cli.list_templates(template_name)
        sys.exit(0)

    response = cli.build(repo=repo, 
                         name=name,
                         recipe=recipe, 
                         preview=args.preview)
