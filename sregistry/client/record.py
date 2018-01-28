'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017-2018 Vanessa Sochat.

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


def main(args, parser, subparser):

    '''the record command is intended for working with remote endpoint records,
       such as adding an entry to the local database for the record without
       downloading the image. To do the same but retrieve and store the image,
       the user should use pull. To retrieve but not store the image, the user
       can use pull with no-cache.
    '''

    from sregistry.main import get_client
    images = args.image

    if not isinstance(images,list):
        images = [images]

    for image in images:
        cli = get_client(image, quiet=args.quiet)
        cli.announce(args.command)
        cli.record(image, action=args.action)
