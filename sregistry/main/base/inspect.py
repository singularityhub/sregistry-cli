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

from sregistry.utils import ( 
    mkdir_p,
    parse_image_name,
    remove_uri,
    run_command,
    which 
)

from sregistry.logger import bot
from sregistry.auth import ( read_client_secrets, update_client_secrets )
import os
import json

# Metadata


def get_metadata(self, image_file, names={}):
    '''extract metadata using Singularity inspect, if the executable is found.
       If not, return a reasonable default (the parsed image name)

       Parameters
       ==========
       image_file: the full path to a Singularity image
       names: optional, an extracted or otherwise created dictionary of
              variables for the image, likely from utils.parse_image_name

    '''
    metadata = dict()

    # We can't return anything without image_file or names
    if image_file is not None:
        if not os.path.exists(image_file):
            bot.error('Cannot find %s.' %image_file)
            return names or metadata

    # The user provided a file, but no names
    if not names:
        names = parse_image_name(remove_uri(image_file))

    # Look for the Singularity Executable
    singularity = which('singularity')['message']

    # Inspect the image, or return names only
    if os.path.exists(singularity) and image_file is not None:
        from spython.main import Client as Singularity

        # We try and inspect, but not required (wont work within Docker)
        try:
            Singularity.quiet = True
            updates = Singularity.inspect(image=image_file)
        except:
            bot.warning('Inspect command not supported, metadata not included.')
            updates = None

        # Try loading the metadata
        if updates is not None:
            try:
                updates = json.loads(updates)
                metadata.update(updates)
            except:
                pass

    metadata.update(names)
    return metadata
