---
layout: default
title: Getting Started with Commands
pdf: true
permalink: /commands
toc: false
---

# Global Commands

The following commands are provided for the client for all endpoints, as they
pertain to interaction with the local sregistry database. This section shows the commands
running from the host command line (which could be an executable installed to python or
a singularity image of the same name). In both cases, the executable is called `sregistry`.
It is not written yet, but a separate guide will be made for interaction using the pre-built
Singularity image. For these same functions for within python (for developers) [see here](developers.md). As a reminder, the global commands are the following:

 - *add*: `[local]`: corresponds with adding an image file on your host directly to your registry. Not everything is downloaded from the cloud!
 - *get*: `[local]`: given a uri, return the full path to the image in your storage. A common use case would be to pipe a get command into a singularity command, for example.
 - *images*: `[local]`: list images in your local database, optionally with filters to search.
 - *inspect* `[local]`: prints out an image manifest and metadata retrieved from its endpoint.
 - *rm* `[local]`: is akin to Docker's remove, and says "remove this record from my database, but don't delete the image." This corresponds with deleting the database record, but not the image file in your storage.
 - *rmi* `[local]`: the same as `rm`, but additionally deletes the image file from storage.
 - *shell* `[local]`: want to work with a client interactively? Just shell in and go!


## Add
Adding an image to your database, meaning a local file, is the simplest action that you can perform, as it doesn't requite any remote endpoint or even web connectivity. Let's try doing this now.

```
sregistry add --name expfactory/example expfactory-expfactory-master-test.simg 
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container] expfactory/example:latest
```

In the above, I've taken the local file `expfactory-expfactory-master-test.simg` and moved
it into my storage and database. The file will be removed from the present working directory. You can achieve the equivalent to add an image to your database and storage but make a copy with copy.

```
sregistry add --copy --name expfactory/example expfactory-expfactory-master-test.simg 
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container] expfactory/example:latest
```


## Images
I can then use a simple "images" operation to list the available images. and in the list I can
see the image newly added. 

```
sregistry images
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers:   [date]   [location]  [client]	[uri]
1  December 27, 2017	local	   [hub]	vsoch/hello-pancakes:latest@22aa66e0c80847c676f34f35e70ea066
2  December 27, 2017	local	   [hub]	expfactory/expfactory-master:v2.0@03c1ab08e58c6a5101bc790cd9836d25
3  December 27, 2017	local	   [hub]	vsoch/sregistry-example:v1.0@b102e9f4c1b2228d6e21755b27c32ed2
4  December 27, 2017	remote 	   [hub]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
```

Note that you will see, for each image, the client that was use, the date added, the complete uri (and importantly) whether
the image file exists in storage locally (local) or if it's just a remote entry (remote). 
If you want to filter the listing, just add a search term!

```
Containers:   [date]   [location]  [client]	[uri]
1  December 27, 2017	local	   [hub]	expfactory/expfactory-master:v2.0@03c1ab08e58c6a5101bc790cd9836d25
```

## Get
Great! We've added images, and we know how to list and search. But how do we use them? After you have secured an image in your local database (using the add example above) to interact with it you can use the `get` command, and again you can reference the image based on its uri. Here are some examples.

```
$ sregistry get vsoch/hello-world:latest@5808346196ab69c3fcdc2394de358840
/home/vanessa/.singularity/shub/vsoch/hello-world:latest.simg

$ sregistry get vsoch/hello-pancakes:latest@22aa66e0c80847c676f34f35e70ea066
/home/vanessa/.singularity/shub/vsoch/hello-pancakes:latest.simg
```

It logically follows that you should be very specific about the image that you are asking for. You can use these get statements with singularity (or other) commands too!

```
$ singularity run $(sregistry get vsoch/hello-world)
RaawwWWWWWRRRR!!

$ ls -l $(sregistry get vsoch/hello-world)
-rw------- 1 vanessa vanessa 65347615 Dec 25 11:08 /home/vanessa/.singularity/shub/vsoch/hello-world:latest.simg
```

## Inspect
You probably would want to inspect your images to get more detail about a particular one! Do that as follows:


```
sregistry inspect vsoch/hello-world
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
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

Since this is a Singularity Hub image, we have stored with it the metadata from Singularity Hub, along with the output from the Singularity inspect.

## Shell
If we want to interact with a client, we can use a shell.

```
sregistry shell
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
>>> client
[client][sregistry.main.hub]
>>> client.database
'sqlite:////home/vanessa/.singularity/sregistry.db'
>>> client.client_name
'hub'
>>> 
```
Notice how the client is already loaded into the space!


## Remove
The client can either remove an image from the database record (rm) but **not** the container
in storage (`rm`) or delete the database record **and** theimage (`rmi`). You **must** be specific about versions, if you want to target a particular version. Otherwise, the first returned in the query is removed, which may not be what you want. Thus we recommend this sort of remove command:

```
sregistry rmi vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
/home/vanessa/.singularity/shub/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg

sregistry rmi vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
https://www.googleapis.com/download/storage/v1/b/singularityhub/o/singularityhub%2Fgithub.com%2Fvsoch%2Fhello-world%2Fe279432e6d3962777bb7b5e8d54f30f4347d867e%2Fed9755a0871f04db3e14971bec56a33f%2Fed9755a0871f04db3e14971bec56a33f.simg?generation=1508072025589820&alt=media
```

The first example has found and removed an image and record, and the second is just a record (a url for an image). We could have issued these same two deletions (but perhaps out of order) like:

```
sregistry rmi vsoch/hello-world:latest
sregistry rmi vsoch/hello-world:latest
```

<div>
    <a href="/sregistry-cli/developers.html"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
