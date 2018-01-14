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
|SREGISTRY_DOCKERHUB_NO_HTTPS | not set        | If found as yes/t/true/y or some derivation, make calls without https (usually for local registries and not recommended)  
|SREGISTRY_DOCKERHUB_VERSION  |  v2            | the Docker Hub API version to use |
|SREGISTRY_DOCKERHUB_OS       | linux          | The choice of operating system to use from the schema version 2 image manifest |
|SREGISTRY_DOCKERHUB_ARCHITECTURE| amd64       | the system architecture to use from the schema verison 2 image manifest
|SREGISTRY_DOCKERHUB_CMD |     not set         | If found as yes/t/true/y or some derivation, use "CMD" instead of "EntryPoint" for container runscript|


#### Authentication
You will notice in the above table that you have multiple options for authenticating with Docker Hub. We recommend that you use the standard docker credential file (generated with `docker login` that is usually located at `$HOME/.docker/config.json` with your secrets token. If you choose to export your username and password, we do not send it beyond the client (or cache it anywhere) but instead generate a base64 encoded string to pass with the header to identify you and ask for a token. **Important** `sregistry` will not cache or otherwise save any of your credential information to the `.sregistry` secrets. This information must be set in the environment (either the path to the file or username and password) for each usage of the client.


## Commands
For a detailed list of other (default) environment variables and settings that you can configure, see the [getting started](../getting-started) pages.  For the globally shared commands (e.g., "add", "get", "inspect," "images," and any others that are defined for all clients) see the [commands](../getting-started/commands.md) documentation. Here we will review the set of commands that are specific to the Google Storage client:

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

# STOPPED HERE

## Shell
After we have exported `SREGISTRY_CLIENT` above, if you are looking to interact with a shell for the google-storage `sregistry` client, just ask for it:

```
sregistry shell
[bucket][sregistry-vanessa]
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Python 3.5.2 |Anaconda 4.2.0 (64-bit)| (default, Jul  2 2016, 17:53:06) 
Type "copyright", "credits" or "license" for more information.

IPython 5.1.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.

In [1]: 
```

Here we see straight away that we are using the default bucket name (`sregistry-vanessa`) and the google-storage client. The printing of the bucket on the first line indicates we successfully connected to it.

## Push
If you don't have any images in your bucket, that is probably a good start to add some. In this case we will add an image sitting in our present working directory.

```
sregistry push --name vsoch/hello-world:latest vsoch-hello-world-master-latest.simg
[bucket][sregistry-vanessa]
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container][update] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media
```

You will see again the connection to the bucket, and then a progress bar that shows the status of the upload, and the progress bar is replaced by the final container url. By default, this push command doesn't add a container to our local storage database, but just a record that it exists in Google. To see the record, you can list your images:

```
sregistry images
[bucket][sregistry-vanessa]
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers:   [date]   [location]  [client]	[uri]
1  December 29, 2017	remote	   [google-storage]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
2  December 30, 2017	remote	   [google-storage]	expfactory/expfactory:test@846442ecd7487f99fce3b8fb68ae15af
```

At this point you have remote records, but no images locally. You could do a "get" or an "inspect".

## Get
For a remote image record, if you do a "get" you will be given the remote url:

```
sregistry get vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media
```

If you don't want to get the url but you want to look at all metadata, then use "inspect."

## Inspect
Of course you can inspect an image (here we will inspect the image we just pushed above), and you will see a ton of goodness:

```
sregistry inspect vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
[bucket][sregistry-vanessa]
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media
{
    "client": "google-storage",
    "collection": "vsoch",
    "collection_id": 1,
    "created_at": "2017-12-29 00:05:09",
    "id": 1,
    "image": null,
    "metrics": {
        "attributes": {
            "deffile": "Bootstrap: docker\nFrom: ubuntu:14.04\n\n%labels\nMAINTAINER vanessasaur\nWHATAMI dinosaur\n\n%environment\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n%files\nrawr.sh /rawr.sh\n\n%runscript\nexec /bin/bash /rawr.sh\n",
            "environment": "# Custom environment shell code should follow\n\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n",
            "help": null,
            "labels": {
                "MAINTAINER": "vanessasaur",
                "WHATAMI": "dinosaur",
                "org.label-schema.build-date": "2017-10-15T12:52:56+00:00",
                "org.label-schema.build-size": "333MB",
                "org.label-schema.schema-version": "1.0",
                "org.label-schema.usage.singularity.deffile": "Singularity",
                "org.label-schema.usage.singularity.deffile.bootstrap": "docker",
                "org.label-schema.usage.singularity.deffile.from": "ubuntu:14.04",
                "org.label-schema.usage.singularity.version": "2.4-feature-squashbuild-secbuild.g780c84d"
            },
            "runscript": "#!/bin/sh \n\nexec /bin/bash /rawr.sh\n",
            "test": null
        },
        "branch": "master",
        "bucket": "sregistry-vanessa",
        "collection": "vsoch",
        "commit": "e279432e6d3962777bb7b5e8d54f30f4347d867e",
        "contentType": "application/octet-stream",
        "crc32c": "1FCMGQ==",
        "etag": "CIHy5PnTstgCEAE=",
        "generation": "1514668522289409",
        "id": "sregistry-vanessa/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg/1514668522289409",
        "image": "hello-world",
        "kind": "storage#object",
        "md5Hash": "7ZdVoIcfBNs+FJcb7FajPw==",
        "mediaLink": "https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media",
        "metageneration": "1",
        "name": "vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg",
        "selfLink": "https://www.googleapis.com/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg",
        "size": "65347615",
        "size_mb": "333",
        "storage": "vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg",
        "storageClass": "STANDARD",
        "tag": "latest",
        "timeCreated": "2017-12-30T21:15:22.270Z",
        "timeStorageClassUpdated": "2017-12-30T21:15:22.270Z",
        "type": "container",
        "updated": "2017-12-30T21:15:22.270Z",
        "uri": "vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f",
        "version": "ed9755a0871f04db3e14971bec56a33f"
    },
    "name": "hello-world",
    "tag": "latest",
    "uri": "vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f",
    "url": "https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media",
    "version": "ed9755a0871f04db3e14971bec56a33f"
}
```

### Record
Finally, if you don't have a record locally but want to get one that already exists, then use record.

```
sregistry record vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
Searching for vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f in gs://sregistry-vanessa
[container][update] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
```

If you had an image already, it won't be replaced, but the record will be updated.


## Pull and Search
Now let's say that we pushed an image a while back to Google Storage, we have the record locally, and we want to get it. We could use "get" to get the url and then plug it into our special download logic, or we could instead want to pull the image to our local `sregistry` database. This would mean that the "remote" record gets updated to "local" because we actually have the image! How do we do that? We will go through two scenarios. In the first, we've totally forgotten about our local database (or it blew up) and we need to search the remote endpoint. In the second, we have our local database and just want to get one (pull).

### Search
A search without any parameters will essentially list all containers in the configured storage bucket. But how do we know what is a container?

>> a container is defined by having the metadata key "type" with value "container" and this is set by the upload (push) client.

Thus, if you do some fancy operation outside of using the client to upload containers to storage, make sure that you add this metadata value, otherwise they will not be found. Let's do a quick search to get our list in Google Storage. This action has no dependency on a local storage or database.

```
sregistry search
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
[gs://sregistry-vanessa] Containers
1      174 MB	/home/vanessa/desktop/expfactory:latest
2       62 MB	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
```

Then to look at details for a more specific search, let's try searching for "vsoch"

```
sregistry search vsoch
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
[gs://sregistry-vanessa] Found 1 containers
vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg 
id:      sregistry-vanessa/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg/1514668522289409
uri:     vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
updated: 2017-12-30 21:15:24.132000+00:00
size:    62 MB
md5:     7ZdVoIcfBNs+FJcb7FajPw==
```

### Pull
With pull, we might have a record (or did a search to find a container that we liked, as shown above). In this case, instead of inspect or get, we just use pull.

```
sregistry pull vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
Searching for vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f in gs://sregistry-vanessa
Progress |===================================| 100.0% 
[container][update] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
Success! /home/vanessa/.singularity/shub/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg
```

Did you notice that this was an update? The reason is because we already had the record in our database from when we pushed it in the first place, and the record was updated to now be for a local file:

```
sregistry images
sregistry images
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
Containers:   [date]   [location]  [client]	[uri]
1  December 29, 2017	local 	   [google-storage]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
2  December 30, 2017	remote	   [google-storage]	expfactory/expfactory:test@846442ecd7487f99fce3b8fb68ae15af
```

and if we do a get, instead of the url we get the path to the file:

```
sregistry get vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
/home/vanessa/.singularity/shub/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg
```

You can also see in the pull output that on the backend of pull is the same search as you did before. This means that
if you want to be precise, you should ask for the complete uri (version included). If you aren't precise, it will do
a search across name fields and give you the first match. Be careful, my linux penguins.

<div>
    <a href="/sregistry-cli/commands"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-drive"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
