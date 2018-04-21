---
layout: default
title: Singularity Registry Client
pdf: true
permalink: /client-registry
toc: false
---

# Singularity Registry Client

A Singularity Registry backend is optimized to interact with a Singularit Registry, the configuration which is set in a credentials file typically located at `$SREGISTRY_CLIENT_SECRETS` that defaults to `$HOME/.sregistry`. If you aren't familiar with a Singularity Registry, it is an open source effort to empower institutions to host their own registries. It's more substantial then this `sregistry` client as it involves a bit of set up and configuration, and must run on a server with Docker. To read more, [view the documentation here](https://singularityhub.github.io/sregistry). You should check out the [getting started](../getting-started) pages for a list of environment variables that you can configure, and the [global commands](../getting-started/commands.md) for commands that are useful for all clients. Here we will review the set of commands that are specific to the Singularity Registry client:

 - *pull*: `[remote->local]` is a common use case. It says "get this remote registry image and pull it from there to my storage."
 - *push*: `[local->remote]` takes an image on your host and pushes to the registry (if you have permission).
 - *search*: `[remote]`: list containers for a remote endpoint, optionally with a search term.

The following commands are not yet developed or implemented, but can be (please [post an issue](https://www.singularityhub.github.io/sregistry/issues)):

 - *delete*: `[remote]`: delete an image from a remote endpoint if you have the correct credential (note this isn't implemented yet for the registry, but is noted here as a todo).


## Install
The Singularity Registry client for sregistry is recommended for use with Python 3, since it uses the datetime package to help with the credential header (if you have a workaround for this, please contribute since it causes issues for many). To install the dependencies:

```bash
$ pip install sregistry[registry]

# Or locally
$ pip install -e .[registry]
```

And this will install the extra requirements

## Sanity Checks
You will want to make sure that when you interact with `sregistry` that the Singularity Registry client is loaded. Note how when you use the shell, the default is Singularity hub:

```bash
$ sregistry shell
$ client.speak()
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
```

Instead, export the environment variable for `SREGISTRY_CLIENT` as `registry` for Singularity Registry (this tutorial):

```bash
$ SREGISTRY_CLIENT=registry sregistry shell
client.speak()
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
```

And of course you can set this as default by adding an export for `SREGISTRY_CLIENT=registry` in your bash profile, or simply exporting it
for your terminal session:

```bash
SREGISTRY_CLIENT=registry
export SREGISTRY_CLIENT
```
You can also activate the client:

```bash
$ sregistry backend activate registry
[activate] registry
sregistry backend status
[backend status]
There are 9 clients found in secrets.
active: registry
```

Now when you run the client, it will be active for the registry. You can glance quickly at which client is detected just by running
`sregistry` without any arguments, and note the top of the message:

```bash
$ sregistry

Singularity Registry Global Client v0.0.1 [registry]
usage: sregistry [-h] [--debug]
                 
                 {pull,version,images,rmi,rm,get,add,search,delete,inspect,shell,push,labels}
                 ...
```

## Pull
To pull an image, you would equivalently use "pull" with the registry client active. The base of your registry
will be read in from your `SREGISTRY_CLIENT_SECRETS`, and if this isn't found, it assumes local host.

The most likely thing that you would want to do with the client is pull an image. And
if you have just installed sregistry and done nothing else, this is the default client
that is used. The only difference between this pull and the Singularity pull is that
this pull will be saved to your local database. This means you can easily find and
manage images later. Here is how to pull:

```bash
$ sregistry pull vanessa/tacos:latest
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Progress |===================================| 100.0% 
[container][new] vanessa/tacos:latest
Success! /home/vanessa/.singularity/shub/vanessa/tacos:latest.simg
```

Notice that the container is flagged as "new" because we didn't have it (or metadata about it) before. If we were to pull again, the image would be found and updated, and we would be flagged as an update (see `[update]`):

```bash
$ sregistry pull vanessa/tacos:latest
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Progress |===================================| 100.0% 
[container][update] vanessa/tacos:latest
Success! /home/vanessa/.singularity/shub/vanessa/tacos:latest.simg
```

Importantly, if you pull an image that is a different **version** it's going to create a new container file and database entry. The above example is pulling an equivalent image, so we update the database entry that exists.

Note that the pull command is available from within python using the client:


```bash
$ sregistry shell
$ client.client_name
# 'registry'
$ client.pull('vanessa/tacos:latest')
```

## Inspect
Inspect isn't a command specific to any client, but we can use it here to look at the local image:

```python
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
vanessa/tacos:latest
http://127.0.0.1/containers/1/download/ec7e5014-4949-4c08-9d0e-744a15ea47d1
{
    "client": "registry",
    "collection": "vanessa",
    "collection_id": 5,
    "created_at": "2017-12-28 19:24:16",
    "id": 13,
    "image": null,
    "metrics": {
        "add_date": "2017-12-28T02:56:24.560592-06:00",
        "collection": "vanessa",
        "frozen": false,
        "id": 1,
        "image": "http://127.0.0.1/containers/1/download/ec7e5014-4949-4c08-9d0e-744a15ea47d1",
        "metadata": {
            "deffile": "Bootstrap: docker\nFrom: ubuntu:14.04\n\n%labels\nMAINTAINER vanessasaur\nWHATAMI dinosaur\n\n%environment\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n%files\nrawr.sh /rawr.sh\n\n%runscript\nexec /bin/bash /rawr.sh\n",
            "environment": "# Custom environment shell code should follow\n\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n",
            "runscript": "#!/bin/sh \n\nexec /bin/bash /rawr.sh\n",
            "size_mb": 62,
            "test": null
        },
        "metrics": {},
        "name": "tacos",
        "selfLink": "http://127.0.0.1/api/container/vanessa/tacos:latest",
        "tag": "latest",
        "version": null
    },
    "name": "tacos",
    "tag": "latest",
    "uri": "vanessa/tacos:latest",
    "url": "http://127.0.0.1/containers/1/download/ec7e5014-4949-4c08-9d0e-744a15ea47d1",
    "version": ""
}
```

and when we ask to see the specific versioned image, we see a modified inspection:

```python
$ sregistry inspect vanessa/tacos:latest@ed9755a0871f04db3e14971bec56a33f
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
vanessa/tacos:latest@ed9755a0871f04db3e14971bec56a33f
/home/vanessa/.singularity/shub/vanessa/tacos:latest.simg
{
    "client": "registry",
    "collection": "vanessa",
    "collection_id": 5,
    "created_at": "2017-12-28 19:27:32",
    "id": 14,
    "image": "/home/vanessa/.singularity/shub/vanessa/tacos:latest.simg",
    "metrics": {
        "add_date": "2017-12-28T02:56:24.560592-06:00",
        "collection": "vanessa",
        "frozen": false,
        "id": 1,
        "image": "http://127.0.0.1/containers/1/download/ec7e5014-4949-4c08-9d0e-744a15ea47d1",
        "metadata": {
            "deffile": "Bootstrap: docker\nFrom: ubuntu:14.04\n\n%labels\nMAINTAINER vanessasaur\nWHATAMI dinosaur\n\n%environment\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n%files\nrawr.sh /rawr.sh\n\n%runscript\nexec /bin/bash /rawr.sh\n",
            "environment": "# Custom environment shell code should follow\n\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n",
            "runscript": "#!/bin/sh \n\nexec /bin/bash /rawr.sh\n",
            "size_mb": 62,
            "test": null
        },
        "metrics": {},
        "name": "tacos",
        "selfLink": "http://127.0.0.1/api/container/vanessa/tacos:latest",
        "tag": "latest",
        "version": null
    },
    "name": "tacos",
    "tag": "latest",
    "uri": "vanessa/tacos:latest",
    "url": "http://127.0.0.1/containers/1/download/ec7e5014-4949-4c08-9d0e-744a15ea47d1",
    "version": "ed9755a0871f04db3e14971bec56a33f"
}
```

The same works from within python:

```python
$ sregistry shell
client.inspect('vanessa/tacos:latest')
```

## Push
Singularity Registry is one of the few clients that has "push," meaning that we can take an image that we have locally and push it to a registry. First, make sure that you have generated your [credentials file](https://singularityhub.github.io/sregistry/credentials.html). You **must** be an admin and/or manager of a Singularity Registry to push to it! If it's not running locally, also make sure that your credentials file has the correct url base (the file that you copy paste usually defaults to localhost, and this would be fine given that you are running the registry locally on your machine, and would need to be changed otherwise). Then, find a local image to push. In the example below, we will push an image called "expfactory.simg."

You can export the `SREGISTRY_CLIENT=registry` one time (on the same line before the command)

```bash
$ SREGISTRY_CLIENT=registry sregistry push --name milkshakes/pudding:banana expfactory.simg
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[================================] 173/173 MB - 00:00:00
[Return status 201 Created]

```
 or export it globally:

```bash
$ export SREGISTRY_CLIENT=registry
$ sregistry push --name registry://milkshakes/pudding:banana expfactory.simg
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[================================] 173/173 MB - 00:00:00
[Return status 201 Created]
```

Then you should see the image in a remote search:

```bash
$ sregistry search
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Collections
1  mso4sc/sregistry-cli:latest	http://127.0.0.1/containers/4
2  milkshakes/pudding:banana	http://127.0.0.1/containers/5
```

and then pull it to your local database.

```bash
$ sregistry pull milkshakes/pudding:banana
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Progress |===================================| 100.0% 
[container][new] milkshakes/pudding:banana
Success! /home/vanessa/.singularity/shub/milkshakes-pudding:banana.simg
```
```python
$ sregistry images | grep banana
27 January 24, 2018	[registry]	milkshakes/pudding:banana
28 January 24, 2018	[registry]	milkshakes/pudding:banana@846442ecd7487f99fce3b8fb68ae15af
vanessa@vanessa-ThinkPad-T460s:~/Desktop$
```


## Search
Finally, search is the correct way to list or search a remote endpoint, distinguished from "images" which does the same for your local database. For Singularity Registry, as a general user you will be able to see public images. The images you can see correspond with the images you are able to pull. 

```python
$ sregistry search
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Collections
1  vanessa/tacolicious:gobacktosleep	http://127.0.0.1/containers/3
2  vanessa/tacos:latest	http://127.0.0.1/containers/1
```

**Note** currently the images that you see for a search command (as above) are reflective of what images are public. The only images that are now "pullable" are those that are public, because we need to implement the same checks into the search and pull functions that we have for push. If you would like to make this contribution it would be a [great help](https://www.github.com/singularityhub/sregistry).


You can also search for a particular container or collection:

```python
$ sregistry search vanessa/tacos
[client|registry] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers vanessa/tacos
1  vanessa/tacos	latest	Dec 28, 2017 02:56AM
```
We can also do this same thing from within Python, and get back rows (lists of the result) to work with.

```python
$ sregistry shell 
rows = client.search()

# or search by collection
>>> client.search('vanessa')
# [['vanessa/tacolicious:gobacktosleep', 'http://127.0.0.1/containers/3'], ['vanessa/tacos:latest', 'http://127.0.0.1/containers/1']]

# or a particular container in a collection
>>> client.search('vanessa/tacos')
# [['vanessa/tacos', 'latest', 'Dec 28, 2017 02:56AM']]
```

This has been a general review of the custom commands for Singularity Registry. Don't forget that the Singularity Registry client also supports the [global client commands](../getting-started/commands.md) such as `inspect`, `images`, and `get`.

<div>
    <a href="/sregistry-cli/"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-hub.html"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
