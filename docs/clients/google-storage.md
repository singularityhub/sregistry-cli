---
layout: default
title: Singularity Global Client, Google Storage
pdf: true
permalink: /client-google-storage
toc: false
---

# Singularity Global Client: Google Storage

These sections will detail use of the Google Storage client for `sregistry`, which is a connection to a Google Storage
cloud bucket. 

[![asciicast](https://asciinema.org/a/154858.png)](https://asciinema.org/a/154858?speed=3)

## Getting Started
If you are using the sregistry image, the client is likely already installed. If you want to install this natively (or build a custom container) the command to install the module extras is:

```bash
pip install sregistry[google-storage]

# or locally
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli
pip install -e .[google-storage]
```

The next steps we will take are to first set up authentication, and then define your Storage Bucket (and other settings) via environment variables. 

### Environment
Singularity Registry Global Client works by way of obtaining information from the environment, which are cached when appropriate for future use. For Google Storage, you will first need to [set up authentication](https://cloud.google.com/docs/authentication/getting-started) by following those steps. It comes down to creating a file and saving it on your system with the variable name `GOOGLE_APPLICATION_CREDENTIALS`. This variable will be found and used every time you use the storage Client, without needing to save anything to the secrets.

Thus, the complete list of this required variable (and other options, with defaults shown) are the following:

 - [GOOGLE_APPLICATION_CREDENTIALS](https://cloud.google.com/docs/authentication/getting-started) should point to the file provided.
 - [SREGISTRY_GOOGLE_STORAGE_BUCKET](https://cloud.google.com/storage/docs/json_api/v1/buckets): is the name for the bucket you want to create. If not provided, we use your username prefixed with "sregistry."
 - `SREGISTRY_GOOGLE_STORAGE_PRIVATE`: by default, images that you upload will be made public, meaning that a user that stumbles on the URL (or has permission to read your bucket otherwise) will be able to see and download them. If you want to make an image private (one time or globally with an export in your bash profile) you should export this variable as some derivative of yes/true. If no variable is found, images are made public by default. If you set the variable once, it will be saved in your configuration for all subsequent images.

Notice that the first variable is not prefixed with `SREGISTRY_` and this is because it is already defined for the Google namespace, and use by `sregistry`.

For a detailed list of other (default) environment variables and settings that you can configure, see the [getting started](../getting-started) pages.  For the globally shared commands (e.g., "add", "get", "inspect," "images," and any others that are defined for all clients) see the [commands](../getting-started/commands.md) documentation. Here we will review the set of commands that are specific to the Google Storage client:

 - [pull](#pull): `[remote->local]` pull an image from the Singularity Hub registry to the local database and storage.
 - [search](#search): `[remote]` list all image collections in Singularity Hub

For all of the examples below, we will export our client preference to be `google-storage`

```bash
SREGISTRY_CLIENT=google-storage
export SREGISTRY_CLIENT
```
but note that you could just as easily define the variable for one command:

```bash
SREGISTRY_CLIENT=google-storage sregistry shell
```

or do away the need to export this environment variable by simply activating the client:

```bash
$ sregistry backend activate google-storage
[activate] google-storage
$ sregistry backend status
[backend status]
There are 9 clients found in secrets.
active: google-storage
```


## Shell
After we have exported `SREGISTRY_CLIENT` above, if you are looking to interact with a shell for the google-storage `sregistry` client, just ask for it:

```bash
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

```bash
sregistry push --name vsoch/hello-world:latest vsoch-hello-world-master-latest.simg
[bucket][sregistry-vanessa]
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container][update] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media
```

You will see again the connection to the bucket, and then a progress bar that shows the status of the upload, and the progress bar is replaced by the final container url. 


## Inspect
Of course you can inspect an image (here we will inspect the image we just pushed above), and you will see a ton of goodness:

```bash
$ sregistry inspect vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
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


## Pull and Search
Now let's say that we pushed an image a while back to Google Storage, we have the record locally, and we want to get it. We could use "get" to get the url and then plug it into our special download logic, or we could instead want to pull the image to our local `sregistry` database. This would mean that the "remote" record gets updated to "local" because we actually have the image! How do we do that? We will go through two scenarios. In the first, we've totally forgotten about our local database (or it blew up) and we need to search the remote endpoint. In the second, we have our local database and just want to get one (pull).

### Search
A search without any parameters will essentially list all containers in the configured storage bucket. But how do we know what is a container?

>> a container is defined by having the metadata key "type" with value "container" and this is set by the upload (push) client.

Thus, if you do some fancy operation outside of using the client to upload containers to storage, make sure that you add this metadata value, otherwise they will not be found. Let's do a quick search to get our list in Google Storage. This action has no dependency on a local storage or database.

```bash
$ sregistry search
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
[gs://sregistry-vanessa] Containers
1      174 MB	/home/vanessa/desktop/expfactory:latest
2       62 MB	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
```

Then to look at details for a more specific search, let's try searching for "vsoch"

```bash
$ sregistry search vsoch
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
With pull, we might have done a search to find a container that we liked, as shown above, and we want to retrieve it. In this case, instead of inspect or get, we just use pull.

```bash
$ sregistry pull vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
Searching for vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f in gs://sregistry-vanessa
Progress |===================================| 100.0% 
[container][update] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
Success! /home/vanessa/.singularity/shub/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg
```
and if we do a get, we get the path to the file:

```bash
$ sregistry get vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
/home/vanessa/.singularity/shub/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg
```

You can also see in the pull output that on the backend of pull is the same search as you did before. This means that
if you want to be precise, you should ask for the complete uri (version included). If you aren't precise, it will do
a search across name fields and give you the first match. Be careful, my linux penguins.

For debugging scripts, see [Google Cloud Debugging](/sregistry-cli/client-google-debugging).


<div>
    <a href="/sregistry-cli/commands"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-drive"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
