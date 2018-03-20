---
layout: default
title: Singularity Google Compute Builder
pdf: true
permalink: /client-google-compute
toc: true
---

# Singularity Google Compute Builder

The Google Compute Builder is the first builder offered by the `sregistry` client! Using your Google Cloud
project you can deploy builds to Google Compute Engine and then have images saved in Google Storage. This
in essence is a mini "Singularity Hub" that you have complete control over. For the command line usage, continue
reading the Getting Started below. For interaction within Python, see the [Developer Tutorial](#developer-tutorial) 
below.

## Quick Start
For the quickstart you need your `GOOGLE_APPLICATION_CREDENTIALS` and `GOOGLE_CLOUD_PROJECT` export to the environment, and `sregistry` installed.

```
# Export credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-secrets.json
export GOOGLE_CLOUD_PROJECT=vanessasur-us
export SREGISTRY_CLIENT=google-compute

# Install
$ pip install sregistry[google-compute]
```
```
# View Templates
$ sregistry build templates

# Save a template to customize
$ sregistry build templates /cloud/google/compute/ubuntu/securebuild-2.4.3.json > config.json

# Build with a repo with Singularity recipe in root
$ sregistry build https://www.github.com/vsoch/hello-world 

# Preview a Configuration for the same (don't launch builder)
$ sregistry build --preview https://www.github.com/vsoch/hello-world

# List instances
$ sregistry build instances

# List containers in storage
$ sregistry search

# Get detailed metadata for remote
$ sregistry search vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d

# Pull a container
$ sregistry pull vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d

# Look at images from compute locally
$ sregistry images | grep google-compute

# Look at metadata for local
$ sregistry inspect vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d

# Look at latest log
$ sregistry build logs

# Look at specific logs
$ sregistry build logs vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d

# Run it!
$ singularity run $(sregistry get vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d)
RaawwWWWWWRRRR!! Avocado!
```

## Detailed Start Started
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


| Variable | Default | When is it used? | Description |
|----------|---------|------------------|-------------|
| [SREGISTRY_GOOGLE_STORAGE_BUCKET](https://cloud.google.com/storage/docs/json_api/v1/buckets) | `sregistry-$USER` | on your machine to create and query containers, and by the builder to upload finished | the Google Cloud Storage bucket in your project |
| `SREGISTRY_GOOGLE_STORAGE_PRIVATE` | not set (False) | build time | by default, images that you upload will be made public, meaning that a user that stumbles on the URL (or has permission to read your bucket otherwise) will be able to see and download them. If you want to make an image private (one time or globally with an export in your bash profile) you should export this variable as some derivative of yes/true. If no variable is found, images are made public by default. If you set the variable once, it will be saved in your configuration for all subsequent images. |
| `SREGISTRY_COMPUTE_ZONE` | `us-west1-a` | At setup to choose a zone for your instance. | The zone to deploy the instance to. [docs](https://cloud.google.com/compute/docs/regions-zones/) |
| `SREGISTRY_COMPUTE_CONFIG` | `cloud/google/ubuntu/secbuild-2.4.1.json` | The build configuration for Google Compute Engine | It is used when setting up the build on the user's machine | This variable can refer to a file on the host, or a build configuration id associated with a path in the `SREGISTRY_BUILDER_REPO`. In both cases, a json config.json is found and loaded to set up the builder. | 
| SREGISTRY_BUILDER_machine_type | `n1-standard-1`| Sent to Google Cloud APIs to deploy the instance | The Google Compute Instance type, with [options described here](https://cloud.google.com/compute/docs/machine-types) |
| GOOGLE_COMPUTE_PROJECT | `debian-project` |  To get the path to the actual image of your instance, you must provide a project and family. This is the project for debian. | The project that has a family of images to select your instance from |
|GOOGLE_COMPUTE_IMAGE_FAMILY| `debian-8` | To find the instance image link from the family at setup time. | The default image to use for the builder |

Notice the last two images for the Google Compute Project and Family? If you want faster builds, or to further customize your instance, you can generate images in advance with things ready to go, and then specify them here. This is how we configure the Singularity Hub builders so building starts immediately without waiting to install and compile Singularity.

And don't forget to take a peek at the [builder's environment space](https://singularityhub.github.io/builders/environment) too. You can customize many things!


## Developer Tutorial
You might want to integrate the global client into your software to run custom builds. You can do this!

### 1. Start the Client
We will be using the interactive shell, started as follows, to do this:

```
SREGISTRY_CLIENT=google-compute sregistry shell
[client|google-compute] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
```

and note that if you wanted to do this from scratch, you could do:

```
from sregistry.main import get_client
client = get_client('google-compute')
```

You will also want to export your `SREGISTRY_GOOGLE_PROJECT` to be found in the environment.
If you don't, you'll run a command and see this error:

```
ERROR Export your SREGISTRY_GOOGLE_PROJECT to build.
```

After exporting and opening a shell with one of the methods above, let's start 
by defining a repository with Singularity build recipes, and using the default
provided by the client, `Singularity`.

```
repo = 'https://www.github.com/vsoch/singularity-images'
recipe = "Singularity"
```

### 2. Familiarize with Build

The client "build" command can accept the following arguments:

 - `repo`: (required) the Github url to the repository with Singularity recipe files to build!
 - `config` an actual json format file OR an id associated with the path in the [builders repo](https://www.github.com/singularityhub/builders). Given that we are using Google Compute, the configuration file must match the format to deploy an instance, with the primary start_script corresponding to what the instance does at start up.
 - `recipe` the Singularity recipe file **within the Github repository**
 - `preview`: if True, will return the config without launching a build.

### 3. Create a config template
We will use preview to get the config and walk through what (would happen) if done automatically.
First, the way that we retrieved our config file can also be done from within Python:

```
$ configs = client._get_templates()
{'data': [{'author': 'Vanessa Sochat',
   'id': 'https://singularityhub.github.io/builders/cloud/google/compute/ubuntu/securebuild-2.4.3.json',
   'name': '/cloud/google/compute/ubuntu/securebuild-2.4.3.json',
   'tags': ['ubuntu', 'singularity', 'google-compute', 'google-storage']}],
 'links': {'self': 'https://singularityhub.github.io/builders/configs.json'}}
```

There is only one right now, since this is under development! To load it (if
this were run on the command line) we use the function `_load_build_config` with the name:

```
$ config = client._load_build_config('cloud/google/compute/ubuntu/securebuild-2.4.3.json')
```

and the config is loaded:

```
{'data': {'author': 'Vanessa Sochat',
  'config': {'disks': [],
   'labels': [{'key': 'sregistry', 'value': 'builder'}],
   'networkInterfaces': [{'accessConfigs': [{'name': 'External NAT',
       'type': 'ONE_TO_ONE_NAT'}],
     'network': 'global/networks/default'}],
   'serviceAccounts': [{'email': 'default',
     'scopes': ['https://www.googleapis.com/auth/compute',
      'https://www.googleapis.com/auth/devstorage.read_write',
      'https://www.googleapis.com/auth/logging.write']}],
   'tags': {'items': ['http-server', 'https-server']}},
  'id': '/cloud/google/compute/ubuntu/securebuild-2.4.3',
  'metadata': {'GOOGLE_COMPUTE_IMAGE_FAMILY': 'debian-8',
   'GOOGLE_COMPUTE_PROJECT': 'debian-cloud',
   'SINGULARITY_BRANCH': 'feature-squashbuild-secbuild-2.4.3',
   'SINGULARITY_REPO': 'https://github.com/cclerget/singularity.git',
   'SREGISTRY_BUILDER_machine_type': 'n1-standard-1',
   'SREGISTRY_GOOGLE_STORAGE_PRIVATE': 'false'},
  'path': '_cloud/google/compute/ubuntu/securebuild-2.4.3.json',
  'repo': 'https://www.github.com/singularityhub/builders',
  'tags': ['ubuntu', 'singularity', 'google-compute', 'google-storage']},
 'links': {'self': 'https://singularityhub.github.io/builders_cloud/google/compute/ubuntu/securebuild-2.4.3.json'}}
```

The subtle distinction is that this function will load a URI OR a file. This means
that we could have done following:

```
$ client._load_build_config('config.json')
```

You can check the zone and project enabled:

```
$ client._get_zone()
'us-west1-a'

$ client._get_project()
...
```

Now let's say we want to preview the Google Instance Configuration that would be generated
from our config? We can run build, and specify preview to be True. Note that when run from
the client, the config goes in as a string (either a URI or a file) and in this case we 
are going to try and break that by giving it a dictionary. This will actually turn out ok,
all three of these cases work. You might want to load a config and edit it programatically
before use, or loop over a set of config files instead.

```
$ config = client._load_build_config('config.json')
$ client.build(repo='https://www.github.com/vsoch/hello-world',
               recipe="Singularity",
               preview=True)

Found config google/compute/ubuntu/securebuild-2.4.3 in library!

...
{'description': 'vsoch-hello-world-builder https://singularityhub.github.io/builders_cloud/google/compute/ubuntu/securebuild-2.4.3.json',
 'disks': [{'autoDelete': True,
   'boot': True,
   'initializeParams': {'diskSizeGb': '100',
...
```

Notice how we **didn't** specify a config, and it gave us a good default? Note
that if the repository isn't found (success for Github is indicated by a 200 or 301, redirect response) 
you will get an error that it isn't healthy. It's better to figure this out before launching a builder!

```
$ client.build(repo='https://www.github.com/tacos/i-dont-exist',
               recipe="Singularity",
               preview=True)
ERROR https://www.github.com/tacos/i-dont-exist, response status code 404.
```

If you see this error:

```
ERROR Cannot get or create sregistry-vanessa
```

It means that we couldn't create or get the bucket. This usually means that:
 - your project isn't exported as `GOOGLE_CLOUD_PROJECT`
 - your credentials file is not exported as `GOOGLE_APPLICATION_CREDENTIALS` 
 - the credentials exported aren't for that Google Project!
 - the bucket name is already owned by someone else, try exporting `SREGISTRY_GOOGLE_STORAGE_BUCKET`

If you have several Google Cloud Project spaces it is easy to create a bucket in one, and then
not be able to access it from a different project.

### 4. Run the build!
Now we can launch the build!

```
$ response = client.build(repo='https://www.github.com/vsoch/hello-world')
Found config google/compute/ubuntu/securebuild-2.4.3 in library!
Inserting carniverous-fork-0369 to build vsoch-hello-world-builder https://singularityhub.github.io/builders_cloud/google/compute/ubuntu/securebuild-2.4.3.json
```

In the above command, note that a lot of hidden argument defaults were used:

```
   # Optional Arguments ----------------
   # config [default]google/compute/ubuntu/securebuild-2.4.3
   # recipe [default]Singularity at repository root)
   # branch [default]master
   # name   e.g., vsoch/hello-world
   # commit current
   # tag    [default]latest unless provided in name
```

We can look at the response to see the status of the instance

```
$ response
{'id': '1397962134226444746',
 'insertTime': '2018-03-18T01:11:17.701-07:00',
 'kind': 'compute#operation',
 'name': 'operation-1521360676388-567ab62b0fca0-fe5f787b-2381e436',
 'operationType': 'insert',
 'progress': 0,
 'selfLink': 'https://www.googleapis.com/compute/v1/projects/srcc-gcp-ruth-will-phs-testing/zones/us-west1-a/operations/operation-1521360676388-567ab62b0fca0-fe5f787b-2381e436',
 'status': 'PENDING',
 'targetId': '8438793552607289803',
 'targetLink': 'https://www.googleapis.com/compute/v1/projects/srcc-gcp-ruth-will-phs-testing/zones/us-west1-a/instances/vsoch-hello-world-builder',
 'user': 'vanessasaur@srcc-gcp-ruth-will-phs-testing.iam.gserviceaccount.com',
 'zone': 'https://www.googleapis.com/compute/v1/projects/srcc-gcp-ruth-will-phs-testing/zones/us-west1-a'}
```

And after launch, you can always get a list of instances:

```
$ client._get_instances()
```
If you wanted to destroy a particular instance and stop the build, you can do that too. In the
case above, we had an instance called "vsoch-hello-world-builder"

```
$ client.destroy('vsoch-hello-world-builder')
```

<div>
    <a href="/sregistry-cli/clients"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-storage"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
