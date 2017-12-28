---
layout: default
title: Getting Started Developers
pdf: true
permalink: /developers
toc: false
---

# SRegistry Global Client for Developers

This walkthrough will show interaction with the Singularity Registry Global client from within Python. This is what you would be interested in if you want to integrate the client into your own applications. If you are interested in steps to develop a new integration endpoint, read about [that here](/sregistry-cli/contribute-client).

## Environment variables
If you recall from the [getting started](/sregistry-cli), sregistry will help you to manage
a local database, and the settings are determined by environment variables. We can
check the defaults that are set from within python. Here is what we see if there are
no special variables exported. These commands are from the terminal after installing
`sregistry` on the host:

```
# Here we see the default client is Singularity Hub when no environment is set
python -c "from sregistry.main import Client; print(Client.client_name)"
hub


# Now we set the client to be Singularity Registry
SREGISTRY_CLIENT=registry python -c "from sregistry.main import Client; print(Client.client_name)"
registry

# We see the registry database is defined
python -c "from sregistry.main import Client; print(Client.database)"
sqlite:////home/vanessa/.singularity/sregistry.db

# Now we see that the registry database is disabled, the attribute doesn't even exist
SREGISTRY_DISABLE=true python -c "from sregistry.main import Client; print(hasattr(Client,'database'))"
False
```

You should also remember that you can also customize the database location with `SREGISTRY_DATABASE` or (if applicable) your client secrets file `SREGISTRY_CLIENT_SECRETS`. So if you are wanting to integrate `sregistry` into your application using python functions, you would want to make sure to:

 - ensure the right client is exported, or have a logical entrypoint for the user to do this
 - during development, make sure you do this yourself!

If you are interested in the logic for the environment settings or have a suggestion for a new setting, you can see the complete list of variables the [sregistry/defaults.py](../../sregistry/defaults.py).


## Shell
To make development easiest for you, we have provided an interactive shell that will
preload a client (given an environment setting). It isn't overly complicated - it just imports the client
as we've shown above. It can be useful, however, for quick testing to see the active 
client and database:

```
sregistry shell
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
>>> client
[client][hub]
```

For the remainder of the tutorial we will enter a standard python (starting from scratch) with the default client running, with Singularity Hub. If you are interested in commands for specific clients, see the [clients](../clients) folder.

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

# Hello client, who are you?
Client.speak()
# [client|hub] [database|/home/vanessa/.singularity/sregistry.db]
```
When you run the client interactively from the command line, he will speak (announce himself as above) for all commands except for get. It tells us above the active client is Singularity Hub (hub) and the database path is in our singularity cache. Now, any operations that we do via the 
sregistry tool will update our database. 

## Commands
We've reviewed these commands before, and will do it again. The following commands are provided with the client for all endpoints, as they pertain to interaction with the local database.

 - *add*: `[local]`: corresponds with adding an image file on your host directly to your registry. Not everything is downloaded from the cloud!
 - *get*: `[local]`: given a uri, return the full path to the image in your storage. A common use case would be to pipe a get command into a singularity command, for example.
 - *images*: `[local]`: list images in your local database, optionally with filters to search.
 - *inspect* `[local]`: prints out an image manifest and metadata retrieved from its endpoint.
 - *rm* `[local]`: is akin to Docker's remove, and says "remove this record from my database, but don't delete the image." This corresponds with deleting the database record, but not the image file in your storage.
 - *rmi* `[local]`: the same as `rm`, but additionally deletes the image file from storage.
 - *shell* `[local]`: want to work with a client interactively? Just shell in and go!


### Add
Add is primarily acted with from within client "pull" functions, because logically
when a user pulls an image from some endpoint, it would be added to the database. But you could
easily use it in your own functions (or implementing a client) to, once you have retrieved an
image in some fashion, add it to the database. There are actually a few interesting use cases, and
some don't even involve a file:

 1. You have a local image (file) that you want to add to the sregistry (storage and database)
 2. You have an image url (that doesn't correspond to a local file) that you want to add to the database (but not storage).

The second is cool, because you could, for example, use `sregistry` to manage image paths on one or more (different!) storage locations, and then use `sregistry` as a common tool to search across them.

**1. Local File**
The most common use case for the client "add" function is to assume being given 
an image path and image uri (like `vsoch/hello-world`) with a complete tag/version, and to
save the image file to storage. For example, I might have a ton of images saved on my computer
that I want to add when I first start using `sregistry`. This operation will look something like this:

```
from sregistry.main import Client as cli

image_path='example:latest.simg'
image_name='vsoch/sregistry-example:v1.0'

