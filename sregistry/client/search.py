'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot

def main(args,parser,subparser):

    from sregistry.main import get_client

    for query in args.query:
        if query in ['','*']:
            query = None

        try:
            cli = get_client(query, quiet=args.quiet)
            cli.announce(args.command)
            cli.search(query=query, args=args)
        except NotImplementedError:
            msg = "search is not implemented for %s. Why don't you add it?"
            bot.exit(msg % cli.client_name)
