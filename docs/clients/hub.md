---
layout: default
title: Singularity Hub Client
pdf: true
permalink: /client-hub
toc: false
---

# Singularity Hub Client

These sections will detail use of the Singularity Hub clients for `sregistry`, which is
the default backend client to use given that no other environment variables are set. For a detailed list of
the environment variables and settings that you can configure, see the [getting started](../getting-started) pages. 
For the globally shared commands (e.g., "add", "get", "inspect," "images," and any others that are defined for all clients)
see the [commands](../getting-started/commands.md) documentation. Here we will review the set of commands that are
specific to the Singularity Hub client:

 - [pull](#pull): `[remote->local]` pull an image from the Singularity Hub registry to the local database and storage.
 - [search](#search): `[remote]` list all image collections in Singularity Hub
 - [record](#record): `[remote->local]` obtain metadata and image paths for a remote image and save to the database, but don't pull the container to storage.


## Pull
The most likely thing that you would want to do with the client is pull an image. And
if you have just installed sregistry and done nothing else, this is the default client
that is used. The only difference between this pull and the Singularity pull is that
this pull will be saved to your local database. This means you can easily find and
manage images later. Here is how to pull:

```bash
$ sregistry pull vsoch/hello-world
[client|hub] [database|/home/vanessa/.singularity/sregistry.db]
Progress |===================================| 100.0% 
[container] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
Success! /home/vanessa/.singularity/shub/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg
```

Notice how the image is saved (and named) under it's collection folder, and with the full path corresponding
to all information about the version we could find. [@vsoch](https://www.github.com/vsoch) might change this storage strategy to have the full
image path correspond to include the collection too - it's not decided if a folder for each collection is the best
way to go. [What do you think](https://www.github.com/singularityhub/sregistry-cli/issues)? You can also do this from within python:

```python
sregistry shell
client.client_name
# 'hub'
client.pull('vsoch/hello-world')
```

## Inspect
While this isn't considered a client command (you can use it across clients) its useful now to inspect the container we've just pulled. The inspection includes metadata extracted from
the Singularity Hub API, along with from the image (if Singularity was installed on the host
that downloaded it).

```bash
sregistry inspect vsoch/hello-world
[client|hub] [database|/home/vanessa/.singularity/sregistry.db]
/home/vanessa/.singularity/shub/vsoch/hello-world:latest.simg
{
    "client": "hub",
    "collection": "vsoch",
    "collection_id": 2,
    "created_at": "2017-12-26 16:31:15",
    "id": 2,
    "image": "/home/vanessa/.singularity/shub/vsoch/hello-world:latest.simg",
    "metrics": {
        "data": {
            "attributes": {
                "deffile": "Bootstrap: docker\nFrom: ubuntu:14.04\n\n%runscript\n\nexec echo \"Tacotacotaco\"\n",
                "environment": "# Custom environment shell code should follow\n\n",
                "help": null,
                "labels": {
                    "org.label-schema.build-date": "2017-10-18T13:54:37+00:00",
                    "org.label-schema.build-size": "341MB",
                    "org.label-schema.schema-version": "1.0",
                    "org.label-schema.usage.singularity.deffile": "Singularity",
                    "org.label-schema.usage.singularity.deffile.bootstrap": "docker",
                    "org.label-schema.usage.singularity.deffile.from": "ubuntu:14.04",
                    "org.label-schema.usage.singularity.version": "2.4-feature-squashbuild-secbuild.g217367c"
                },
                "runscript": "#!/bin/sh \n\n\nexec echo \"Tacotacotaco\"\n",
                "test": null
            },
            "type": "container"
        }
    },
    "name": "hello-world",
    "tag": "latest",
    "uri": null,
    "url": null,
    "version": "22aa66e0c80847c676f34f35e70ea066"
}
```

and the same works from within python:

```bash
$ client.inspect('vsoch/hello-world')
```

Notice that the client is relevant to Singularity Hub. You could imagine at some point using
different clients to retrieve images with possibly the same (without version) names, in which case
this keeps them separate. It's less important for this use case, and more important so that in the future when you want to do some operation with this image, we know the backend to use to perform it.


## Search
Search is the correct way to list or search a remote endpoint, distinguished from "images" which does the same for your local database. For Singularity Hub you can do a search without arguments to list all containers at the endpoint:

```bash
$ sregistry search
```

or you can issue a search for a specific collection and container

```bash
$ sregistry search vsoch/hello-world
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers vsoch/hello-world
1  [name]	vsoch/hello-world
2  [date]	Oct 18, 2017 01:06PM
3  vsoch/hello-world:latest
```

We can also do this same thing from within Python, and get back rows (lists of the result) to work with.

```bash
$ sregistry shell 
# akin to starting a shell and doing from from sregistry.main import Client as client

rows = client.search()

# You can also query by a container - note this currently just supports
# knowing the full name
cli.search('vsoch/hello-world')
# Containers vsoch/hello-world
# 1  [name]	vsoch/hello-world
# 2  [date]	Oct 18, 2017 01:06PM
# 3  vsoch/hello-world:latest
```

## Record
Finally, the "record" command is akin to a pull, but you don't care about retrieving the image. You just want the metadata! You can also do this with the command line:

```bash
$ sregistry record vsoch/hello-world
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
```

and then view that a record (see the remote label) for our image was added to our images:

```bash
$ sregistry images
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers:   [date]   [location]  [client]	[uri]
1  December 27, 2017	local 	   [hub]	expfactory/expfactory-master:v2.0@03c1ab08e58c6a5101bc790cd9836d25
2  December 27, 2017	local 	   [hub]	vsoch/sregistry-example:v1.0@b102e9f4c1b2228d6e21755b27c32ed2
7  December 28, 2017	local 	   [registry]	library/tacolicious:gobacktosleep@5b0c0982-9e9a-4e66-8aa1-91ae2cba4cd3
8  December 28, 2017	remote	   [hub]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
```

If you have a record and then later pull the image, the record is considered equivalent and updated.
Don't forget that the Singularity Hub client also supports the [global client commands](../getting-started/commands.md)

<div>
    <a href="/sregistry-cli/"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-registry.html"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
