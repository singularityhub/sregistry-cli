'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot

def main(args, parser, extra):
    '''the list command corresponds with listing images for an external
       resource. This is different from listing images that are local to the
       database, which should be done with "images"
    '''
    from sregistry.main import get_client
    cli = get_client(quiet=args.quiet)
    
    # If the client doesn't have the command, exit
    if not hasattr(cli, 'ls'):
        msg = "list is not implemented for %s. Why don't you add it?"
        bot.exit(msg % cli.client_name)

    for query in args.query:
        if query in ['','*']:
            query = None

        cli.ls(query=query)
