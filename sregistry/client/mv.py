'''

Copyright (C) 2018-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

def main(args, parser, subparser):

    from sregistry.main import Client as cli
    cli.announce(args.command)
    cli.mv(image_name=args.name[0],
           path=args.path[0])
