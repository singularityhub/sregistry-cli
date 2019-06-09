'''

Copyright (C) 2016-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''


def main(args, parser, extra):

    lookup = { 'ipython': ipython,
               'python': python,
               'bpython': bpython }

    shells = ['ipython', 'python', 'bpython']

    # If the user supplies a client choice, make into a uri
    if args.endpoint is not None:
        if not args.endpoint.endswith('://'):
            args.endpoint = '%s://' %args.endpoint

    from sregistry.main import get_client
    cli = get_client(args.endpoint, quiet=args.quiet)

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
