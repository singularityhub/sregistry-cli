---
layout: default
title: Contribute a Client
pdf: true
permalink: /contribute-client
toc: false
---

# Contributing a Client

## What is a client?
A client is an endpoint that you might want to push or pull Singularity images (or other metadata) from a local resource to and from it. Generally, your client will implement any or all of the following functions:

 - *pull*: `[remote->local]` is a common use case. It says "get this remote image and pull it from there to my local database and storage."
 - *push*: `[local->remote]` takes an image on your host and pushes to the remote (usually given some permission).
 - *record*: `[remote->local]` the same as a pull, but without the image file (just get the metadata!)
 - *search*: `[remote]`: list or search a remote endpoint. 
 - *delete*: `[remote]`: delete an image from a remote endpoint if you have the correct credential.

## Getting Started
I'll briefly outline the order of operations that I (@vsoch) have taken when adding a new client, because when you go about it in a certain way, it's very logical.


### Order of Operations
In a nutshell, do this:

```
1.                    2.          3.         4.           5.         6.           7. 
[skeleton client] --> [shell] --> [push] --> [search] --> [pull] --> [record] --> [share]
```

1. Very importantly, as you go through each step, write the documentation for it. It's very easy to test as you go, and write notes about different functions when they are fresh in your mind.
2. I start with the template (more detail below) and add the basic steps to instantiate an empty client `shell` (sregistry shell). Using the shell, I first implement whatever is needed for authentication, usually by commenting out the init functions to start, and then working in the terminal window. These steps to connect the user to the remote service may mean checking for a credentials file and then issuing some sort of request, checking for variables, or otherwise interacting with the user.
3. When you have a basic client that is authenticated with a service, write the `push` function first. Your goal is to start with a local image file, and ultimately get it into your storage place. It needs to have organization and metadata to identify it as a container, **and** easily provide a uri back to the user.
4. Once you have "push" working, it's trivial to push a few images. Do this. Write some documentation about it if you haven't already. When you have a few different ones, then it's logical to write `search` (functions in the template query.py file) because you have images with metadata to work with, and a client that can interact with the service.)
5. After push and search are done, write the `pull` function. It's going to be similar to search because you will start with searching for a particular container given some user query, but then you add the step to actually download and add it to the local storage.
6. Following `pull` you should write the `record` function. It will be trivial and simple because it's exactly the same as pull, but for the final call to the `add` function you don't provide an image file.
7. After this core, implement any of the extra functions relevant to your client (like share!) Usually at this point I'm super excited and I record an asciinema for it, and finish up the documentation.


### The General Steps
We are going to generally follow these steps. Note that these docs haven't been fully written out, so the instructions are brief for now. Expect more soon!

1. Adding the client dependencies
2. Start with a template for the client. This will mean filling in basic functions with your custom calls to get or send images. 
3. Add any custom or hidden functions
4. Add the client to the application. This means registering its uri (e.g., `hub`) to the client's logic when it initializes.
5. Think about credentials. We advocate for an approach that determines needed credentials based on envirionment variables, and thus you can ask a user to export what is needed for your functions to find. 
6. Think about settings. If you need a more enduring storage for settings, `sregistry` has a default settings file where you can write a data structure for your client.
7. Test the client to make sure things work as expected.

If you haven't already, fork the repository, and then clone your fork, or clone our repository and add your remote fork later.

```
git clone https://www.singularityhub.org/sregistry-cli
cd sregistry-cli
```

### 1. Adding Dependencies
The user doesn't have to install any or all custom clients, this is one advantage to Singularity Registry Global Client. For this reason, you must first define any additional (python) dependencies that are needed for the install. You can do that by first adding your client as a submodule in the [version.py](https://github.com/singularityhub/sregistry-cli/blob/master/sregistry/version.py#L42) file. For example, if I am adding globus, I might define a variable for it and put needed python dependencies:

```
INSTALL_REQUIRES_GLOBUS = (

    ('globus-sdk[jwt]', {'exact_version': '1.3.0'}),
)
```

and then add the end of the file make sure to add your new variable to the `INSTALL_REQUIRES_ALL`

```
INSTALL_REQUIRES_ALL = (INSTALL_REQUIRES +
                        ...
                        INSTALL_REQUIRES_GLOBUS)
```

