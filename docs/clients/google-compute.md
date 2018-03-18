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

## Getting Started
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
b
We will do the above in two different ways - first with the minimum customization required (and using defaults) and then generating a full, custom configuration from a library of builder bundles that is worked on collaboratively by the community.
We will first review environment variables, followed by our tutorial walk throughs noted above. You can skip down to [Build](#build) if you are impatient.


### Required Environment
The tools served by `sregistry` work way of obtaining information from the environment. For the Google Compute Builder you need the same base of information as for using the [Google Storage Client](/sregistry-cli/client-google-storage). You will first need to [set up authentication](https://cloud.google.com/docs/authentication/getting-started) by following those steps. It comes down to creating a file and saving it on your system with the variable name `GOOGLE_APPLICATION_CREDENTIALS`. This variable will be found and used every time you use the Google Compute Builder, without needing to save anything to the secrets. Thus, the minimum required environment variables that you need to set (meaning they are required and have no defaults) are the following:

| Variable | Default | When is it used? | Description |
|----------|---------|------------------|-------------|
| [GOOGLE_APPLICATION_CREDENTIALS](https://cloud.google.com/docs/authentication/getting-started) | Not set | When you issue commands to work with Google Cloud APIs | This is a json file on your host that authenticates you with Google Cloud |
| SREGISTRY_COMPUTE_PROJECT | Not set | On the host and builder to specify your project | This is the name of your Google Cloud Project |

Beyond the credentials, the builders use reasonable defaults for most things, but you might also want to change them. We will discuss optional variables for build setup and runtime [later in this document](#optional-environment).


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
usage: sregistry build [-h] [--list] [--preview] [--name NAME]
                       [--config CONFIG]
                       [command]

positional arguments:
  command          Github repository with templates, or command

optional arguments:
  -h, --help       show this help message and exit
  --list, --ls     list builder instances.
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
[builder bundle Github repository](https://www.github.com/singularityhub/builders) 
We could then retrieve that particular template,  and pipe it into a file:

```
$ sregistry build templates cloud/google/compute/ubuntu/securebuild-2.4.3.json >> config.json
```

At this point you would likely open up the config.json file, and edit to your needs.

### Build
You want to build! The commands argument to build can look like any of the following. The
only requirement is a Github repository. You are **required** to have your work in version
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

### Instances

**TBA**

If you are interested to read more about the local commands for the Google Storage client,
continue reading about the [Google Storage](/sregistry-cli/client-google-storage) client.


## Optional Environment

### Build Setup Environment
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

### Runtime (Before Builder Bundle) Environment

These variables are relevant to actual build runtime, and defined and retrieved as metadata in the [start_script templates](https://github.com/singularityhub/sregistry-cli/tree/master/sregistry/main/templates) packaged with the
`sregistry` client. This is the script that is called when the instance starts up, and its job is to clone the 
builder bundle repository (with your selected builder scripts) and run it. At this point in time, we've deployed the
instance but haven't yet cloned the builder bundle. We use a set of variables prefixed with `SREGISTRY_BUILDER_*` retrieved
via instance metadata to identify the builder's repository (e.g., [https://www.github.com/singularityhub/builders](https://www.github.com/singularityhub/builders).


| Variable | Default | When is it used? | Description |
|----------|---------|------------------|-------------|
| SREGISTRY_BUILDER_REPO | https://www.singularityhub.org/builders | Used to retrieve the builder bundle specified by the user. | The repository that serves the builder bundle API that is cloned to get the scripts to perform the build. Yes, you can create your own, or contribute to the community default! |
| SREGISTRY_BUILDER_BRANCH | `master` | To clone the correct branch of the builder at runtime | The branch of the builder bundle to clone |
| SREGISTRY_BUILDER_COMMIT | Not set | To clone the correct commit of the builder at runtime | The commit to use for the buider repository |
| SREGISTRY_BUILDER_RUNSCRIPT | `run.sh` | This, with path relative to the build bundle, is called after cloning the build bundle repo and cd'ing into the folder. The path is relevant to its parent folder, so usually `run.sh` will suffice. | This is the script that is called after cd'ing into the folder. It should handle installing dependencies (including Singularity) along with running the build, uploading results to storage, and shutting down the instance. |
| SREGISTRY_BUILDER_KILLHOURS | 10| During build, in case there is issue, kill the process at this time | After how many hours should the entire process be given up? If not, you need to manage your instances in your build console. |
| SREGISTRY_BUILDER_MANAGER | `apt` | The package manager use in the `start_script.sh` to install git and clone the builder repo | The custom installation of dependencies is done by the builder bundle, but we need a starting base to clone this with git. This variable will determine if you will get an instance with git or yum. |

### Runtime (During Builder Bundle) Environment
Once the builder bundle is cloned and the `SREGISTRY_BUILDER_RUNSCRIPT` is called, we need to do simple things line install Singularity. Thus, variables prefixed with `SINGULARITY_*` refer to the installation of Singularity itself, and other Singulraity building environment variables that you want to set.

| Variable | Default | When is it used? | Description |
|----------|---------|------------------|-------------|
| SINGULARITY_RECIPE | Singularity at base (root) of repository | The recipe is up to you to specify for the builder, and must be discovered to exist at buildtime. | The Singularity recipe to build from the repository, which also determines the image tag via its extension. No extension indicates tag `latest` |
| SINGULARITY_REPO | `https://github.com/cclerget/singularity.git` | The Singularity repository to install from is cloned and built at runtime. |  This default is used as the source of secure builds maintained by [@cclerget](https://www.github.com/cclerget). |
| SINGULARITY_BRANCH  | `feature-squashbuild-secbuild-2.4.3` | The branch is cloned from the getgo to install Singularity during build time |  This is the branch that you want to checkout for the Singularity software |
| SINGULARITY_COMMIT  | Not set | The commit to use to install Singularity during build time |  This is the commit that would be checked out, if defined. |

Any other remaining variables that you might find in a config.json are specific to that builder, for example, the default has a `CONTACT` variable that might be set to send notification to an email.  Remember that all of these variables are defined in your `config.json` file that you hand off to the `sregistry` client. You are free to add or subtract any variables that your custom config might need, and generally the config will provide an empty value if a metadata variable is optional.


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
   'tags': ['ubuntu', 'singularity']}],
 'links': {'self': 'https://singularityhub.github.io/builders/configs.json'}}
```

There is only one right now, since this is under development! To load it (if
this were run on the command line) we use the function `_load_build_config` with the name:

```
$ config = client._load_build_config('cloud/google/compute/ubuntu/securebuild-2.4.3.json')
```

and the config is loaded:

```
[{'data': {'author': 'Vanessa Sochat',
   'config': {'disks': [{'autoDelete': True,
      'boot': True,
      'initializeParams': {}}],
    'networkInterfaces': [{'accessConfigs': [{'name': 'External NAT',
        'type': 'ONE_TO_ONE_NAT'}],
      'network': 'global/networks/default'}],
    'serviceAccounts': [{'email': 'default',
      'scopes': ['https://www.googleapis.com/auth/compute',
       'https://www.googleapis.com/auth/devstorage.read_write',
       'https://www.googleapis.com/auth/logging.write']}]},
   'id': '/cloud/google/compute/ubuntu/securebuild-2.4.3',
   'metadata': {'BUILDER_KILLHOURS': '10',
    'BUILDER_LOGFILE': '/tmp/.shub-log',
    'BUILDER_TAG': '',
    'CONTACT': '',
    'GOOGLE_COMPUTE_IMAGE_FAMILY': 'debian-8',
    'GOOGLE_COMPUTE_PROJECT': 'debian-project',
    'SINGULARITY_BRANCH': 'feature-squashbuild-secbuild-2.4.3',
    'SINGULARITY_COMMIT': '',
    'SINGULARITY_RECIPE': '',
    'SINGULARITY_REPO': 'https://github.com/cclerget/singularity.git',
    'SINGULARITY_RUNSCRIPT': 'run.sh',
    'SREGISTRY_BUILDER_machine_type': 'n1-standard-1'},
   'tags': ['ubuntu', 'singularity']},
  'links': {'self': 'https://singularityhub.github.io/builders/cloud/google/compute/ubuntu/securebuild-2.4.3.json'}}]
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
               config=config,
               preview=True)

Adding recipe Singularity to config.

{'disks': [{'autoDelete': True,
   'boot': True,
   'initializeParams': {'sourceImage': 'https://www.googleapis.com/compute/v1/projects/debian-cloud/global/images/debian-8-jessie-v20180307'}}],
 'machine_type': 'zones/us-west1-a/machineTypes/n1-standard-1',
...
```

Note that if the repository isn't found (indicated by a 200 or 301, redirect response) you will
get an error that it isn't healthy. It's better to figure this out before launching a builder!

```
$ client.build(repo='https://www.github.com/tacos/i-dont-exist',
               recipe="Singularity",
               config='config.json',
               preview=True)
ERROR https://www.github.com/tacos/i-dont-exist, response status code 404.
```

### 4. Run the build!
Now we can launch the build!

```
$ client._run_build(config)
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
