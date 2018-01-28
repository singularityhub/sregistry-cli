'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2017 Vanessa Sochat.

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

def main(args,parser,subparser):
    '''the images entrypoint is intended to list images locally in the user
       database, optionally taking one or more query string to subset the 
       search
    '''
    from sregistry.main import get_client
    cli = get_client(quiet=args.quiet)

    for query in args.query:
        if query in ['','*']:
            query = None
        cli.images(query=query)
