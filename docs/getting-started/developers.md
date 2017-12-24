# Singularity Registry Global Client

**for developers**

This walkthrough will show interaction with the Singularity Registry Global client from within Python. This is what you would be interested in if you want to integrate the client into your own applications.

## Environment variables
If you recall from the [getting started](README.md), sregistry will help you to manage
a local database, and the settings are determined by environment variables. We can
check the defaults that are set from within python. Here is what we see if there are
no special variables exported:


```
# We can look at the defaults, if we don't have any environment variables
from sregistry.defaults import *

# The database will be written to our .singularity cache
SREGISTRY_DATABASE
# '/home/vanessa/.singularity/sregistry.db

# And the client secrets for sregistry also have a default location
SREGISTRY_CLIENT_SECRETS
# '/home/vanessa/.sregistry'
```

For the Singularity Registry secrets, the location will be set to default
even if they aren't found. The reason for this is that some clients might need
the file to write client-specific variables and options.

## Client

When we import a client, the client we get depends on environment too.
If there is an export of `SREGISTRY_CLIENT` in the environment, we get that.
Otherwise, we get a client for Singularity Hub.

```
from sregistry.main import Client
# Database: /home/vanessa/.singularity/sregistry.db
```

In the above, also note that it has initialized our default database.
Now, any operations that we do via the sregistry tool will update our 
database. 

## Commands
The following commands are provided with the client for all endpoints, as they pertain to
interaction with the local database.


### Add
By default, images 

THINK ABOUT:
 - images should be saved by default (to cache or where pulled?)
 - can we put some kind of watcher on the file? so when it moves or changes, the database updates?
 - should the images that are pulled with sregistry be managed there too?
 - if they are managed there, how does a user easily retrieve (to interact with singularithy). Something like
 - image = $(sregistry get vsoch/hello-world:latest)
      TODO: implement the get function, and yes the images should be pulled and put in some known location
      - if a previously existing image is gone, then update database and give warning message.
      - If we use / manage cache, can give user functions to clean / work with it, but we would need to be careful
        aabout shared caches.

For all clients, we can add an image or delete an image with 
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

For commands (e.g., pull) that might not exist for all endpoints, see [client specific docs](../clients).