container = cli.add(image_path=image_path, image_name=image_name)
[container] vsoch/sregistry-example:v1.0
```

The resulting container that is created (and returned) has all attributes that
match to the database fields, for example:

```
container.image
# '/home/vanessa/.singularity/shub/vsoch/sregistry-example:v1.0.simg'
container.uri
# 'vsoch/sregistry-example:v1.0'
container.tag
# 'v1.0'
container.name
# 'sregistry-example'
container.version
#'b102e9f4c1b2228d6e21755b27c32ed2'
```
Notice how a version magically appeared? This is the hash of the file. If you were to download a container from Singularity Hub, or another resource that maintained these versions, the file hash should match up if you have the same image. Note that the version will only be calculated on the fly given that it isn't provided. Also with the container we have a representation of its collection:

```
container.collection
# <Collection 'vsoch'>
container.collection.name
#'vsoch'
```

And this collection coincides with the folder we keep it under in `SREGISTRY_STORAGE`. It's pretty darn simple.

```
/home/vanessa/.singularity/shub
├── expfactory
│   └── expfactory-master:v2.0.simg
└── vsoch
    ├── hello-pancakes:latest.simg
    ├── hello-world:latest.simg
    └── sregistry-example:v1.0.simg  # we just added him!
```

If you are implementing this in a "pull" function for a specific client, you would
probably want to return the final `container.image`  (the path for usage).

**1. Local File with Metadata**
You might be using the add function in your own custom integration, and you might, before calling "add",  also have other calls to make, and metadata to add. Here is a theoretical workflow for how you can do these calls and add metadata:

```
url = 'myservice.com/containers/1'

# Use cli.download to download file from a url
image_path = cli.download(...)

# Retrieve metadata and some custom image name from a manifest, or a user
metadata = ...
image_name = ...

# Then create the container, providing all of the above
container = cli.add(image_path=image_path, 
                    image_name=image_name,
                    metadata=metadata,
                    url=url)
```

Notice now that we are adding a metadata field, along with a url? This is important because we can go back and further interact with that endpoint. Matter of fact, we can skip storing the image entirely and just keep a record where it is (somewhere on the cloud!) This is our next use case:

**2. Metadata with URL**
Images are fat. Computer hard drives can fill up quickly with fat containers hanging around. You might just want to keep a record of external resources, but not save the image files. If you are using a client that supports this feature for the user (for example, with Singularity Hub you could just save the url to the image and metadata) the client would have implemented an entrypoint to `sregistry record`. This entrypoint (on the backend) is just done via the `add` function, with `save` set to False, and without needing to provide an image file. We will walk through an example here. First, let's grab an image from Singularity Hub by grabbing it's manifest. We first parse the image name:

```
from sregistry.main import Client
from sregistry.utils import *

image = 'vsoch/hello-world'
q = parse_image_name(image, ext='simg')

# q {'collection': 'vsoch',
#    'image': 'hello-world',
#    'storage': 'vsoch/hello-world:latest.simg',
#    'tag': 'latest',
#    'uri': 'vsoch/hello-world:latest',
#    'version': None}
```

and then form the url, and retrieve it!
```
# Verify image existence, and obtain id
url = "%s/container/%s/%s:%s" %(Client.base, q['collection'], q['image'], q['tag'])
# 'https://www.singularity-hub.org/api/container/vsoch/hello-world:latest'

# Get the manifest, add a selfLink to it
manifest = Client._get(url)
manifest['selfLink'] = url
```

Here is what it looks like, and notice we've added the selfLink for safekeeping.

```
 {'branch': 'master',
 'commit': 'e279432e6d3962777bb7b5e8d54f30f4347d867e',
 'id': 23,
 'image': 'https://www.googleapis.com/download/storage/v1/b/singularityhub/o/singularityhub%2Fgithub.com%2Fvsoch%2Fhello-world%2Fe279432e6d3962777bb7b5e8d54f30f4347d867e%2Fed9755a0871f04db3e14971bec56a33f%2Fed9755a0871f04db3e14971bec56a33f.simg?generation=1508072025589820&alt=media',
 'name': 'vsoch/hello-world',
 'selfLink': 'https://www.singularity-hub.org/api/container/vsoch/hello-world:latest',
 'size_mb': '333',
 'tag': 'latest',
 'version': 'ed9755a0871f04db3e14971bec56a33f'}
```

Now we are going to use the manifest to put together the proper uri for the image, and we will save
this in the database.

```
image_uri = "%s:%s@%s" %(manifest['name'], manifest['tag'], manifest['version'])
# 'vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f'
```

At this point, we could download the image, get a file, and call the Client "add" function to add the entry and file to storage. But since we just want to keep a record of this file, we will call add without any image file.

```
container = Client.add(image_name=image_uri,
                       metadata=manifest,
                       url=manifest['image'])
```

Note that if you put the url to the image download in the manifest (given to variable metadata) it will be found automatically and you don't need to supply the url variable:

```
manifest['url'] = url
container = Client.add(image_name=image_uri,
                       metadata=manifest)
```

### Images
We will sneak in another command here, because right now it is useful! `Client.images()` is a way to list local images in the database, akin to `docker images` in spirit. It's different from functions that interact with remote endpoints (e.g., search) that are implemented on the level of the client. If you take a look at your images now with `Client.images()` you can see the newly added image is classified as remote:

```
 Client.images()
Containers:   [date]   [location]  [client]	[uri]
1  December 27, 2017	local 	   [hub]	vsoch/hello-pancakes:latest@22aa66e0c80847c676f34f35e70ea066
2  December 27, 2017	local 	   [hub]	expfactory/expfactory-master:v2.0@03c1ab08e58c6a5101bc790cd9836d25
3  December 27, 2017	local 	   [hub]	vsoch/sregistry-example:v1.0@b102e9f4c1b2228d6e21755b27c32ed2
4  December 27, 2017	remote	   [hub]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f

