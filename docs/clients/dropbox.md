---
layout: default
title: Dropbox Client
pdf: true
permalink: /client-dropbox
---


# SRegistry Client: Dropbox
These sections will detail use of the Dropbox client for `sregistry`, meaning that you can push, pull, and otherwise interact with containers on your personal Dropbox. 

## Getting Started
Dropbox has one dependency to install it's python sdk. You can do this via sregistry:


```
pip install sregistry[dropbox]
```

or on your own:

```
pip install dropbox
```

or read [instructions here](https://github.com/dropbox/dropbox-sdk-python).

And if you haven't, you should install the `sregistry` client either from pypi or source:

```
pip install sregistry

# or from source
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli 
python setup.py install
```

To make the Dropbox client default, you **must** set `SREGISTRY_CLIENT` to `dropbox`, either for individual commands or exported globally:

```
# Globally
SREGISTRY_CLIENT=dropbox
export SREGISTRY_CLIENT

# Single Command
SREGISTRY_CLIENT=dropbox sregistry shell
```

### Environment
Singularity Registry Global Client works by way of obtaining information from the environment, which are cached when appropriate for future use. For Dropbox, we have defined the following environment variables (and defaults).

| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SREGISTRY_DROPBOX_TOKEN  | None (required)        | Your API token associated with your account, generated [here](https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account)|

The following variables are *shared* between different `sregistry` clients that have a Docker registry backend. The following variables are relevant for clients that use multiprocessing:

| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SREGISTRY_PYTHON_THREADS       | 9          | The number of workers (threads) to allocate to the download client |


The following variables are specific to Singularity (not the Singularity Registry Global Client) and honored during any pull of Docker layers:

| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SINGULARITY_CACHEDIR  | `$HOME/.singularity`           | Set the root of the cache for layer downloads |
|SINGULARITY_DISABLE_CACHE  | not set               | Disable the Singularity cache entirely (uses temporary directory) |

More details about how to generate and export the token are discussed in the next section.

#### Authentication

To use the Dropbox client, you must have an access token exported in the environment. The access token is personal and for your account only, and so it is essential that you don't share it with anyone. When you go to your [apps page](https://www.dropbox.com/developers/apps/) and create an application, make sure that you click the button to reveal a code under "Generated access token." Then export your secret token for the api:

```
SREGISTRY_DROPBOX_TOKEN = "xxxxxx"
export SREGISTRY_DROPBOX_TOKEN
```

After you connect, you will receive a notification (or see in your Dropbox) a new folder created. For the development and testing, I used a folder that wasn't mapped to my machine, so I received a notification in my browser, and saw the folder in the web interface:

![/sregistry-cli/img/dropbox-folder.png](/sregistry-cli/img/dropbox-folder.png)

Notice how it's under the "Apps" folder? This is good to know - because it means that the application permission is scoped to be within that folder. The client cannot touch the rest of your Dropbox.

## Commands
For a detailed list of other (default) environment variables and settings that you can configure, see the [getting started](sregistry-cli/getting-started) pages.  For the globally shared commands (e.g., "add", "get", "inspect," "images," and any others that are defined for all clients) see the [commands](/sregistry-cli/commands) documentation. Here we will review the set of commands that are specific to the Docker client:

 - [push](#push): `[local->remote]` push a local image to the `sregistry` Apps folder in your personal Dropbox
 - [pull](#pull): `[remote->local]` pull layers from Docker Hub to build a Singularity images, and save in storage.
 - [record](#record): `[remote->local]` obtain metadata to save to the database, but don't pull the container.
 - [search](#search): `[remote]` search your personal Dropbox for a container
 - [share](#share): `[remote]`: share a remote container, meaning returning a share link

For all of the examples below, we will export our client preference to be `dropbox`

```
SREGISTRY_CLIENT=dropbox
export SREGISTRY_CLIENT
```

but note that you could just as easily define the variable for one command (as we did above):

```
SREGISTRY_CLIENT=dropbox sregistry shell
```

A good test for viewing the client is to use shell, as above, and confirm that you see `[client|dropbox]`

```
sregistry shell
[client|dropbox] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
```

## Push
When you first use the client, you won't have any Singularity images in your personal Dropbox. You thus should push one there first! Push looks like this:

```
sregistry push --name dropbox://pusheen/asaurus:blue library-busybox-latest.simg 
[client|dropbox] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
connected to Vanessa S
Progress |===================================| 100.0% 
```

The third line confirms the name of the dropbox that we are connecting to. Notice how we have the dropbox uri (`dropbox://`) to tell the client to use Dropbox? If you plan to use this for a session (or want to set it globally) you can also export `SREGISTRY_CLIENT` as `dropbox` to the environment, and then drop the uri entirely.

```
export SREGISTRY_CLIENT=dropbox
sregistry push --name pusheen/asaurus:pink library-busybox-latest.simg 
[client|dropbox] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
connected to Vanessa S
Progress |===================================| 100.0% 
```

What is actually going on, organization wise? Your dropbox folder has an "Apps" section, and within it are individual folders, one per application (and one for sregistry!). When you push an image in collection "pusheen," a collection folder is made under `sregistry/` and then within that folder, you will have your images. It would look like this:

```
Apps

├── sregistry
│   ├── pusheen
│   │   ├── asaurus:blue
│   │   ├── asaurus:green
│   │   └── asaurus:red
│   └── vsoch
│       └── hello-world:tacos
│
├── ...
```

## Search
Once you've pushed a few images, we can search! Without a query, your search is akin to a listing of remote images.

```
sregistry search
[client|dropbox] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
connected to Vanessa S
Collections
1  vsoch/hello-world:tacos
2  pusheen/asaurus:green
3  pusheen/asaurus:red
4  pusheen/asaurus:blue
```

## Pull
After you have some images remotely, you might want to pull them (for example, if you build on your local machine, and then want to pull the images to your cluster).  You can use sregistry with the dropbox:// uri to do this.

```
sregistry pull dropbox://pusheen/asaurus:red
[client|dropbox] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
connected to Vanessa S
Progress |===================================| 100.0% 
[container][new] pusheen/asaurus:red
Success! /home/vanessa/.singularity/shub/pusheen-asaurus:red.simg
```
Note that the final path is in your storage registry. You can get it (and pipe into commands, variables, etc.)

```
sregistry get pusheen/asaurus:red
/home/vanessa/.singularity/shub/pusheen-asaurus:red.simg
```
What if we try to pull the same image again?

```
sregistry pull dropbox://pusheen/asaurus:red
[client|dropbox] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
connected to Vanessa S
ERROR Image exists! Remove first, or use --force to overwrite
```

We need to use force to force overwrite.

```
sregistry pull --force dropbox://pusheen/asaurus:red
[client|dropbox] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
connected to Vanessa S
Progress |===================================| 100.0% 
[container][update] pusheen/asaurus:red
Success! /home/vanessa/.singularity/shub/pusheen-asaurus:red.simg
```

We can then see the images (tags red and blue) have been added to our local database:

```
sregistry images | grep dropbox
30 January 28, 2018	local 	   [dropbox]	pusheen/asaurus:blue@02c08a25c8f4697e16e896239e549a2b
31 January 28, 2018	local 	   [dropbox]	pusheen/asaurus:red@02c08a25c8f4697e16e896239e549a2b
```

## Record
We can do the same action as above, but without the download! You might want to grab metadata for an image but not pull the file itself. You can use record for that. Let's first get the record for another version of the pusheen green image:

```
sregistry record pusheen/asaurus:green
[client|dropbox] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
connected to Vanessa S
[container][new] pusheen/asaurus:green
```

It's a really quick action, because all we've done is obtained the file metadata. If you do it a second time, you
update the existing record:

```
sregistry record pusheen/asaurus:green
[client|nvidia] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container][update] pusheen/asaurus:green
```

## Images
We can see the record as a "remote" in our images list:

```
 sregistry images | grep dropbox
30 January 28, 2018	local 	   [dropbox]	pusheen/asaurus:blue@02c08a25c8f4697e16e896239e549a2b
31 January 28, 2018	local 	   [dropbox]	pusheen/asaurus:red@02c08a25c8f4697e16e896239e549a2b
32 January 28, 2018	remote	   [dropbox]	pusheen/asaurus:green
```

## Inspect
And we can inspect it!

```
sregistry inspect pusheen/asaurus:green
[client|nvidia] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
nvidia/caffe2:17.10
https://nvcr.io/v2/nvidia/caffe2/manifests/17.10
{
    "client": "nvidia",
    "collection": "nvidia",
    "collection_id": 6,
    "created_at": "2018-01-15 15:33:30",
    "id": 16,
    "image": null,
    "metrics": {
        "1": {
            "architecture": "amd64",
            "fsLayers": [
                {
                    "blobSum": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4"
                },
               ...

                {
                    "digest": "sha256:7afe52ea9cb6a8875fc3c865ad45869cbed901580aa530b64031badf99e4c645",
                    "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                    "size": 954
                }
            ],
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "schemaVersion": 2,
            "selfLink": "https://nvcr.io/v2/nvidia/caffe2/manifests/17.10"
        },
        "selfLink": "https://nvcr.io/v2/nvidia/caffe2/manifests"
    },
    "name": "caffe2",
    "tag": "17.10",
    "uri": "nvidia/caffe2:17.10",
    "url": "https://nvcr.io/v2/nvidia/caffe2/manifests/17.10",
    "version": ""
}
```

the above is truncated in the middle, but what you should know is that the middle chunk contains both versions of the manifest, if available.

## Get
And then to use (or otherwise interact with the image via it's path in your local database) you can use get. Notice the different between performing a get for a remote image (returns the url):

```
sregistry get nvidia/caffe2:17.10
https://nvcr.io/v2/nvidia/caffe2/manifests/17.10
```

and one that we have in our local storage (returns a full path to it)

```
sregistry get nvidia/tensorflow:17.11@16765f12b73ec77235726fa9e47e808c
/home/vanessa/.singularity/shub/nvidia-tensorflow:17.11.simg
```

All of these functions are also available to interact with via the python client, if you are a developer.

```
sregistry shell
[client|nvidia] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Python 3.5.2 |Anaconda 4.2.0 (64-bit)| (default, Jul  2 2016, 17:53:06) 
Type "copyright", "credits" or "license" for more information.

IPython 5.1.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.

In [1]: client.get('nvidia/caffe2:17.10')
https://nvcr.io/v2/nvidia/caffe2/manifests/17.10
Out[1]: <Container 'nvidia/caffe2:17.10'>
```


 It will give you an interactive shell with the Dropbox client active. If you run a shell and **don't** see that dropbox is the active client, it's not active.
And finally, for commands that are relevant for an image, you can just use the dropbox uri:

```
sregistry pull dropbox://vanessa/pancakes
```

## Shell
After we have exported `SREGISTRY_CLIENT` above, if you are looking to interact with a shell for interacting with your Dropbox client `sregistry` client, just ask for it:

```
[client|dropbox] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Python 3.5.2 |Anaconda 4.2.0 (64-bit)| (default, Jul  2 2016, 17:53:06) 
Type "copyright", "credits" or "license" for more information.

IPython 5.1.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.

In [1]:
```

If you **don't** see dropbox as the client, stop, go back, and make sure to export the environment variable.



<div>
    <a href="/sregistry-cli/client-docker"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-storage"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
