'''

Copyright (C) 2016-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot

def main(args, parser, extra):

    from sregistry.main import get_client
 
    image = args.image
    name = args.name

    # Customize client based on uri
    cli = get_client(image, quiet=args.quiet)
    cli.announce(args.command)

    # Does the user want to save the image?
    do_save = True
    if args.nocache is True or not hasattr(cli, 'storage'):
        do_save = False

    # If the client doesn't have the command, exit
    if not hasattr(cli, 'pull'):
        msg = "pull is not implemented for %s. Why don't you add it?"
        bot.exit(msg % cli.client_name)

    cli.pull(images=image,
             file_name=name,
             force=args.force,
             save=do_save)
