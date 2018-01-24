---
layout: default
title: Docker Hub Client
pdf: true
permalink: /client-nvidia
toc: false
---

# SRegistry Client: Nvidia Container Registry

These sections will detail use of the Nvidia Container Cloud client for `sregistry`, which is a connection to the Docker registry served y Nvidia. Implementation wise, this means that we start with the basic [docker](/sregistry-cli/client-docker) client, and tweak it.

## Why would I want to use this?
Singularity proper will be the best solution if you want to pull and otherwise interact with Docker images. However, the Nvidia Container Cloud uses a slightly different authentication protocol (use of `$oauthtoken` as a username, and password as an API token, and so this client helps to support those customizations.

As with [Docker Hub](/sregistry-cli/client-docker) The images are built from layers, and the layers that you obtain depend on the uri that you ask for, along with the host architecture and operating system. See the [environment](#environment). setting for more details.

## Getting Started
The Nvidia Container Registry module does not require any extra dependencies other than having Singularity on the host.

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
|SREGISTRY_NVIDIA_TOKEN  | None (required)        | Your API token associated with your account, generated [here](https://ngc.nvidia.com/configuration/api-key)|
|SREGISTRY_NVIDIA_BASE | ngcr.io           | the api base (default is ngcr.io) |
|SREGISTRY_NVIDIA_VERSION | v2           | the version of the API to use (default is v2) |
|SREGISTRY_NVIDIA_USERNAME | $oauthtoken           | if the username could be different, set it here (defaults to $oauthtoken) |
|SREGISTRY_NVIDIA_NOHTTPS | not set        | If found as yes/t/true/y or some derivation, make calls without https (usually for local registries and not recommended)  

The following variables are *shared* between different `sregistry` clients that have a Docker registry backend.

| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SREGISTRY_DOCKER_OS       | linux          | The choice of operating system to use from the schema version 2 image manifest |
|SREGISTRY_DOCKER_ARCHITECTURE| amd64       | the system architecture to use from the schema verison 2 image manifest
|SREGISTRY_DOCKER_CMD |     not set         | If found as yes/t/true/y or some derivation, use "CMD" instead of "EntryPoint" for container runscript|


The following variables are relevant for clients that use multiprocessing:

| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SREGISTRY_PYTHON_THREADS       | 9          | The number of workers (threads) to allocate to the download client |


The following variables are specific to Singularity (not the Singularity Registry Global Client) and honored during any pull of Docker layers:

| Variable                    |        Default |          Description |
|-----------------------------|----------------|----------------------|
|SINGULARITY_CACHEDIR  | `$HOME/.singularity`           | Set the root of the cache for layer downloads |
|SINGULARITY_DISABLE_CACHE  | not set               | Disable the Singularity cache entirely (uses temporary directory) |


#### Authentication
You should first export your secret token for the api:

```
SREGISTRY_NVIDIA_TOKEN = "xxxxxx"
export SREGISTRY_NVIDIA_TOKEN
```

If you don't, you won't get very far!


```
SREGISTRY_CLIENT=nvidia sregistry shell
ERROR You must have an Nvidia GPU cloud token to use it.
```

Once you export your token (and increase the message level) you can see that there is an Authentication header added to the client:

```
MESSAGELEVEL=5 SREGISTRY_CLIENT=nvidia sregistry shell
DEBUG credentials cache
DEBUG Headers found: Content-Type,Accept,Authorization
DEBUG Database located at sqlite:////home/vanessa/.singularity/sregistry.db
[client|nvidia] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
ePython 3.5.2 |Anaconda 4.2.0 (64-bit)| (default, Jul  2 2016, 17:53:06) 
...
```

## Commands
For a detailed list of other (default) environment variables and settings that you can configure, see the [getting started](../getting-started) pages.  For the globally shared commands (e.g., "add", "get", "inspect," "images," and any others that are defined for all clients) see the [commands](../getting-started/commands.md) documentation. Here we will review the set of commands that are specific to the Nvidia Container Registry client:

 - [pull](#pull): `[remote->local]` pull layers from Docker Hub to build a Singularity images, and save in storage.
 - [record](#record): `[remote->local]` obtain Docker Hub manifests and metadata to save to the database, but don't pull layers to build a container.

For all of the examples below, we will export our client preference to be `nvidia`

```
SREGISTRY_CLIENT=nvidia
export SREGISTRY_CLIENT
```

but note that you could just as easily define the variable for one command (as we did above):

```
SREGISTRY_CLIENT=nvidia sregistry shell
```

## Shell
After we have exported `SREGISTRY_CLIENT` above, if you are looking to interact with a shell for the Nvidia Container Registry `sregistry` client, just ask for it:

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

In [1]: 
```

## Pull
The most likely action you want to do is to pull. Pull in this context is different than a pull from Singularity Registry, because we aren't pulling an entire, pre-built image - we are assembling layers at pull time and building an image with them. Specifically we:

 1. **obtain image manifests from a Docker registry served by Nvidia** based on an image unique resource identifier (uri) e.g., `tensorflow:17.10`. Currently, the image manifests we look for are schemaVersion 1 and 2. Version 1 has important metadata relevant to environment, labels, and the EntryPoint and Cmd (what Singularity will use as the runscript). Version 2 has sizes for layers, and in some cases returns a list of manifests that the user (you!) can choose based on selecting an operating system and system architecture. If you do a simple record (and not pull) it's these manifests that will be obtained and stored in your database.

 2. **download layers into a sandbox** and build a squashfs image from the sandbox (per usual with Singularity, build is recommended to do using sudo). The client will detect if you are running the command as sudo (user id 0) and adjust the command to singularity appropriately.
 3. **add the image** to your local storage and sregistry manager so you can find it later.

If you are interested in seeing how to ask for a particular architecture or operating system (given that the image provides it) please see the [environment](#environment). setting for more details. Here is an example of using the Docker Hub `sregistry` client.

```
sregistry pull tensorflow:17.11
[client|nvidia] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[1/6] ||----------------------------------|   0.0%
Progress |===================================| 100.0% 
Progress |===================================| 100.0% 
Progress |===================================| 100.0% 
...
Progress |===================================| 100.0% 
Progress |===================================| 100.0% 
Progress |===================================| 100.0% 
[6/6] |===================================| 100.0% 
Exploding /usr/local/libexec/singularity/bootstrap-scripts/environment.tar
Exploding /home/vanessa/.singularity/docker/sha256:4fa80d7b805d323b3296c28d3a585c827a7cb1a8cbeb59025f63a42f61702edc.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:484dd0f2fbdc3aef130768e63a3f109d78665267a5fdad9d13f72cc1f7e3ca8b.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:47004b22ec620cce9a94e5acbec229d1d12a2dd2dbcd0b3cec3c92e667d85bc5.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:b70745c852a25dd5eb90a47b01117efe777d7541572d17d6fb62cdf0c3a5d3c0.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:718060832ef2f022ecb3bfca72beecd10d046eec02f2faec61da0ab8abe906b4.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:16f3012c3b223a28aab26c9424115754ffa181fe49b0965cf1f0283fa1c524dc.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:8f2b470a5af39f76c4b149724208bb5097d57414ab7e47ddf09e856dfddec2e8.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:c8738138ecbfab29095a4c638ab047528c4fab7e35a48854454d20b50670481f.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:8ce63c97503f009c70f7398a0fcc71c790d036b56b9e281ddd62cb801b7f455e.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:4d9ead04c4f2d670cd577aec135489e59c9d4bdf8e090b0e3b84bbad6d4bb505.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:c35392c413d6ea794525715b50badddbb7fa332ccaa6c983b769ada1157b1b77.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:b79da51ea9de5c94351ba76e3b36a9ba58ee87ff8b292db60c03c56942434d30.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:a26b77f3a1b713137850afc687645e8f874bf8975f74ffb8b4d29beb88bab972.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:109dd7ecfe28ef977dcafb59246238593cb3a56bbb8ae82add857e0b28b84a67.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:8e02d087ca1121cb88e27aa6ad81942841dcfc5fc1fb37d081106382e36361b0.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:884cce72a8c53aebebb7efbc2d0fe1bab7c3a8d2b0d032009e4d30b1225561f0.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:b16d4d5b02be1207016cca519ad618a41c510fa927b811a2df94f54129e6b731.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:0a191fd6641294fdfcc0001afb6bb1f25dbad22e5d139da87ed81c37f6bb14a0.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:94adc164edc321af880411448a764a76761527c0d623da7e3623c9be43a8de44.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:d283606c9c78a7e77e7323de059a915ab2cef330c7ca7c69ee8d73eb384039db.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:3f2000d401e21f24b646a85c576feffbab0e54a3c5ccc9df4f3d57626d7dbbcb.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:36848e9e524ea7a102f974f3e6640129fd34dd79d7353938c1aaf934ff0ee17c.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:aae77cc86f9900cb87793f91dbeecf05931c528b50b18ce036b47cab740631ac.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:d58370fea5e761a06c08a40a6f4406864d9eac12cb8d93b1d3faf074da935471.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:89f8c62a112ff73ab6030daf5cf3d543c6b9098a3d0d8c1e724023eccf6f895b.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:2d9b8c51408033989dbef6d9943b328c7297c5ff5e2d7af5372ec676b2d6ff21.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:feebeefb36547c6072274440704db4665e41972a972016a15c31e5e7cb65a394.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:ec2a56d3d2d14d8da35643b85e883849566d2a0e2203b79cb0e8389831dd2cfe.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:d6541b6ed7852d23260488be2d4d2b224c59950579396e63093094f43fe705f9.tar.gz
Exploding /home/vanessa/.singularity/docker/sha256:438c302223eb8688f0dce8326ce7fbeec2d9b51520763a899878622756e2349a.tar.gz
Exploding /home/vanessa/.singularity/docker/metadata/sha256:76ad0968c61d5a8db57df5a165e0432a9da78a74cc70d7c162311af764196994.tar.gz
WARNING: Building container as an unprivileged user. If you run this container as root
WARNING: it may be missing some functionality.
Building FS image from sandbox: /tmp/tmpdwhl5ahf
Building Singularity FS image...
Building Singularity SIF container image...
Singularity container built: /home/vanessa/.singularity/shub/nvidia-tensorflow:17.11.simg
Cleaning up...

[container][new] nvidia/tensorflow:17.11
Success! /home/vanessa/.singularity/shub/nvidia-tensorflow:17.11.simg
```

Notice that the first layer extracted is the standard environment metadata tar. The next set of layers come from the user's default cache (either set as the Singularity default or a user specified, we honor the Singularity envionment variable settings for this, and use a temporary directory if it's disabled. The final layer is a metadata tar that is specifically for the runscript, environment, and labels (if found in the manifest). After you do a pull, you can see the record in your local database (see the last record):

```
sregistry images
[client|docker] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers:   [date]   [location]  [client]	[uri]
1  December 29, 2017	local 	   [google-drive]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
2  December 30, 2017	remote	   [google-storage]	expfactory/expfactory:metadata@846442ecd7487f99fce3b8fb68ae15af
3  December 30, 2017	local 	   [google-storage]	vsoch/avocados:tacos@ed9755a0871f04db3e14971bec56a33f
4  January 01, 2018	local 	   [google-drive]	expfactory/expfactory:master@846442ecd7487f99fce3b8fb68ae15af
5  January 01, 2018	remote	   [google-drive]	vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f
6  January 09, 2018	local 	   [registry]	mso4sc/sregistry-cli:latest@953fc2a30e6a9f997c1e9ca897142869
7  January 14, 2018	local 	   [docker]	library/ubuntu:latest@f8d7d2e9f5da3fa4112aab30105e2fcd
8  January 15, 2018	local 	   [nvidia]	nvidia/tensorflow:17.11@16765f12b73ec77235726fa9e47e808c
```

## Record
We can do the same action as above, but without the download! You might want to grab metadata for an image but not pull and download layers. You can use record for that. Let's first get the record for another version of caffe:

```
sregistry record caffe2:17.10
[client|docker] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container][new] continuumio/anaconda3:latest
```

It's a really quick action, because all we've done is obtained the manifests. If you do it a second time, you
update the existing record:

```
sregistry record caffe2:17.10
[client|nvidia] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container][update] nvidia/caffe2:17.10
```

## Images
We can see the record in our images list (last one):

```
sregistry images
[client|docker] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers:   [date]   [location]  [client]	[uri]
1  December 29, 2017	local 	   [google-drive]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
2  December 30, 2017	remote	   [google-storage]	expfactory/expfactory:metadata@846442ecd7487f99fce3b8fb68ae15af
3  December 30, 2017	local 	   [google-storage]	vsoch/avocados:tacos@ed9755a0871f04db3e14971bec56a33f
4  January 01, 2018	local 	   [google-drive]	expfactory/expfactory:master@846442ecd7487f99fce3b8fb68ae15af
5  January 01, 2018	remote	   [google-drive]	vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f
6  January 09, 2018	local 	   [registry]	mso4sc/sregistry-cli:latest@953fc2a30e6a9f997c1e9ca897142869
7  January 14, 2018	local 	   [docker]	library/ubuntu:latest@f8d7d2e9f5da3fa4112aab30105e2fcd
8  January 15, 2018	local 	   [nvidia]	nvidia/tensorflow:17.11@16765f12b73ec77235726fa9e47e808c
9  January 15, 2018	remote	   [nvidia]	nvidia/caffe2:17.10
```

## Inspect
And we can inspect it!

```
sregistry inspect nvidia/caffe2:17.10
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

<div>
    <a href="/sregistry-cli/google-drive"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-hub"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
