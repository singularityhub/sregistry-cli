---
layout: default
title: Google Compute Builder Detailed Start
pdf: true
permalink: /client-google-compute-detail
toc: true
---

# Google Compute Builder

This is the detailed start for the Google Compute Builder. For a quick
start, see the [previous page](/sregistry-cli/client-google-compute). If you are looking
to use the library from within python, see our [Development Tutorial](/sregistry-cli/client-google-compute-developer).


## Detailed Start
You will need to install some of the Google API Client libraries, and you can do that as follows:

```
pip install sregistry[google-compute]

# or locally
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli
pip install -e .[google-compute]
```

This command will install the python modules for both interacting with Google Compute
and Google Storage. Compute is needed for deploying the builders, and Storage is
needed for interacting (and retrieving) the results.

## Overview
For the Google Compute Builder, we are going to do the following:

 - Deploy a compute instance with your build settings of choice. The build will be based on a Github repository to ensure version control of the inputs.
 - The builder will perform the build, and upload to Google Storage
 - You can pull the final result.

The builder templates, called **builder bundles** are from a [community maintained library](https://singularityhub.github.io/builders/) that you can use as is, or customize with particulars about the build environment. 
We will first review environment variables, followed by our tutorial walk throughs noted above. You can skip down to [Build](#build) if you are impatient.


### Required Environment
The tools served by `sregistry` work way of obtaining information from the environment. For the Google Compute Builder you need the same base of information as for using the [Google Storage Client](/sregistry-cli/client-google-storage). You will first need to [set up authentication](https://cloud.google.com/docs/authentication/getting-started) by following those steps. It comes down to creating a file and saving it on your system with the variable name `GOOGLE_APPLICATION_CREDENTIALS`. This variable will be found and used every time you use the Google Compute Builder, without needing to save anything to the secrets. Thus, the minimum required environment variables that you need to set (meaning they are required and have no defaults) are the following:

| Variable | Default | When is it used? | Description |
|----------|---------|------------------|-------------|
| [GOOGLE_APPLICATION_CREDENTIALS](https://cloud.google.com/docs/authentication/getting-started) | Not set | When you issue commands to work with Google Cloud APIs | This is a json file on your host that authenticates you with Google Cloud |
| SREGISTRY_COMPUTE_PROJECT | Not set | On the host and builder to specify your project | This is the name of your Google Cloud Project |

Beyond the credentials, the [builders use reasonable defaults](https://singularityhub.github.io/builders/environment) for most things, and you able to customize any or all of these by defining them in your config.json file. We will discuss these along with optional variables for build setup and runtime in more detail [later in this document](#optional-environment).


## Client
The backend of the builder is an extended google storage client, and the only distinction
is that to perform the install, you needed an extra python library. For usage, you can
set the client to be `google-compute` or `google-storage`. For all of the 
examples below, we will export our client preference to be `google-compute`

```
SREGISTRY_CLIENT=google-compute
export SREGISTRY_CLIENT
```
and note that you could just as easily define the variable for one command:

```
SREGISTRY_CLIENT=google-compute sregistry shell
```

## Build
After we have exported `SREGISTRY_CLIENT` above, let's familiarize with how we
are going to build. 

```
$ sregistry build --help
usage: sregistry build [-h] [--preview] [--name NAME] [--config CONFIG]
                       [commands [commands ...]]

positional arguments:
  commands         RUN: build [repo] [recipe] [config] ----------------------
                   ALL templates: build templates -------------------------
                   GET template: build templates [template] ---------------
                   LIST instances: build instances --------------------------
                   GET logs: build logs [name] ---------------

optional arguments:
  -h, --help       show this help message and exit
  --preview, -p    preview the parsed configuration file only.
  --name NAME      name of image, in format "library/image"
  --config CONFIG  specify a config file or uri
```

We can see that the build command let's use specify a build command (the positional arguments),
for a given image name (`--name`), interact with instances (`--list`), 
preview a configuration for an instance (`--preview`). We will show examples of all
the commands and actions you would want to do.

### Templates

```
$ sregistry build templates
1  /cloud/google/compute/ubuntu/securebuild-2.4.3.json
```

Specifically, the id of the templates listed above refers to the path in the
[builder bundle Github repository](https://www.github.com/singularityhub/builders) in the "_cloud" 
folder. We could then retrieve that particular template,  and pipe it into a file:

```
$ sregistry build templates cloud/google/compute/ubuntu/securebuild-2.4.3.json > config.json
```

At this point you would likely open up the config.json file, and edit to your needs.


### Build
The only requirement for build is a Github repository, to ensure that you have your work in version
control.


#### Provide Github Repo
If you want to use a default recipe `Singularity` in the base of the Github repository,
and are also happy with the repository name as the container's uri (e.g., `vsoch/singularity-images`
and are happy using the default configuration for Google Compute, then you only need to give
the builder the name of the Github repository:

```
$ sregistry build https://www.github.com/vsoch/singularity-images
```

The above will build a container `vsoch/singularity-images:latest` from the file 
`Singularity` in the repository.


#### Github Repo and Recipe
If you provide two arguments, the second refers to the path (relative to the repository base)
of the Singularity recipe:

```
$ sregistry build https://www.github.com/singularityhub/hello-registry os/ubuntu/Singularity.14.04 
```

This will build the image `singularityhub/hello-world` with tag `14.04` from the recipe file
`os/ubuntu/Singularity.14.04` in the repository. It's useful to type out this path from the
repo on your local machine so by the time it gets to the builder and clones, we know where to find it!

#### Custom Name
If you want to customize the name of the final image, you can set it with `--name`. If you
set a tag here, this takes preference over the file extension.

```
$ sregistry build --name vanessa/tacos:avocado https://www.github.com/vsoch/singularity-images
```

#### Custom Config
You most likely will want to generate a custom configuration (as instructed with build templates commands
above) to control your build. You can provide it to the build command as follows:

```
$ sregistry build https://www.github.com/vsoch/singularity-images --config config.json
```

When you issue the command above, you will launch a builder and get back an ip address
that you can visit to track his progress.


### Instances
Once we issue a build command, we likely want to interact with our instances! First,
check on the status by listing instance for your project:

```
$ sregistry build instances
[google-compute] Found 8 instances
1  instance-1	RUNNING
2  phs-ubuntu-1610	RUNNING
3  singularity-hub-postgres	TERMINATED
4  singularity-hub-postgres-hot	TERMINATED
5  singularity-hub-test	TERMINATED
6  vsoch-hello-world-builder	RUNNING
7  wglurp-ldap-dev	TERMINATED
8  wglurp-ldap-dev-2	RUNNING
```

### Storage
What about when you have a container finished? You can use `search` to list the containers in your storage!

```
sregistry search
[client|google-compute] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
[gs://sregistry-vanessa] Containers
1       62 MB	vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
```

This works by looking for the metadata of `type:container`. If you have a container of interest,
you can further look at the (high level) metadata by just adding the uri:

```
sregistry search vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
[client|google-compute] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
[gs://sregistry-vanessa] Found 1 containers
github.com/vsoch/hello-world/master/3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d/36b34e5b8da824e271f09c691e9002518e355dd981d99e7de934cb0a5a6b7f6e:latest.simg 
id:      sregistry-vanessa/github.com/vsoch/hello-world/master/3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d/36b34e5b8da824e271f09c691e9002518e355dd981d99e7de934cb0a5a6b7f6e:latest.simg/1521441991052885
uri:     vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
updated: 2018-03-19 06:46:31.040000+00:00
size:    62 MB
md5:     eS1GnjAyo558EwtuLvHxVQ==
```


### Pull
Once you've built and see your container in storage, you can pull it.

```
$ sregistry pull vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
sregistry pull vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
[client|google-compute] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
Searching for vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d in gs://sregistry-vanessa
Progress |===================================| 100.0% 
[container][new] vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
Success! /home/vanessa/.singularity/shub/vsoch-hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d.simg
```

And guess what? The metadata generated for your container during build is saved with it.

```
$ sregistry inspect vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
```

And of course, run it :)

```
$ singularity run $(sregistry get vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d)
RaawwWWWWWRRRR!! Avocado!
```
You have to watch out for these containers, they eat all the avocados!

If you are interested to read more about the local commands for the Google Storage client,
continue reading about the [Google Storage](/sregistry-cli/client-google-storage) client.


## Optional Environment
These variables are relevant to deployment of the builder itself. While they aren't required, it's recommended to look them over to see if you want to change any defaults. You can further customize your Singularity Builder by setting the following environment variables. Keep in mind that for a subset of these (e.g., the storage bucket name) that are unlikely to change, they will be cached in your secrets at `$HOME/.sregistry`. This is great because you would only need to specify it once, but not ideal if you have a different use case than the developers of the software anticipated.


| Variable | Default | Description |
|----------|---------|------------|
| [SREGISTRY_GOOGLE_STORAGE_BUCKET](https://cloud.google.com/storage/docs/json_api/v1/buckets) | `sregistry-$USER`| the Google Cloud Storage bucket in your project |
| `SREGISTRY_GOOGLE_STORAGE_PRIVATE` | not set (False) | upload private images to Google Storage |
| `SREGISTRY_COMPUTE_ZONE` | `us-west1-a` | The zone to deploy the instance to. [docs](https://cloud.google.com/compute/docs/regions-zones/) |
| `SREGISTRY_COMPUTE_CONFIG` | `cloud/google/ubuntu/secbuild-2.4.1.json` | The build configuration for Google Compute Engine. This variable can refer to a file on the host, or a build configuration id associated with a path in the `SREGISTRY_BUILDER_REPO` | 
| `SREGISTRY_BUILDER_machine_type` | `n1-standard-1`| The Google Compute Instance type, with [options described here](https://cloud.google.com/compute/docs/machine-types) |
| `GOOGLE_COMPUTE_PROJECT` | `debian-project` |  The project that has a family of images to select your instance from |
|`GOOGLE_COMPUTE_IMAGE_FAMILY`| `debian-8` | The default image to use for the builder |

Notice the last two images for the Google Compute Project and Family? If you want faster builds, or to further customize your instance, you can generate images in advance with things ready to go, and then specify them here. This is how we configure the Singularity Hub builders so building starts immediately without waiting to install and compile Singularity.

And don't forget to take a peek at the [builder's environment space](https://singularityhub.github.io/builders/environment) too. You can customize many things!


<div>
    <a href="/sregistry-cli/client-google-compute"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-compute-developer"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
