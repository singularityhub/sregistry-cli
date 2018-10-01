'''

Copyright (C) 2016-2017 Vanessa Sochat.

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
    do_save = True
    if args.nocache is True or not hasattr(cli,'storage'):
        do_save = False
    
    images = args.image
    if not isinstance(images,list):
        images = [images]

    # if the user has given more than one image, not allowed to name
    name = args.name
    if len(images) > 1:
        name = None

    for image in images:

        # Customize client based on uri
        cli = get_client(image, quiet=args.quiet)
        cli.announce(args.command)
        response = cli.pull(images=image,
                            file_name=name,
                            force=args.force,
                            save=do_save)
