'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.utils import ( 
    parse_image_name,
    remove_uri,
    which 
)

from sregistry.logger import bot
import os
import json

# Metadata


def get_metadata(self, image_file, names=None):
    '''extract metadata using Singularity inspect, if the executable is found.
       If not, return a reasonable default (the parsed image name)

       Parameters
       ==========
       image_file: the full path to a Singularity image
       names: optional, an extracted or otherwise created dictionary of
              variables for the image, likely from utils.parse_image_name

    '''
    if names is None:
        names = {}

    metadata = {}

    # We can't return anything without image_file or names
    if image_file:
        if not os.path.exists(image_file):
            bot.error('Cannot find %s.' %image_file)
            return names or metadata

    # The user provided a file, but no names
    if not names:
        names = parse_image_name(remove_uri(image_file))

    # Look for the Singularity Executable
    singularity = which('singularity')['message']

    # Inspect the image, or return names only
    if os.path.exists(singularity) and image_file:
        from spython.main import Client as Singularity

        # Store the original quiet setting
        is_quiet = Singularity.quiet

        # We try and inspect, but not required (wont work within Docker)
        try:
            Singularity.quiet = True
            updates = Singularity.inspect(image=image_file)
        except:
            bot.warning('Inspect command not supported, metadata not included.')
            updates = None

        # Restore the original quiet setting
        Singularity.quiet = is_quiet

        # Try loading the metadata
        if updates is not None:
            try:
                updates = json.loads(updates)
                metadata.update(updates)
            except:
                pass

    metadata.update(names)
    return metadata
