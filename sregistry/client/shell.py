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

from sregistry.logger import bot
import traceback
import os
import select
import sys


def main(args,parser,subparser):

    from sregistry.main import Client as cli
    shells = [bpython, python]
    for shell in shells:
        try:
            return shell(cli)
        except ImportError:
            pass
    

def ipython(cli):
    '''Not sure how to add the client to the working environment, so
      disabled for now
    '''
    from IPython import start_ipython
    from sregistry.main import Client as cli
    start_ipython(argv=[], locals_={'cli':cli})


def bpython(cli):
    import bpython
    from sregistry.main import Client as cli
    bpython.embed(locals_={'client':cli})

def python(cli):
    import code
    from sregistry.main import Client as cli
    code.interact(local={"client":cli})
