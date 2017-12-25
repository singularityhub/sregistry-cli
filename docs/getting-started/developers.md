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

# And this means storage is in a subfolder, shub
SREGISTRY_STORAGE
# '/home/vanessa/.singularity/shub

# And the client secrets for sregistry also have a default location
SREGISTRY_CLIENT_SECRETS
# '/home/vanessa/.sregistry'
```

And you of course can export either of `SREGISTRY_DATABASE` or `SREGISTRY_STORAGE` to 
change these defaults. For the Singularity Registry secrets, the location will be set to default
even if they aren't found. The reason for this is that some clients might need
the file to write client-specific variables and options.

## Client

When we import a client, the client we get depends on environment too.
If there is an export of `SREGISTRY_CLIENT` in the environment, we get that.
Otherwise, we get a client for Singularity Hub.

```
from sregistry.main import Client
# [client|hub] [database|/home/vanessa/.singularity/sregistry.db]
```

It tells us above the active client is Singularity Hub (hub) and the database path
is in our singularity cache. Now, any operations that we do via the 
sregistry tool will update our database. 

## Commands
The following commands are provided with the client for all endpoints, as they pertain to
interaction with the local database.


### Add
Add is primarily acted with from within client "pull" functions, because logically
when a user pulls an image from some endpoint, it would be added to the database. Here we will
show you how to use add, for example, for two use cases:

 1. A local image that you want to add to the sregistry
 2. A url or reference to an image (that doesn't correspond to a local file).

The most common use case for the client "add" function is to assume being given 
an image path and image uri (like `vsoch/hello-world`) with a complete tag/version, and to
save the image file to storage. This operation will look something like this:

```
from sregistry.main import Client as cli

image_path='expfactory-expfactory-master-test.simg'
image_name='expfactory/expfactory-test:master'

container = cli.add(image_path=image_path, image_name=image_name)
Adding expfactory/expfactory-test:master to registry
[container] expfactory/expfactory-test:master
```

The resulting container that is created (and returned) has all attributes that
match to the database fields, for example:

```
container.image
# '/home/vanessa/.singularity/shub/expfactory/expfactory-test:master.simg'
container.id
# 2
container.tag
# 'master'
container.name
# 'expfactory-test'
```

If you are implementing this in a "pull" function for a specific client, you would
probably want to return the final `container.image` (the path for usage). You
might, before the call to add, also have other calls to make, and metadata to add:

```
url = 'myservice.com/containers/1'

# Use cli.download to download file from a url
image_path = self.download(...)

# Retrieve metadata and some custom image name from a manifest, or a user
metadata = ...
image_name = ...

# Then create the container, providing all of the above
container = cli.add(image_path=image_path, 
                    image_name=image_name,
                    metadata=metadata,
                    url=url)
```

If you don't have or want to download the file at all (if you are implementing a client
that simply keeps a record of an external or remote resource) then skip the steps to 
download the image.

```
container = cli.add(image_name=image_name, url=url)
# (you can still provide metadata if you like)
```

And if you take this approach, it would be recommended to implement the "get" function
for your client, so when the user calls "get" it does an actual retrieval action of
the particular image to return a path on the machine (Note that images in storage would
just return the path to the image).

For any of the above, regardless of providing an image path or not, you can set the 
variable save to False and a record will be added to the database **without** moving
the image into storage.

```
container = cli.add(image_name=image_name, url=url, save=False)
```

If you need examples for using add, see the `add.py` scripts in the `sregistry/main/hub` and `sregistry/main/registry` folders.

By default, images that you pull (or otherwise interact with) are brought to your local storage, the Singularity cache. This behavior can change if you've defined your cache to be elsewhere, or specified a different database location.


### Get
STOPPED HERE - need to write these functions. GET should return the image from storage, and if not in storage, a uri to download.

### List
LIST needs to (somehow) be untangled from listing a remote endpoint.

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
