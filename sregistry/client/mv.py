'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot

def main(args, parser, extra):

    from sregistry.main import get_client
    cli = get_client(quiet=args.quiet)
    cli.announce(args.command)

    # If the client doesn't have the command, exit
    if not hasattr(cli, 'mv'):
        msg = "move is not implemented for %s. Why don't you add it?"
        bot.exit(msg % cli.client_name)

    cli.mv(image_name=args.name,
           path=args.path)
