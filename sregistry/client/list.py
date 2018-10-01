'''

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


def main(args,parser,subparser):
    '''the list command corresponds with listing images for an external
       resource. This is different from listing images that are local to the
       database, which should be done with "images"
    '''
    from sregistry.main import get_client
    cli = get_client(quiet=args.quiet)
    
    for query in args.query:
        if query in ['','*']:
            query = None

        cli.ls(query=query)
