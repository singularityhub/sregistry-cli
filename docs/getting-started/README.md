---
layout: default
title: Getting Started
pdf: true
permalink: /getting-started
toc: false
---

# Getting Started

In the pages here we will first review some important concepts about the Singularity
Registry Global (SRG) client, and then provide [install instructions](#install) and [tutorials](#tutorials) for using
the client, both on the command line and from within Python.

 - [Commands](#commands): a general review of the sets of commands found for particular client endpoints.
 - [Database](#database): The SRG client maintains a record of the images you are managing via a local database.
 - [Settings](#settings): Settings are managed via environment variables.
 - [Client](#client): The client itself is a shell that intuitively responds to environment configuration hints to connect you to different storage endpoints.
 - [Endpoints](#endpoints): The endpoints are generally cloud hosted services and storage for images. We push and pull from our local registry to and from endpoints. This means that you can 

## How does Singularity Global Client relate to Singularity?
With Singularity, you can pull images from Singularity Hub, or assemble Docker layers into an image with any of the action commands like run, exec, etc. The Singularity client is ideal for creating and using images. The Singularity Global Client specializes in one particular thing - movement of images. This maps nicely only the "singularity pull" functionality, and there is both overlap and some key differences.

### Overlap
We want the `sregistry` client to support the current workflow of using Singularity images. This means that the local file database created `sregistry` lives alongside the cache folders:

```
tree -L 1 $HOME/.singularity
├── docker
├── shub
└── sregistry.db
```

It also means that when you interact with a storage endpoint using Singularity registry, it will honor your Singularity cache folder. This means that if you use sregistry to manage images, when you run Singularity proper those images will be found.

### Differences
You can best think of the `sregistry` client as an extension to Singularity, one that adds a layer of organization to images that live on your system. It fits the niche of the local user, whether on his personal machine or home node on a cluster, to be able to move images between common places, search, and generally manage them. A few additional keys points:

 - the `sregistry` client, in that it can be served from a Singularity image, has many fewer constraints to the modules that can be installed. For example, instead of using older python libraries for web requests that are supported on the oldest operating systems, we can use a modern library called `requests`. This makes it much easier for development, and for integration with third party libraries. 
 - the `sregistry` client itself is also internally modular, because each endpoint integration is a submodule. This is great because it means that the user can customize the installation based on needs and preferences. If you don't need a connection to Dropbox or Globus, you don't install them. If a third party wants to add a new integration, the dependencies and code can plug in nicely.

It's entirely up to you how you want to (or don't want to) use `sregistry` clients. If you have a preference for a particular kind of storage, this will be very useful to you. If you want to integrate Singularity into your own software, this will also be useful. 

## Commands
When you start a client, whether it be in an interactive python environment or running
natively on your host **or** via a Singularity container, a client for an endpoint of choice is started up, and this client will give you access, minimally, to a core set of commands:

let you do any or a subset of the following:

### Local
The following commands are considered "local" in that they come with every client, and are specifically created to interact with your local registry (the database and storage).

 - *add*: `[local]`: corresponds with adding an image file on your host directly to your registry. Not everything is downloaded from the cloud!
 - *get*: `[local]`: given a uri, return the full path to the image in your storage. A common use case would be to pipe a get command into a singularity command, for example.
 - *images*: `[local]`: list images in your local database, optionally with filters to search.
 - *inspect* `[local]`: prints out an image manifest and metadata retrieved from its endpoint.
 - *rm* `[local]`: is akin to Docker's remove, and says "remove this record from my database, but don't delete the image." This corresponds with deleting the database record, but not the image file in your storage.
 - *rmi* `[local]`: the same as `rm`, but additionally deletes the image file from storage.
 - *shell* `[local]`: want to work with a client interactively? Just shell in and go!

These specific commands are [demonstrated with more examples](/sregistry-cli/commands).

### Client (remote)
This next set of commands, while they interact with local resources, are primarily implemented by the specific clients. For example, a pull from Singularity Hub is going to have particular commands using the Singularity Hub API.

 - *delete*: `[remote]`: delete an image from a remote endpoint. You likely will need some kind of credential.
 - *pull*: `[remote->local]` is a common use case. It says "there is this image somewhere remote and I want to pull it from there to my local host."
 - *push*: `[local->remote]` takes an image in your local resource and puts it in some remote one.
 - *record*: `[remote->local]` obtain metadata and image paths for a remote image and save to the database, but don't pull the container to storage.
 - *search*: `[remote]`: list containers for a remote endpoint, optionally with a search term.

Each of these commands will be detailed with examples in the various [client walkthroughs](/sregistry-cli/clients), and if you are implementing an endpoint, there are also details about how you should "fill in the space" to
implement your custom client.

## Database
By default, using sregistry will help you manage a local database 
of images for personal use. This is an sqlite3 database, so you should
not use it for scaled write operations - you would use sregistry to push
pull, search, and then run scaled operations with singularity proper
with the path from sregistry. If you need to manage images at scale, you should
consider hosting a [Singularity Registry](https://www.singularityhub.github.io/sregistry) 
or building on [Singularity Hub](https://www.singularity-hub.org).


### Storage
The database itself stores metadata and paths for images. You can imagine pulling an image, perhaps that looks like this:

```
sregistry pull shub://vsoch/hello-world
```

and then you would want to be able to search your local database, and find the image.

```
sregistry search vsoch/hello-world
```

On the back end, this means that we are storing (minimally) some path, and metadata about the image. But where does the image actually live?

 - The "where" depends on the kind of integration you are working with. If you pull the image, it will be a path on your file system.
 - SRegistry can promise that, given that you retrieve an image using it, it will organize and keep images in your singularity cache (or another location you've specified).
 - If you manually go in and remove an image, the database cannot know. However when you try to retrieve the image, a best effort will be taken to fix the manual change. For example, a record is kept of the url and associated method used to get the image, and it will redo this operation if not found. With the strategy, you can delete the files in your cache and re-create your database by downloading them again.


## Settings
The sregistry client is driven by environment variables. Since each call is quick, you can have a lot of power to switch between endpoints and clients just by way of changing an environment variable for the call. We will review the most important defaults, and then a robust list of all that you can set. 

### Environment Variable Defaults
The database path, an sqlite3 file, is determed based on the environment variable
`SREGISTRY_DATABASE`. If not found, it will be written to our singularity cache
folder, which is usually in our `$HOME`.

```
SREGISTRY_DATABASE
/home/vanessa/.singularity/sregistry.db
```

For storage of images, we use the same folder that Singularity will by default look for the cache.

```
SREGISTRY_STORAGE
/home/vanessa/.singularity/shub
```

And for either, if you want to change these locations you can export the variables. There is no
reason that the database file needs to live next to the image folder, for example, and you might
want to give it a unique name to a user, depending on your setup.

If you have exported the variable `SINGULARITY_DISABLE_CACHE`, an option with
the Singularity command line software to not cache anything, SRegistry will honor
this and not maintain a database. If you want to keep the cache but just disable
the SRegistry database, then export `SREGISTRY_DISABLE=yes`.


### Environment Variables Lists
The `sregistry` client exposes a lot of customization through environment variables, so you as the user have the power to configure it exactly as you need, or stick to defaults that are reasonably set. In these sections, we will review the sets of environment variables for you to use. If you are a developer, see our [client contribution guide](/sregistry-cli/contribute-client) for details on interacting with these environment variables.


#### Database and Storage
The database refers to the sqlite3 file used to store metadata, typically in the user's home, and the storage refers to the actual folder of images. You can control this behavior with the following environment variables.

 - *SREGISTRY_CLIENT*: Set the client (either as an export or runtime) to determine which endpoint you want to use. By default, Singularity Hub is used, and functions that are available for all commands (detailed in this section and also reviewed under [commands](/sregistry-cli/commands) are available.
 - *SREGISTRY_SHELL*: When you use `sregistry shell` it will default to looking for python, bpython, and then ipython. If you have preference for one or the other, set this variable. Note that it will persist in your `.sregistry` secrets, so if you change your mind you should set the variable again, or remove it from here.
 - *SINGULARITY_DISABLE_CACHE*: By default, `sregistry` honors your Singularity configuration, meaning that if you have disabled the cache entirely (coinciding with pulling / interacting with images in temporary locations) the `sregistry` client will not use a database or cache. If this variable is found as a derivate of y/yes/true, this means that we simply use the commands as tools to work with images locally.
 - *SREGISTRY_DISABLE*: If for some reason you don't want to disable your Singularity cache but you do want to disable the `sregistry` database and storage, set this to one of y/yes/true.
 - *SREGISTRY_DATABASE*: The `sregistry` has two parts - a database file (sqlite3) and a storage location for the images. This variable should be to a folder where you want the application to live. By default, it will use the same Singularity cache folder (`$HOME/.singularity`), meaning that you would find the database at `$HOME/.singularity/sregistry.db` alongside your docker, metadata, and shub folders.
 - *SREGISTRY_PYTHON_THREADS*: the number of threads to allocate to the worker (if used, typically is useful for download of layers). Defaults to 9.
 - *SREGISTRY_STORAGE*: The storage of images is **drumroll** exactly the same as your Singularity cache for Singularity images! If your `SREGISTRY_DATABASE` is set to `$HOME/.singularity`, then the storage goes into `$HOME/.singularity/shub`. The one difference is that with `sregistry` we create a folder one level up that coincides with the collection name. For example:


```
tree $HOME/.singularity.shub

/home/vanessa/.singularity/shub/
├── expfactory
│   └── expfactory-master:v2.0.simg
└── vsoch
    ├── hello-pancakes:latest.simg
    └── hello-world:latest.simg
```

The organization is trivial for `sregistry` because images are interacted with via uri (unique resource identifier). This is also a way to distinguish images that you have pulled via Singularity into the cache (and aren't in your database) from those retrieved with `sregistry`, and organized and present in the database. For future versions of Singularity it would be ideal to give the user an option to add images in this format (and possibly add to the database, if the integration is available).

#### Credentials and Settings
Credentials broadly refer to tokens and secrets (authentication and refresh tokens, for example) needed by various clients to authenticate you to their services. The `sregistry` client has two storage strategies for handling credentials and settings.

 - [SREGISTRY_CLIENT_SECRETS](#): is a file that is accessible to all clients, and is indexed by the client name (e.g., `google-storage`. This is a file where you can expect to keep parameters for different clients, and likely details about these settings are provided in the [client documentation](/sregistry-cli/clients). This is also where, if you manage or use a singularity registry, you are instructed to keep your token. The default location of this json file is at `$HOME/.sregistry`, and if you want to change that, simply define this variable. If you don't use or host a registry and the default location is good, you don't need to set this variable.
 - [SREGISTRY_DISABLE_CREDENTIAL_CACHE](#): if you want to disable caching credentials entirely, meaning that you will not take advantage of refresh tokens (not recommended) you can export this variable as some derivative of yes/y/true. Note that an alternative would be to use the client as you need, and then manually delete the file.
 - [SREGISTRY_DISABLE_CREDENTIAL_<client>](#): It might be the case that you want to disable credential caching on a per-client basis. To do this, just export the variable above with the client that you want to disable.
 - [SREGISTRY_CREDENTIALS_CACHE](#) By default, we use the database folder (`SREGISTRY_DATABASE`) as the credentials cache folder, and create a subfolder `.sregistry` in it for the client-specific credential files. This means that, by default, the `google-drive` client would use the file `$HOME/.singularity/.sregistry/google-drive` for it's refresh tokens, and the path `$HOME/.singularity/.sregistry` is the default path that you can override with `SREGISTRY_CREDENTIALS_CACHE`. If you are ok with the defaults, there is no need to set this.

## Client
Each client might have slight variability in the functions that it supports. For example,
you can push to a Singularity Registry that you have credentials for, but you can't push
to Singularity Hub directly. We will discuss clients at a high level here. When you
use the client, whether from within Python or command line:

 1. The environment is parsed for `SREGISTRY_CLIENT`. If it's found, then you have specified a particular client to use and that choice is honored.
 2. If a specified client is not declared, then we step through looking for client-specific exports. Finding a path to a `SREGISTRY_CLIENT_SECRETS` for example means it is likely you want to interact with a Singularity Registry, so the client is loaded.
 3. If no environment variables can be determined, the default client is optimized to work with Singularity Hub.

In all cases, after we create a client, given that we have not disabled it, a local database is generated or connected to:

```
from sregistry.main import Client
# Database: /home/vanessa/.singularity/sregistry.db
```

And following this step, operations that we do across all clients interact with our local database.

## Endpoints
An endpoint is a remote place to put or get images. It could be Singularity Hub (pulling images from Google Cloud Storage), Dropbox (saving and retrieving images from a personal Dropbox) or Globus (moving images to and from endpoints that you control). You might even host one of these endpoints locally, so for the purposes of the client, just remember that it will interact with both your hosted endpoints and others (with appropriate permissions).

## Install
The most tested approach has been to install `sregistry` in your local python using pip, or from Github:

```
pip install sregistry
```
```
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli
python setup.py install
```

If you need to install dependencies for a particular client, just provide the name:

```
pip install -e .[google-storage]
```

## Tutorials

Now that we've discussed these concepts, let's jump into using the client. We have two getting started guides:

 - [command-line](/sregistry-cli/commands): a getting started for command line use of the client.
 - [developers](/sregistry-cli/developers): a getting started for developers that want to interact with the client from within Python.

Once you've mastered the basics, take a look at the [specific clients documentation](/sregistry-cli/clients)

<div>
    <a href="/sregistry-cli/"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/commands"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
