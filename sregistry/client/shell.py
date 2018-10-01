'''

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

import sys

def main(args,parser,subparser):

    from sregistry.main import Client as cli

    lookup = { 'ipython': ipython,
               'python': python,
               'bpython': bpython }

    shells = ['ipython', 'python', 'bpython']

    # If the user supplies a client choice, make into a uri
    if args.endpoint is not None:
        if not args.endpoint.endswith('://'):
            args.endpoint = '%s://' %args.endpoint


    # If the user asked for a specific shell via environment
    shell = cli._get_and_update_setting('SREGISTRY_SHELL')
    if shell is not None:
        shell = shell.lower()
        if shell in lookup:
            try:    
                return lookup[shell](args)
            except ImportError:
                pass

    # Otherwise present order of liklihood to have on system
    for shell in shells:
        try:
            return lookup[shell](args)
        except ImportError:
            pass
    

def ipython(args):
    '''give the user an ipython shell, optionally with an endpoint of choice.
    '''

    # The client will announce itself (backend/database) unless it's get
    from sregistry.main import get_client
    client = get_client(args.endpoint)
    client.announce(args.command)
    from IPython import embed
    embed()


def bpython(args):
    import bpython
    from sregistry.main import get_client
    client = get_client(args.endpoint)
    client.announce(args.command)
    from sregistry.database.models import Container, Collection
    bpython.embed(locals_={'client': client,
                           'Container': Container,
                           'Collection': Collection})

def python(args):
    import code
    from sregistry.main import get_client
    client = get_client(args.endpoint)
    client.announce(args.command)
    from sregistry.database.models import Container, Collection
    code.interact(local={"client":client,
                         'Container': Container,
                         'Collection': Collection})