Take careful note that this *must be a tuple*. If you only have one thing, don't forget the hanging comma at the end (otherwise it's a string!) Then in the [setup.py](https://github.com/singularityhub/sregistry-cli/blob/master/setup.py) make sure to add it as a submodule:

```
# Here I'm reading in the variable from lookup, which comes from version.py
GLOBUS = get_requirements(lookup,'INSTALL_REQUIRES_GLOBUS')

...

# Now under "extra_requires" I add globus to the list
          extras_require={
              'dropbox': [DROPBOX],
              'globus': [GLOBUS],
              'google-storage': [GOOGLE_STORAGE],
              'google-drive': [GOOGLE_DRIVE],
              'all': [INSTALL_REQUIRES_ALL]
          },
```

The user would then install your client for his/her sregistry by doing:

```
pip install sregistry[globus]
```

#### Singularity Image
And don't forget to add your client to the Singularity image! That is in the [Singularity file](https://github.com/singularityhub/sregistry-cli/blob/master/Singularity) at the root of the repository. 

```
#######################################
# Globus
#######################################

%appenv globus
    SREGISTRY_CLIENT=globus
    export SREGISTRY_CLIENT
```

This will ensure that if a user tries to run your client with:

```
singularity run --app globus sregistry
```

it will set the environment variable `SREGISTRY_CLIENT` to globus to activate the client. You don't need to worry about triggering the install for the install extras, we use a command at the end to make sure all are installed.

### 2. Start with the template
First, let's look at where to find things. We've simplified this structure quite a bit.

```
├── LICENSE
├── MANIFEST.in
├── setup.py
├── Singularity
├── sregistry
│   ├── auth
│   ├── main            # where you will add a folder for your client functions
│       ├── base.py     # The client base has an APIConnection class you will start with
│       ├── __init__.py     # The logic to determine what client to load is here
│       └── myclient    # your client will be added as a folder here
│   ├── database        
│       ├── sqlite.py   # Global functions (inspect, get, images) are here
│       └── models.py   # Database models are here
│   ├── defaults.py     # Environment variables loaded at runtime are defined here
│   ├── logger
│   ├── client          # Imports the client from main, and parses what the user wants
│       ├── pull.py     # contains the logic for "pull," and will call client.pull
        ...
│       └── __init__.py # **the application entrypoint** that adds commands to arguments
                          based on what is found for the client
│   ├── utils
│   └── version.py
└── README.md
```

The first step is thus to create your client folder under `main`. We have provided a template folder that you can use to get started. You can copy it to your new client:

```
cp -R sregistry/main/__template__ sregistry/main/myclient
```

To describe the above in more detail, the base of a client is the ApiConnection (in `main/base.py`), which comes with standard functions for web requests, showing progress bars with a download, get, etc. Your "myclient" will subclass that, and onto it you will add the custom functions for push, pull (and the others that are important). This happens in the `main/myclient/__init__.py` where your client is generated. Then, if the user wants to use `myclient` the environment variable is detected in `main/__init.__py` and your Client imported from it's respective folder. You can follow along the template for more detail, and feel free to improve it with a pull request.  We will quickly discuss functions that will be useful to you, globally.


#### Fun Customization
If you have a service that needs a thumbnail, for a cute robot you can use a function provided:

```
from sregistry.utils import get_thumbnail
thumbnail = get_thumbnail()
# thumbnail
'/home/vanessa/Documents/Dropbox/Code/sregistry/sregistry-cli/sregistry/database/robot.png'
```

Here is what he looks like:

![../img/robot.png](../img/robot.png)

Note that if you (or your user) exports their own thumbnail, you can change this value! You should
generally choose an image no greater than 2MB, and one that has a minimum width of 220px (these are the standards
defined by [Google Drive](https://developers.google.com/drive/v3/web/file), they may differ for different services. here is how to export your thumbnail:

```
SREGISTRY_THUMBNAIL = /path/to/myrobot.png
export SREGISTRY_THUMBNAIL
```
or of course you can set this for your client during the initialization, so the variable is found later. Have fun!


#### Logging
If you import the bot, you get with him a bunch of easy to use functions for different levels along with functions. For example, here are different levels of messages coinciding with what gets displayed depending on the user export of `MESSAGELEVEL`:

```
from sregistry.logger import bot

bot.abort('Abort')
ABORT Abort
bot.error('Error')
ERROR Error
bot.warning('Warning')
WARNING Warning
bot.custom(prefix="RUHROH", message='Custom message', color="PURPLE")
RUHROH Custom message
bot.info('Info')
Info
bot.critical('Critcal')
CRITICAL Critcal

And here we see when the message level is set above a particular level, we don't see it.

```
bot.level
# 1
bot.debug('Debug')
bot.verbose('Verbose')
bot.verbose1('Verbose 1')
bot.verbose2('Verbose 2')
bot.verbose3('Verbose 4')
```

You can also turn a list of lists into a nice table with `bot.table()`

```
rows = [["Dunkin","Donuts","Coffee"],["Starbucks","Donuts","Coffee"],["KrispyKreme","Donuts","Coffee"]]
bot.table(rows)

1  Dunkin	Donuts	Coffee
2  Starbucks	Donuts	Coffee
3  KrispyKreme	Donuts	Coffee
```

Finally, for things that might take a while, you can use a spinner (make sure to stop and start it)

```
from time import sleep
bot.spinner.start()
sleep(5)
bot.spinner.stop()
```

At this point, you should implement the functions you need for your client, following the pattern to write a file named according to the function (e.g., push) and then making sure to add the functions to the client at the end of your `main/myclient/__init__.py` file. Be sure to look carefully about what arguments are expected to come in (and come out). For outputs we leave it up to you, but provide "best practices" that are used for the others. We generally want the user experience to be consistent, regardless of using different clients, but if you have rationale for a different experience (and make your users aware) this is a reasonable deviance.

### 3. Add any custom or hidden functions
If you look at a client, it's common to want to add functions to the class that are hidden, or used internally. It also might be the case that you want to expose functions like "pull" and "push" to the command line user, but more interesting functions for the developer to use when interacting with the client in Python. To do this, we ask that you hide the functions with underscores to indicate private. E.g., a call to search might be done like this:

```
client.search(query="vsoch/hello-world")
```

but then on the back end, your search entrypoint does some logical parsing of the input and then calls different functions internally:

```
self._container_search(...)
self._collection_search(...)
```

If you have any questions please don't hesitate to ask.

### 4. Add the Client to sregistry
This is a very simple (but easy to overlook) step of adding an if statement in the `main/__init__.py` file to just check the environment variable for your client name:

```
    if SREGISTRY_CLIENT == 'myclient':
        from .myclient import Client
```

And since you defined the `Client`in `myclient/__init__.py`, a subfolder, it is imported correctly.


### 5. Think about credentials and settings
Environment variables are the primary way in which the user interacts with the clients to define parameters. In addition to the [environment variables](/sregistry-cli/getting-started#environment-variables-lists), your client can also choose to keep a cache of a variable, meaning an entry in the default `SREGISTRY_CLIENT_SECRETS` file (default is `$HOME/.sregistry`) OR using a custom file or folder (defined for you at `self._credential_cache`). The advantages of either approach are that a user doesn't need to set a parameter again, and if a record is needed in the future for some setup, it isn't lost in the environment. You as a client developer are responsible for deciding how to manage this cache, because something direct like an access token may not be appropriate, but instead a path to a file that contains it. To help interact with this cache, we have provided the default client that your client will subclass with helper functions.

 - [Settings](#settings): should be derived primarily from the environment, and with the naming schema specific to your client (see more below).
 - [Storage](#storage): we provide for you functions to easily get and update parameters for your client, along with two methods for saving, depending on what needs to be saved.
 - [Helpers](#helpers): include functions for saving parameters to the default `sregistry` settings file, or to a client secrets file that is specifically for your client.
 - [Tasks](/sregistry-cli/client-tasks): The `sregistry client` includes workers that use multiprocessing if you want to run a bunch of download tasks at the same time, for example.

#### Settings
If you have any settings or parameters that you need to obtain from the user, the recommended way to do this is check for them in a function called by your client `__init__`, and then get them from settings, use a default, or exit if required and not found. First, we will talk about interaction of your client with the user. The user is going to set environment variables that you tell him about, and your variables must live in the sregistry namespace for your client. To maintain the `SREGISTRY` environment variable namespace, you should use the following convention:

```
`SREGISTRY_<CLIENTNAME>_<VARIABLE>`
```

Notice that it starts with `SREGISTRY_`, the client name comes next, and then finally the variable name. Also note that we are using all caps. How should you decide how to name things? If you are using an environment variable that is defined from another service or application (for example, Google has the user export credentials to `GOOGLE_APPLICATION_CREDENTIALS` you should honor that name and not add the `SREGISTRY_` prefix so the user only has to define it once. 

#### Metadata
Before adding an image to your storage or pushing to an external endpoint, it's good to extract metadata to pair with the request. To do this, the Singularity Global clients take a simple approach to use the Singularity "inspect" command to output json. To make this flexible and easy for developers to use, this is provided as a function in the base client. Let's open a shell to test:


```
sregistry shell
client.speak()
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
```

Grab a random file
```
image_file = 'vsoch-hello-world.simg'
image_name = "vsoch/hello-world"
```

If you want to do customization of the tag, or uri otherwise, do this first. There are functions to parse the image name and uri.

```
from sregistry.utils import ( parse_image_name, remove_uri )
$ names = parse_image_name(remove_uri(image_name))
$ names
{'collection': 'vsoch',
 'image': 'hello-world',
 'storage': 'vsoch/hello-world:latest.simg',
 'tag': 'latest',
 'uri': 'vsoch/hello-world:latest',
 'url': 'vsoch/hello-world',
 'version': None}
```
Notice that if we just parse the image based on a name, we have very little metadata about it. 
Finally, use the client's function to get metadata to extract the full data structure.

```
metadata = client.get_metadata(image_file, names=names)
```
Now notice that we have a much richer body of metadata.

```
{'collection': 'vsoch',
 'data': {'attributes': {'deffile': 'Bootstrap: docker\nFrom: ubuntu:14.04\n\n%labels\nMAINTAINER vanessasaur\nWHATAMI dinosaur\n\n%environment\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n%files\nrawr.sh /rawr.sh\n\n%runscript\nexec /bin/bash /rawr.sh\n',
   'environment': '# Custom environment shell code should follow\n\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n',
   'help': None,
   'labels': {'MAINTAINER': 'vanessasaur',
    'WHATAMI': 'dinosaur',
    'org.label-schema.build-date': '2017-10-15T12:52:56+00:00',
    'org.label-schema.build-size': '333MB',
    'org.label-schema.schema-version': '1.0',
    'org.label-schema.usage.singularity.deffile': 'Singularity',
    'org.label-schema.usage.singularity.deffile.bootstrap': 'docker',
    'org.label-schema.usage.singularity.deffile.from': 'ubuntu:14.04',
    'org.label-schema.usage.singularity.version': '2.4-feature-squashbuild-secbuild.g780c84d'},
   'runscript': '#!/bin/sh \n\nexec /bin/bash /rawr.sh\n',
   'test': None},
  'type': 'container'},
 'image': 'hello-world',
 'storage': 'vsoch/hello-world:latest.simg',
 'tag': 'latest',
 'uri': 'vsoch/hello-world:latest',
 'url': 'vsoch/hello-world',
 'version': None}
```

The reason that we provide this function is that it could be the case that the user doesn't have Singularity installed. The functions should work the same, so this client function handles doing these checks. If you don't need to customize the names data structure (or generally provide your own dictionary with some custom metadata) then you can skip the first portion and just call the metadata function:

```
metadata = client.get_metadata(image_file, names=names)
```

and the `parse_image_name` function will be called internally when names is found to be None.


#### Storage
It might be the case that you need more than a shared json file (the `sregistry` settings file shared by all clients) for your secrets or client. Toward this aim, each client is configured to automatically generate a credentials cache path. The path is found with the client at `client._credential_cache` and the following applies:

 - If the user has specified [environment settings](/sregistry-cli/getting-started#environment-variable-lists) to indicate disabling the credential cache, the value of `client._credential_cache` will be `None` and you should not use it.
 - If the cache is enabled, `client._credential_cache` will return a path in the format `<SREGISTRY_DATABASE>/.sregistry/<CLIENT>`. For a default `SREGISTRY_DATABASE` and a client called `MYCLIENT` the path returned would be `$HOME/.sregistry/myclient`.
 - The `client._credential_cache`, if defined, will not exist. The reason for this is that you as the developer can choose to use it as a file, or a folder with some set of files inside. In both cases, you are required to write the file or create the folder, and we recommend the following functions:

```
# Make a directory (recursive)
from sregistry.utils import mkdir_p

# Write or read json
from sregistry.utils import read_json, write_json

# Write or read file
from sregistry.utils import write_file, read_file
```

#### Helper Functions
To make it easy for development, we have created a set of functions that live with all clients to do checks, along with get and update environment variables. In the examples below, we will start with high level functions, and then move into more detailed functions used by them.

##### Update Token
If a call (e.g., get, post, etc.) ever returns a 401 response, the base client will automatically check if it has a function called `_update_token`. If so, it will call the function and then issue a retry of the failed request. This means that, if you have some functional logic for obtaining (or refreshing) a token (or updating a token otherwise) you should implement this function for your client. The function will pass the response object to `_update_token`. For example, here is the function in a submodule of your client:

```
def update_token(self, response):
    '''
    '''
```

and then it's added to the client in the `__init__py`

```
from .submodule import update_token

Client._update_token = update_token
```

The token function should exit with status code 1 if the update for the token is unsuccessful (meaning a second try wouldn't be worth it).

##### Check for secrets
It might be the case that you want to do a quick check that secrets exist for your client. For example, for the `registry` client pull and push functions, there is no feasible way to interact with a registry if the client hasn't defined the `registry` key in his or her client secrets! Actually, there are many things we might want to check for:

 - does the secrets file exist, period?
 - does the secrets file have a lookup for the client?
 - does the lookup have one or more parameters defined?
 - if the parameter is defined, is it None or empty?

We provide an easy way to do these checks for a client, and we will walk through them in a shell:

```
sregistry shell
client.client_name
'hub'
```

This first function will check for a secrets file, and specifically, that the client `hub` has an entry in it. If not defined, it would exit and tell the user.

```
# Do I have a secrets file, period?
client.require_secrets()

# will exit if not found

# Do I have a secrets file with parameter "name" defined?
client.require_secrets(params='name')

# Do I have a secrets file with parameters "name" and "group" defined?
client.require_secrets(params=p["name", "group"])
```

and so, for example, in the push and pull functions, since we require secrets period, we can just call:

```
self.require_secrets()
```

##### GET
First, you might decide for your client (let's call it `myclient`) that your user can optionally set `SREGISTRY_MYCLIENT_ID`. If you just want to get the variable from the user, and return `None` if it's not found, you can use the following function:

```
# self refers to the sregistry.main.Client

setting = self._get_setting('SREGISTRY_MYCLIENT_ID')
```
Note that the above function looks first in the environment, and then in the secrets file. If it's not found in either place, `None` is returned. You can also return all settings for a particular client:

```
# This is the active client
active_settings = self._get_settings(self.client_name)

# This is another client (not necessarily active)
more_settings = self._get_settings('google-storage')
```

or for all clients (including those not active.

```
settings = self._get_settings()
```


##### GET and UPDATE
For our next example, we want to do the same, but instead of just a get, we want to save the parameter that we find in the `sregistry` client settings file (so it's found next time without the user needing to set it). That would look like this:

```
setting = self._get_and_update_setting('SREGISTRY_MYCLIENT_ID')
```

Given that something is found in the environment, it will also update the settings file, and importantly, save it indexed by your client name. For the above, in the client secrets file (default `$HOME/.sregistry`) we would see the following update:

```
{
  'myclient': {'SREGISTRY_MYCLIENT_ID': setting }
}
```

where `setting` corresponds to whatever was found in the environment. The client name (`myclient`) is obtained from the client itself (`self.client_name`). 


##### GET (entire settings file)
If you would prefer to read the entire file (one level down from the above, and used by the functions above):

```
from sregistry.auth import read_client_secrets

secrets=read_client_secrets()

secrets
{'base': 'http://127.0.0.1',
 'token': '3c00ebba888c238a50820bb9a1f38518c9360b31',
 'username': 'vsoch'}
```

##### UPDATE (entire settings file)
Let's say we get the entire settings file, we make many changes, and then we want to update:

```
from sregistry.auth import update_client_secrets
backend = "myclient"
secrets = update_client_secrets(backend="myclient", 
                                updates={'pancakes':'latkes'})
```

Then you will notice you have an entry for `myclient` in the secrets with your settings:


```
{'base': 'http://127.0.0.1',
 'myclient': {'pancakes':'latkes'},
 'token': '3c00ebba888c238a50820bb9a1f38518c9360b31',
 'username': 'vsoch'}
```

You can also call the update function and give it an already defined secrets to update:

```
secrets = update_client_secrets(backend="myclient", 
                                updates={'pancakes':'latkes'},
                                secrets=secrets)

```

We generally don't advocate for this approach, because it's important to maintain the separation of client storage locations.





It's also common practice to ask the user to download some credential file, and then
authorize via a url. For this purpose, we provide a basic function that prompts the user
to go to a url that you provide, accept something, and then enter a code (and return
it to your client).

```
code = self._auth_flow(url)
```

### 7. Test the client!
We don't have requirements or templates for tests yet (please contribute!) but you would obviously want to do the testing and documentation part here. This means:

 - add tests for the continuous integration
 - update the CHANGELOG with your changes, and read the guidelines for contributing
 - write complete docs for your contribution!
 - issue a pull request!


More details will come for this final section, likely after much work on some of the clients.

<div>
    <a href="/sregistry-cli/"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/contribute-docs.html"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
