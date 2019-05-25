'''

Copyright (C) 2016-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot

def main(args, parser, subparser):

    from sregistry.main import get_client
    images = args.query
    if not isinstance(images, list):
        images = [images]

    for image in images:
        cli = get_client(image, quiet=args.quiet)

        # If the client doesn't have the command, exit
        if not hasattr(cli, 'get'):
            bot.exit("get for images requires using the sqlite database.")

        cli.get(image)
