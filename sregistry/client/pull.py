'''

Copyright (C) 2016-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
