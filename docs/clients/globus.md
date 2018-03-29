---
layout: default
title: Singularity Global Client, Globus
pdf: true
permalink: /client-globus
toc: false
---

# Singularity Global Client: Globus

These sections will detail use of the Globus client for `sregistry`, meaning that you
can transfer containers to and from Globus endpoints. You will need to configure a 
[Globus Personal Endpoint](https://docs.globus.org/how-to/). For this tutorial, 
we used the instructions first for the [linux command line](https://docs.globus.org/how-to/globus-connect-personal-linux/#globus-connect-personal-cli). If you have any trouble with these steps, please
[reach out](https://www.github.com/singularityhub/sregistry-cli/issues).


## Installation
The [Globus Python SDK](https://globus-sdk-python.readthedocs.io/en/stable/examples/native_app/)
is the means by which we connect with Globus. You should install it's dependencies: 

```bash
pip install sregistry[globus]

# or locally
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli
pip install -e .[globus]
```

To set the default for your shell to use globus, export `SREGISTRY_CLIENT`

```bash
export SREGISTRY_CLIENT=globus
```

you can also prepend it to any sregistry command:

```bash
$ SREGISTRY_CLIENT=globus sregistry shell
```

### Your Globus  Personal Endpoint
A globus personal endpoint is referring to a computer (such as yours!) that can be
connected to via Globus, meaning that a small set of directories that you've designated
can share files with others that use Globus. This also means that you can transfer files
from your shared paths to folders on other Globus endpoints, such as your research cluster.
While it isn't required to have a Globus Personal Endpoint, without one you will
not be able to add images to your registry from other endpoints, or push images from your
registry to a remote endpoint. To be concise:

 - if you don't have a Globus Personal Endpoint you can only browse remotes
 - if you do have a Globus Personal Endpoint you can transfer images between endpoints, and images between remote endpoints and your computer.

These instructions will walk through how to set this up. If you use your endpoint casually
I would recommend only having it running while you are using it. First, follow
the instructions in the appropriate link (linux, Mac, or Windows) [here](https://docs.globus.org/how-to/) to install
Globus Personal Endpoint. The things we care about are as follows:

 - `globusconnectpersonal`: the command line controller for your endpoint. This will be found inside
the folder that you extracted in the [installation instructions](https://docs.globus.org/how-to/globus-connect-personal-linux/#globus-connect-personal-cli). You can add this to your `$PATH` if you want it to be available from anywhere.
 - `$HOME/.globusonline/lta/config-paths`: a text file with a column of paths and permissions that determine how your endpoint can be used. We will set this up once, and then we can forget about it.

#### Set Up Configuration Paths
Open up the configuration file in your favorite text editor.

```bash
$ vim $HOME/.globusonline/lta/config-paths
```

Each line corresponds to a share. You might have multiple shares, and either way,
add a new line to the file that shares your Singularity Registry images folder:

```
/home/vanessa/.singularity/shub,0,1
```

Note that this step is important, because this is the default folder that
the Singularity Registry Global Client uses for storage. The path followed by `0,1`
means that we want read/write access (for those with permission to the endpoint share). 
If instead you want to be able to push images to endpoints on your research cluster 
but not pull images from there, then you can use a more restrictive read only setting:

```
/home/vanessa/.singularity/shub,0,0
```

At this point, you should be ready to start the service! If you didn't add the
globusconnectpersonal executable to your path, then navigate to the folder where 
it is. You can then start the service:

```
$ globusconnectpersonal -start &
[1] 23031
```
If you had it running and need to restart, I find that a stop and clean start works
best.

```
globusconnectpersonal -stop
Globus Connect Personal is currently running and connected to Globus Online
Sending stop signal... Done
vanessa@vanessa-ThinkPad-T460s:~/Documents/globusconnectpersonal-2.3.3$ globusconnectpersonal -start &
[1] 23034
```

Once this is running, you can continue on to the next step! Since this is a server
that exposes your computer to some extent, unless you have reason to, you might
only consider having your endpoint running when you actually need to use it.


## Authentication
Now we can use the `sregistry` client! The Globus API uses refresh tokens, 
so when you run it for the first time it should ask you to open your browser, 
authenticate, and then copy paste a code back into
the terminal. For our first go, let's try listing endpoints.

```
$ SREGISTRY_CLIENT=globus sregistry search
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Listing shared endpoints. Add query to expand search.
Please select an endpoint id to query from
Please go to this URL and login: https://auth.globus.org/v2/oauth2/authorize?access_type=offline&code_challenge=V_1aRZoHhV1nOotp3UrAXxksXDJLL1VhothI7kBgIIk&redirect_uri=https%3A%2F%2Fauth.globus.org%2Fv2%2Fweb%2Fauth-code&client_id=ae32247c-2c17-4c43-92b5-ba7fe9957dbb&code_challenge_method=S256&state=_default&scope=openid+profile+email+urn%3Aglobus%3Aauth%3Ascope%3Atransfer.api.globus.org%3Aall&response_type=code
Please enter the code you get after login here: 
```

In the browser, we go through first a screen where you authenticate with your
institution or provider of choice, and then the following screen:

![img/globus-login1.png](img/globus-login1.png)

And you can choose a name to identify the connection. Finally, it will show 
you a "Native App Authorization Code" that you can copy paste into the terminal.
The finishing sequence given a successful handshake will show you (likely) a
personal endpoint and any others shared with you.

```bash
Please enter the code you get after login here: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Globus Endpoints
1  9ec1db6a-5052-11e7-bdb7-22000b9a448b	[shared-with-me]	9ec1db6a-5052-11e7-bdb7-22000b9a448b
2  74f0809a-d11a-11e7-962c-22000a8cbd7d	[my-endpoints]	74f0809a-d11a-11e7-962c-22000a8cbd7
```

Once you do this, you shouldn't need to go through the procedure again as the 
refresh token will be used. Here is issuing the command again:

```
SREGISTRY_CLIENT=globus sregistry search
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Listing shared endpoints. Add query to expand search.
Please select an endpoint id to query from
Globus Endpoints
1  74f0809a-d11a-11e7-962c-22000a8cbd7d	[my-endpoints]	74f0809a-d11a-11e7-962c-22000a8cbd7d
2  9ec1db6a-5052-11e7-bdb7-22000b9a448b	[shared-with-me]	9ec1db6a-5052-11e7-bdb7-22000b9a448b
```

## Commands
The core of the Globus endpoint is moving images between your local machine and remote
endpoints. This means the client supports the following commands:

 - [search](#search): `[remote]` list endpoints that you have access to, and peek at contents
 - [push](push): `[local->remote]` a container from your Singularity Registry endpoint to a globus endpoint.
 - [pull](#pull): `[remote->local]` pull an image from the Singularity Hub registry to the local database and storage.

For all of the examples below, we will export our client preference to be `globus`

```bash
SREGISTRY_CLIENT=globus
export SREGISTRY_CLIENT
```
but note that you could just as easily define the variable for one command:

```bash
SREGISTRY_CLIENT=globus sregistry shell
```

Remember that you can also inspect, get, and a host of other commands for your containers 
that aren't specific to the client. If you need a reminder, see the [commands](../getting-started/commands.md) documentation.


## Search
We will start with search, because for both "pull" and "push" you will need another endpoint
to interact with. It's highly unlikely that you've memorized the unique id of an endpoint! Here we will
review the different kinds of search.

### List Endpoints
To list endpoints in the scopes of those that you own (`my-endpoints`) and those that are
shared with you (`shared-with-me`):


```bash
$ sregistry search
sregistry search
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Listing shared endpoints. Add query to expand search.
Please select an endpoint id to query from
Globus Endpoints
1  9ec1db6a-5052-11e7-bdb7-22000b9a448b	[shared-with-me]	9ec1db6a-5052-11e7-bdb7-22000b9a448b
2  74f0809a-d11a-11e7-962c-22000a8cbd7d	[my-endpoints]	74f0809a-d11a-11e7-962c-22000a8cbd7d
```

Notice the message that we can "Add query to expand search?" This is very likely
what you will need to do to discover endpoints on your cluster.

```
$ sregistry search srcc
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
You must specify an endpoint id to query!
Please select an endpoint id to query from
Globus Endpoints
1  6881ae2e-db26-11e5-9772-22000b9da45e	[all]	sherlock
2  b1d99994-35ff-11e7-bcd6-22000b9a448b	[all]	b1d99994-35ff-11e7-bcd6-22000b9a448b
3  065a734e-173c-11e8-b656-0ac6873fc732	[all]	scg
4  96a13ae8-1fb5-11e7-bc36-22000b9a448b	[all]	oak
5  df70ebeb-6d04-11e5-ba46-22000b92c6ec	[all]	srcc
6  e42740f2-6d04-11e5-ba46-22000b92c6ec	[all]	dtn2
7  9ec1db6a-5052-11e7-bdb7-22000b9a448b	[shared-with-me]	9ec1db6a-5052-11e7-bdb7-22000b9a448b
8  74f0809a-d11a-11e7-962c-22000a8cbd7d	[my-endpoints]	74f0809a-d11a-11e7-962c-22000a8cbd7d
```

### List Endpoint Content
Now let's say we've found our favorite endpoint, and we want to peek at what is there:

```bash
$ sregistry search --endpoint 6881ae2e-db26-11e5-9772-22000b9da45e
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Endpoint Listing  
1  type	[perm]	[size]	[name]
2  dir	0755	4096	.chkpnt
3  dir	0755	4096	.singularity
4  dir	0755	4096	WORK
5  dir	0755	4096	docker
6  dir	0755	4096	metadata
7  dir	0775	4096	share
8  dir	0755	4096	vep
9  file	0755	1671569439	cosyne-spm12.simg
10 file	0755	616017951	eilon-s-sherlock_vep-master.simg
11 file	0755	6534725664	qsd.simg
```

We have a nice listing of the default folder at my endpoint, which happens to be
my `$SCRATCH` directory. You can't see it in this interface, but the images are colored
in purple. The client highlights files for you that are likely to be Singularity images
based on the extension. Now what if we wanted to look into the folder .singularity.
which happens to be the directory that I use for caching on the cluster? Just add
it to your endpoint address:


```bash
$ sregistry search --endpoint 6881ae2e-db26-11e5-9772-22000b9da45e:.singularity
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Endpoint Listing .singularity 
1  type	[perm]	[size]	[name]
2  dir	0755	20480	docker
3  dir	0755	4096	metadata
4  dir	0755	4096	shub
5  file	0644	616017951	eilon-s-sherlock_vep-master.img.gz
6  file	0755	422748191	sherlock-recurrent_nn.simg
```

Now that we are comfortable with finding endpoints and seeing content, let's give 
a go at push and pull.


## Push
Let's be lazy and grab a test image from Singularity Hub. We *could* pull this
with Singularity...

```bash
$ singularity pull shub://vsoch/hello-world
```

but if we pull it with sregistry, it will go right into our storage and is ready
to go at the Globus endpoint!

```bash
$ sregistry pull hub://vsoch/hello-world
$ sregistry get vsoch/hello-world
/home/vanessa/.singularity/shub/vsoch-hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d.simg
```

### Push from Your Sregistry
Now let's push to a Globus endpoint. We know from the search that we want to push it
to endpoint with id `6881ae2e-db26-11e5-9772-22000b9da45e`. We will be pushing to
the folder `.singularity/shub`, which is both the Singularity default cache and 
a reasonable default to find images. If it doesn't exist, it will be created.

```bash
$ sregistry push $(sregistry get vsoch/hello-world) --name 6881ae2e-db26-11e5-9772-22000b9da45e
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
.singularity/shub already exists at endpoint
2.4.2-fix/docker-env.g69a088b
{
    "data": {
        "attributes": {
            "deffile": "Bootstrap: docker\nFrom: ubuntu:14.04\n\n%labels\nMAINTAINER vanessasaur\nWHATAMI dinosaur\n\n%environment\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n%files\nrawr.sh /rawr.sh\n\n%post\nchmod u+x /rawr.sh\n\n%runscript\nexec /bin/bash /rawr.sh\n",
            "help": null,
            "labels": {
                "org.label-schema.usage.singularity.deffile.bootstrap": "docker",
                "MAINTAINER": "vanessasaur",
                "org.label-schema.usage.singularity.deffile": "Singularity",
                "org.label-schema.schema-version": "1.0",
                "WHATAMI": "dinosaur",
                "org.label-schema.usage.singularity.deffile.from": "ubuntu:14.04",
                "org.label-schema.build-date": "Sun,_18_Mar_2018_17:40:09_+0000",
                "org.label-schema.usage.singularity.version": "2.4.3-feature-squashbuild-secbuild-2.4.3.g4cd89c9",
                "org.label-schema.build-size": "266MB"
            },
            "environment": "# Custom environment shell code should follow\n\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n",
            "runscript": "#!/bin/sh \n\nexec /bin/bash /rawr.sh\n",
            "test": null
        },
        "type": "container"
    }
}
[container][new] library/vsoch-hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
Requesting transfer from local /home/vanessa/.singularity/shub to 6881ae2e-db26-11e5-9772-22000b9da45e:.singularity/shub/vsoch-hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d.simg
The transfer has been accepted and a task has been created and queued for execution
```
In the above command, we are lazy and instead of getting the long name of the image, we just
use sregistry to get it. You should then be able to go to [https://www.globus.org/app/activity](https://www.globus.org/app/activity) to see the transfer!

![/img/globus-activity.png](/img/globus-activity.png)

If you get this error:

```bash
sregistry push $(sregistry get vsoch/hello-world) --name 6881ae2e-db26-11e5-9772-22000b9da45e
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
ERROR No activated local endpoints online! Go online to transfer
```

Then you need to start your endpoint!

```bash
$ /home/vanessa/Documents/globusconnectpersonal-2.3.3/globusconnectpersonal -start &
```

And you don't actually need to push again - the errored job stays in your queue and is run
when you are back online.

Now we can again look at the endpoint with search... did it show up?

```bash
$ sregistry push $(sregistry get vsoch/hello-world) --name 6881ae2e-db26-11e5-9772-22000b9da45e:.
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Endpoint Listing .singularity/shub 
1  type	[perm]	[size]	[name]
2  file	0644	616017951	sherlock_vep-master-latest.simg
3  file	0644	65028127	vsoch-hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d.simg
```

It sure did!

### Push from Anywhere
Let's push another one, and call it something different. Here is a container on our
Desktop, it's not even in our local Singularity Registry.


```bash
$ sregistry push pancakes.simg --name 6881ae2e-db26-11e5-9772-22000b9da45e
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
.singularity/shub already exists at endpoint
2.4.2-fix/docker-env.g69a088b
{
    "data": {
        "attributes": {
            "deffile": "Bootstrap: docker\nFrom: vanessa/scif\n\n# sudo singularity build color.simg Singularity\n# ./color.simg shell color\n\n%post\n\necho \"%appenv color\n    export SHELL=/bin/bash\n    export alias ls='ls --color=auto'\" >> /recipe.scif\n\n/opt/conda/bin/scif install /recipe.scif\n",
            "help": null,
            "labels": {
                "org.label-schema.usage.singularity.deffile.bootstrap": "docker",
                "org.label-schema.usage.singularity.deffile": "Singularity.test",
                "org.label-schema.schema-version": "1.0",
                "org.label-schema.usage.singularity.deffile.from": "vanessa/scif",
                "org.label-schema.build-date": "Wed,_14_Mar_2018_15:32:10_-0400",
                "org.label-schema.usage.singularity.version": "2.4.2-fix/docker-env.g69a088b",
                "org.label-schema.build-size": "1569MB"
            },
            "environment": "# Custom environment shell code should follow\n\n",
            "runscript": "#!/bin/sh\n\nexec \"scif\" \"$@\"\n",
            "test": null
        },
        "type": "container"
    }
}
[container][new] library/pancakes:latest
Requesting transfer from local /home/vanessa/.singularity/shub to 6881ae2e-db26-11e5-9772-22000b9da45e:.singularity/shub/pancakes.simg
The transfer has been accepted and a task has been created and queued for execution
```

Did you notice anything? The container wasn't in our local storage, so we added it! This
means that you could pull a container from Docker Hub (or else where) and then make
changes and push to globus, and you will also save it in your local Singularity Registry
database. Cool!


## Pull
Now that we have containers on our endpoint, we might want to get them back, right?
You will likely need to first figure out the endpoint id with `search`, look at the
containers there (also with `search`) and then push (with `push`!).

```
# Find the endpoint id we want with scope "all" and search term "srcc"
$ sregistry search srcc

# Look in the singularity cache folder of the endpoint
$ sregistry search --endpoint 6881ae2e-db26-11e5-9772-22000b9da45e:.singularity/shub

# Then pull something we find there!
$ sregistry pull 6881ae2e-db26-11e5-9772-22000b9da45e:.singularity/shub/pancakes.simg

```
the result will tell us that the task is in the queue:

```
sregistry pull 6881ae2e-db26-11e5-9772-22000b9da45e:.singularity/shub/pancakes.simg
[client|globus] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
/home/vanessa/.singularity/shub/sherlock already exists at endpoint
Requesting transfer to sherlock/pancakes:latest.simg
The transfer has been accepted and a task has been created and queued for execution
```

When it is finished, we will find it in our Singularity Registry cache (`$HOME/.singularity/shub`)
under the path specified, `sherlock/pancakes:latest.simg`. Here is where the database is
imperfect - we can pull it to the endpoint, but since we don't know when it will show up, we don't
have a message or notification when it's there. So you will likely want to add it after you
get a successful transfer message. You can also use this as an opportunity to rename the image:

```
$ sregistry add --name sherlock/better-pancakes /home/vanessa/.singularity/shub/sherlock/pancakes\:latest.simg
```

This is the first implementation of Globus, and if you have feedback please <a href="https://www.github.com/singularityhub/sregistry-cli/issues" target="_blank">let us know!</a>

<div>
    <a href="/sregistry-cli/client-google-storage"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-registry"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