#
[<Container 'vsoch/hello-pancakes:latest'>,
 <Container 'expfactory/expfactory-master:v2.0'>,
 <Container 'vsoch/sregistry-example:v1.0'>,
 <Container 'vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f'>]

# search just for it
Client.images('hello-world')
Containers:   [date]   [location]  [client]	[uri]
1  December 27, 2017	remote	   [hub]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
# [<Container 'vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f'>]
```

The data structure above returned is a list of containers, although the command is generally used from the main client to print the formatted list for the user.

If you take this approach, it would be recommended to implement the "get" function
for your client, so when the user calls "get" it does an actual retrieval action of
the particular image to return a path on the machine (Note that by default, if you don't implement a custom get, images that are remote would
just return the path to the image). If you have another default behavior you think we should implement instead, [please let us know](https://www.github.com/singularityhub/sregistry-cli/issues)! If you need examples for using add or record, look into the [hub](../../sregistry/main/hub) or [registry](../../sregistry/main/registry) client folders.


### Get
A "get" will work to point you to an image that you have in storage, or an image url that you need to pull. It will use the same logic to parse your requested name as is used to save an image, so you should be as specific as needed. For example, let's do a "get" for the image we added above.

```
from sregistry.main import Client
Client.get('vsoch/hello-world')

https://www.singularity-hub.org/api/container/vsoch/hello-world:latest
<Container 'vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f'>
```

It printed for us a url since this is a remote container, and it returned the container object to work with. Remote is determined because `container.image` is None. If we try to get an image that does have a file, we are returned a path to the file.

```
/home/vanessa/.singularity/shub/vsoch/hello-pancakes:latest.simg
<Container 'vsoch/hello-pancakes:latest'>
```

## Inspect
To inspect within the client, you could use a "get" and then look at the returned object. You can also use the client's inspect function:


```
from sregistry.main import Client
Client.inspect('vsoch/hello-world')
https://www.singularity-hub.org/api/container/vsoch/hello-world:latest
{
    "client": "hub",
    "collection": "vsoch",
    "collection_id": 1,
    "created_at": "2017-12-27 18:03:26",
    "id": 6,
    "image": null,
    "metrics": {
        "branch": "master",
        "commit": "e279432e6d3962777bb7b5e8d54f30f4347d867e",
        "id": 23,
        "image": "https://www.googleapis.com/download/storage/v1/b/singularityhub/o/singularityhub%2Fgithub.com%2Fvsoch%2Fhello-world%2Fe279432e6d3962777bb7b5e8d54f30f4347d867e%2Fed9755a0871f04db3e14971bec56a33f%2Fed9755a0871f04db3e14971bec56a33f.simg?generation=1508072025589820&alt=media",
        "name": "vsoch/hello-world",
        "selfLink": "https://www.singularity-hub.org/api/container/vsoch/hello-world:latest",
        "size_mb": "333",
        "tag": "latest",
        "version": "ed9755a0871f04db3e14971bec56a33f"
    },
    "name": "hello-world",
    "tag": "latest",
    "uri": "vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f",
    "url": "https://www.singularity-hub.org/api/container/vsoch/hello-world:latest",
    "version": "ed9755a0871f04db3e14971bec56a33f"
}
```

Since this is a Singularity Hub image, we have stored with it the metadata from Singularity Hub, along with the output from the Singularity inspect.


## Remove
Finally, the same remote functions are available to remove an image from the database record (rm) but **not** the container
in storage (`rm`) or delete the database record **and** theimage (`rmi`). That looks like this:

```
from sregistry.main import Client
Client.rm('vsoch/hello-world')

# or
Client.rmi('vsoch/hello-world')
```

The first example removes the image from the database (but not the file) and the second removes the
file from storage and the image.

## Your Ideas Appreciated!
Here is a general list of thoughts and ideas that I'd be interested in feedback on. I will discuss pros and cons of each idea.

 - Can we put some kind of watcher on the file? so when it moves or changes, the database updates? The pro of this is a database that reacts to changes in storage, or manually. This would also make it possible to have a registry on the local file system, and know when an image is moved. The huge con is that it won't work on most cluster filesystems that don't have inotify.
 - Given the above (or not) should the user be allowed to store images around the filesystem, wherever he/she pleases? This seems messy to me and I haven't thought of rationale to support it, given that the organized manner is (in my mind) more consistent and dependable.
 - What kind of weirdness happens if a Singularity Registry uses that cache for its storage?
 - How do (or should) we update the database if a previously existing image is gone (meaning manual removal). Should we clean up, or just give a warning?
 - The user should have GLOBAL functions to:
   - remove all images (or database records)
   - clean the database / cache (meaning fixing broken links, etc.)
   - use clients and associated metadata to refresh or update a database (with caution).
 - What happens with shared caches?


<div>
    <a href="/sregistry-cli/"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/commands"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
