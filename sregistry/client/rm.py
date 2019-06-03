'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot

def main(args, parser, extra):

    from sregistry.main import get_client

    image = args.image

    cli = get_client(image, quiet=args.quiet)
    cli.announce(args.command)

    if not hasattr(cli, 'rm'):
        msg = "remove is not implemented for %s. Why don't you add it?"
        bot.exit(msg % cli.client_name)

    result = cli.rm(image)

    if result is None:
        bot.exit("No {} record found in the database".format(image))
