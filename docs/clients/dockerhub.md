---
layout: default
title: Docker Hub Client
pdf: true
permalink: /client-dockerhub
toc: false
---

# SRegistry Client: Docker Hub

These sections will detail use of the Docker Hub client for `sregistry`, which is a connection to the default Docker Hub API. 

## Why would I want to use this?
Singularity proper will be the best solution if you want to pull and otherwise interact with Docker images. However, under the circumstance that you want additional behavior or features not yet implemented in Singularity:

 - you have credentials at `$HOME/.docker/config.json` you want to utilize
 - you want to use a private hosted (or otherwise different) registry endpoint 

To quicky review, using this client (for pull) you will do the following:

 1. obtain image manifests from Docker Hub based on an image unique resource identifier (uri) e.g., `ubuntu:latest`
 2. download layers into a sandbox, and build a squashfs image from the sandbox (per usual with Singularity, build is recommended to do using sudo)
 3. add the image to your local storage and sregistry manager so you can find it later.

The "images" from Docker Hub are layers, and the layers that you obtain depend on the uri that you ask for, along with the host architecture and operating system. See the [environment](#environment). setting for more details.


## Getting Started
The Docker Hub module does not require any extra dependencies other than having Singularity on the host.

To get started, you simply need to install the `sregistry` client:

```
pip install sregistry

# or from source
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli 
python setup.py install
```

The next steps we will take are to first set up authentication and other environment variables of interest, and then review the basic usage.

### Environment
Singularity Registry Global Client works by way of obtaining information from the environment, which are cached when appropriate for future use. For Docker Hub, we have defined the following environment variables (and defaults).


| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SREGISTRY_DOCKERHUB_SECRETS  | None           | The path to your `.docker/config.json` credentials (if you want to use it) |
|SREGISTRY_DOCKERHUB_USERNAME | None           | login username to Docker Hub. If set, will override the secrets file |
|SREGISTRY_DOCKERHUB_PASSWORD | None           | the login password to Docker Hub. If set, will override the secrets file |
|SREGISTRY_DOCKERHUB_NOHTTPS | not set        | If found as yes/t/true/y or some derivation, make calls without https (usually for local registries and not recommended)  
|SREGISTRY_DOCKERHUB_VERSION  |  v2            | the Docker Hub API version to use |

The following variables are relevant for clients that use multiprocessing:

| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SREGISTRY_PYTHON_THREADS       | 9          | The number of workers (threads) to allocate to the download client |


The following variables are *shared* between different `sregistry` clients that have a Docker registry backend.


| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SREGISTRY_DOCKER_OS       | linux          | The choice of operating system to use from the schema version 2 image manifest |
|SREGISTRY_DOCKER_ARCHITECTURE| amd64       | the system architecture to use from the schema verison 2 image manifest
|SREGISTRY_DOCKER_CMD |     not set         | If found as yes/t/true/y or some derivation, use "CMD" instead of "EntryPoint" for container runscript|


The following variables are specific to Singularity (not the Singularity Registry Global Client) and honored during a Docker Hub pull:

| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SINGULARITY_CACHEDIR  | `$HOME/.singularity`           | Set the root of the cache for layer downloads |
|SINGULARITY_DISABLE_CACHE  | not set               | Disable the Singularity cache entirely (uses temporary directory) |


#### Authentication
You will notice in the above table that you have multiple options for authenticating with Docker Hub. We recommend that you use the standard docker credential file (generated with `docker login` that is usually located at `$HOME/.docker/config.json` with your secrets token. To do this:

 1. `docker login` to generate the file (if it doesn't exist)
 2. export `SREGISTRY_DOCKERHUB_SECRETS` to be the path to this file

As an alternative option, you can also choose to export your username and password, and the client will do the same to base64 encode them (this is the token in the docker config file. Whatever you choose, we do not send your username and password out in the open beyond the client (or cache it anywhere) but instead generate a base64 encoded string to pass with the header to identify you and ask for a token. **Important** `sregistry` will not cache or otherwise save any of your credential information to the `.sregistry` secrets. This information must be set in the environment (either the path to the file or username and password) for each usage of the client.

## Commands
For a detailed list of other (default) environment variables and settings that you can configure, see the [getting started](../getting-started) pages.  For the globally shared commands (e.g., "add", "get", "inspect," "images," and any others that are defined for all clients) see the [commands](../getting-started/commands.md) documentation. Here we will review the set of commands that are specific to the `sregistry` Docker Hub client.

 - [pull](#pull): `[remote->local]` pull layers from Docker Hub to build a Singularity images, and save in storage.
 - [record](#record): `[remote->local]` obtain Docker Hub manifests and metadata to save to the database, but don't pull layers to build a container.

For all of the examples below, we will export our client preference to be `dockerhub`

```
SREGISTRY_CLIENT=dockerhub
export SREGISTRY_CLIENT
```
but note that you could just as easily define the variable for one command:

```
SREGISTRY_CLIENT=dockerhub sregistry shell
```

## Shell
After we have exported `SREGISTRY_CLIENT` above, if you are looking to interact with a shell for the Docker Hub `sregistry` client, just ask for it:

```
sregistry shell
[client|dockerhub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Python 3.5.2 |Anaconda 4.2.0 (64-bit)| (default, Jul  2 2016, 17:53:06) 
Type "copyright", "credits" or "license" for more information.

IPython 5.1.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.

In [1]: client.speak()
[client|dockerhub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
```


## Pull
The most likely action you want to do with a Docker Hub endpoint is to pull. Pull in this context is different than a pull from Singularity Registry, because we aren't pulling an entire, pre-built image - we are assembling layers at pull time and building an image with them. Specifically we:

 1. **obtain image manifests from Docker Hub** based on an image unique resource identifier (uri) e.g., `ubuntu:latest`. Currently, the image manifests we look for are schemaVersion 1 and 2. Version 1 has important metadata relevant to environment, labels, and the EntryPoint and Cmd (what Singularity will use as the runscript). Version 2 has sizes for layers, and in some cases returns a list of manifests that the user (you!) can choose based on selecting an operating system and system architecture. If you do a simple record (and not pull) it's these manifests that will be obtained and stored in your database.
 2. **download layers into a sandbox** and build a squashfs image from the sandbox (per usual with Singularity, build is recommended to do using sudo). The client will detect if you are running the command as sudo (user id 0) and adjust the command to singularity appropriately.
 3. **add the image** to your local storage and sregistry manager so you can find it later.

If you are interested in seeing how to ask for a particular architecture or operating system (given that the image provides it) please see the [environment](#environment). setting for more details. Here is an example of using the Docker Hub `sregistry` client.

```
sregistry pull ubuntu:latest
[client|dockerhub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Exploding /usr/local/libexec/singularity/bootstrap-scripts/environment.tar
Exploding /home/vanessa/.singularity/docker/sha256:50aff78429b146489e8a6cb9334d93a6d81d5de2edc4fbf5e2d4d9253625753e.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:f6d82e297bce031a3de1fa8c1587535e34579abce09a61e37f5a225a8667422f.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:275abb2c8a6f1ce8e67a388a11f3cc014e98b36ff993a6ed1cc7cd6ecb4dd61b.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:9f15a39356d6fc1df0a77012bf1aa2150b683e46be39d1c51bc7a320f913e322.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:fc0342a94c89e477c821328ccb542e6fb86ce4ef4ebbf1098e85669e051ef0dd.tar.gz
Exploding /home/vanessa/.singularity/docker/metadata/sha256:c6a9ef4b9995d615851d7786fbc2fe72f72321bee1a87d66919b881a0336525a.tar.gz
WARNING: Building container as an unprivileged user. If you run this container as root
WARNING: it may be missing some functionality.
Building FS image from sandbox: /tmp/tmpbd78kvnf
Building Singularity FS image...
Building Singularity SIF container image...
Singularity container built: /home/vanessa/.singularity/shub/library-ubuntu:latest.simg
Cleaning up...

[container][new] library/ubuntu:latest
Success! /home/vanessa/.singularity/shub/library-ubuntu:latest.simg
```

Notice that the first layer extracted is the standard environment metadata tar. The next set of layers come from the user's default cache (either set as the Singularity default or a user specified, we honor the Singularity envionment variable settings for this, and use a temporary directory if it's disabled. The final layer is a metadata tar that is specifically for the runscript, environment, and labels (if found in the manifest). After you do a pull, you can see the record in your local database (see the last record):

```
sregistry images
[client|dockerhub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers:   [date]   [location]  [client]	[uri]
1  December 29, 2017	local 	   [google-drive]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
2  December 30, 2017	remote	   [google-storage]	expfactory/expfactory:metadata@846442ecd7487f99fce3b8fb68ae15af
3  December 30, 2017	local 	   [google-storage]	vsoch/avocados:tacos@ed9755a0871f04db3e14971bec56a33f
4  January 01, 2018	local 	   [google-drive]	expfactory/expfactory:master@846442ecd7487f99fce3b8fb68ae15af
5  January 01, 2018	remote	   [google-drive]	vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f
6  January 09, 2018	local 	   [registry]	mso4sc/sregistry-cli:latest@953fc2a30e6a9f997c1e9ca897142869
7  January 14, 2018	local 	   [dockerhub]	library/ubuntu:latest@f8d7d2e9f5da3fa4112aab30105e2fcd
```

## Record
You might want to grab metadata for an image but not pull and download layers. You can use record for that. Let's first get the record for an anaconda image:

```
sregistry record continuumio/anaconda3
[client|dockerhub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container][new] continuumio/anaconda3:latest
```

It's a really quick action, because all we've done is obtained the manifests. We can see the record in our images list:

```
sregistry images
[client|dockerhub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers:   [date]   [location]  [client]	[uri]
1  December 29, 2017	local 	   [google-drive]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
2  December 30, 2017	remote	   [google-storage]	expfactory/expfactory:metadata@846442ecd7487f99fce3b8fb68ae15af
3  December 30, 2017	local 	   [google-storage]	vsoch/avocados:tacos@ed9755a0871f04db3e14971bec56a33f
4  January 01, 2018	local 	   [google-drive]	expfactory/expfactory:master@846442ecd7487f99fce3b8fb68ae15af
5  January 01, 2018	remote	   [google-drive]	vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f
6  January 09, 2018	local 	   [registry]	mso4sc/sregistry-cli:latest@953fc2a30e6a9f997c1e9ca897142869
7  January 14, 2018	local 	   [dockerhub]	library/ubuntu:latest@f8d7d2e9f5da3fa4112aab30105e2fcd
8 January 14, 2018	remote	   [dockerhub]	continuumio/anaconda3:latest
```

Since we didn't ask for an image, the record just records the uri without a version. What did we get? let's inspect it.

```
sregistry inspect continuumio/anaconda3:latest
[client|dockerhub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
continuumio/anaconda3:latest
{
    "client": "dockerhub",
    "collection": "continuumio",
    "collection_id": 5,
    "created_at": "2018-01-14 22:08:41",
    "id": 10,
    "image": null,
    "metrics": {
        "1": {
            "architecture": "amd64",
            "fsLayers": [
                {
                    "blobSum": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4"
                },
                ...

            ],
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "schemaVersion": 2,
            "selfLink": "https://index.docker.io/v2/continuumio/anaconda3/manifests/latest"
        },
        "selfLink": "https://index.docker.io/v2/continuumio/anaconda3/manifests"
    },
    "name": "anaconda3",
    "tag": "latest",
    "uri": "continuumio/anaconda3:latest",
    "url": "continuumio/anaconda3:latest",
    "version": ""
}

```
the above is truncated in the middle, but what you should know is that the middle chunk contains both versions of the manifest, if available.

## Get
Here is an example of a typical flow to download an image, and then use it. We will set the client at runtime to be Docker Hub (and not the default of Singularity Hub)

```
SREGISTRY_CLIENT=dockerhub sregistry pull centos:7
[client|dockerhub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Progress |===================================| 100.0% 
[1/1] |===================================| 100.0% 
Exploding /usr/local/libexec/singularity/bootstrap-scripts/environment.tar
Exploding /home/vanessa/.singularity/docker/sha256:af4b0a2388c69010cf675c050e51cb1fabbdf2303f955c31805b280324fd4523.tar.gz
Exploding /home/vanessa/.singularity/docker/metadata/sha256:7c987cc7f0a84f94bdad653b5eff809145a53cb4ce2af2070c8ce0527d2f2d52.tar.gz
WARNING: Building container as an unprivileged user. If you run this container as root
WARNING: it may be missing some functionality.
Building FS image from sandbox: /tmp/tmpdpenry16
Building Singularity FS image...
Building Singularity SIF container image...
Singularity container built: /home/vanessa/.singularity/shub/library-centos:7.simg
Cleaning up...

[container][new] library/centos:7
Success! /home/vanessa/.singularity/shub/library-centos:7.simg
```

Now we can use (or otherwise interact with the full path to it) with `get`

```
sregistry get library/centos:7
/home/vanessa/.singularity/shub/library-centos:7.simg
```
```
singularity shell $(sregistry get library/centos:7)
Singularity: Invoking an interactive shell within container...

Singularity library-centos:7.simg:~/Documents/Dropbox/Code/sregistry/sregistry-cli> 
```

<div>
    <a href="/sregistry-cli/commands"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-storage"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
