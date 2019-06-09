---
layout: default
title: Google Compute Builder Developer Start
pdf: true
permalink: /client-google-compute-developer
toc: true
---

# Google Compute Builder
This is the documentation for developers that want to use the function from `sregistry`
in their Python scripts. For getting started guides for users, see the [previous page](/sregistry-cli/client-google-compute).

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
    <a href="/sregistry-cli/client-google-compute-detail"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-compute-storage"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
