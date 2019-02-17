'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''


def main(args, parser, subparser):
    '''sharing an image means sending a remote share from an image you
       control to a contact, usually an email.
    '''
    from sregistry.main import get_client
    images = args.image

    if not isinstance(images,list):
        images = [images]

    for image in images:
        print(image)
        
        # Detect any uri, and refresh client if necessary
        cli = get_client(image, quiet=args.quiet)
        cli.announce(args.command)
        cli.share(image, share_to=args.share_to)
