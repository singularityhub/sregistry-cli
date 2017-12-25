# Global Commands

The following commands are provided for the client for all endpoints, as they
pertain to interaction with the local sregistry database.


## Add

For all clients, we can add an image or delete an image with .

# add or remove.

# TODO: stopped here - need to have "add' and "remove" functions to base
# API client - should move files to sregistry database and then organize?


# If you don't have an image, use Singularity Hub client to get, or do
# singularity pull shub://vsoch/hello-world.img
from singularity.cli import Singularity
cli = Singularity()
image_path = cli.pull('shub://vsoch/hello-world')


###################################################################
# Push
###################################################################

from singularity.registry.client import Client

sreg = Client()    # Singularity Registry Client
                   # Default base: 127.0.0.1
                   # Secrets: $HOME/.sregistry OR
                   # $SREGISTRY_CLIENT_SECRETS


# Push an image, this is the path on your filesystem
image_path = 'vsoch-hello-world-master.img'

# This is the tag, and image name you want in the registry
image_tag = 'rawr'
image_name = 'vsoch/dinosaurs'

response = sreg.push(path=image_path,
                     name=image_name,
                     tag=image_tag)

# DEBUG Headers found: Content-Type
# [================================] 391/391 MB - 00:00:00
# Upload finished! [Return status 201 created]


###################################################################
# Query
###################################################################
