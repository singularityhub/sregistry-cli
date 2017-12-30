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

To describe the above in more detail, the base of a client is the ApiConnection (in `main/base.py`), which comes with standard functions for web requests, showing progress bars with a download, get, etc. Your "myclient" will subclass that, and onto it you will add the custom functions for push, pull (and the others that are important). This happens in the `main/myclient/__init__.py` where your client is generated. Then, if the user wants to use `myclient` the environment variable is detected in `main/__init.__py` and your Client imported from it's respective folder. You can follow along the template for more detail, and feel free to improve it with a pull request.  We will quickly discuss functions that will be useful to you, globally:

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
The primary (recommended) way for users to interact with your client is via environment variables. To maintain the `SREGISTRY` environment variable namespace, you should use the following convention:

```
`SREGISTRY_<CLIENTNAME>_<VARIABLE>`
```

Notice that it starts with `SREGISTRY_`, the client name comes next, and then finally the variable name. Also note that we are using all caps. If you are using an environment variable that is defined from another service or application (for example, Google has the user export credentials to `GOOGLE_APPLICATION_CREDENTIALS` you should honor that name and not add the `SREGISTRY_` prefix so the user only has to define it once.

#### Helper Functions
To make this easy for your development, we have created a set of functions that live with all clients to get and update environment variables. In the examples below, we will start with high level functions, and then move into more detailed functions used by them. First, you might want to get an environment variable from the user. You can do that with `client._get_setting()`. Let's say that I tell my user to export a credential to `SREGISTRY_MYCLIENT_ID`. If I want to look for it in the environment, and then if not found, look in the client secrets file, I would do:

```
# self refers to the sregistry.main.Client

setting = self._get_setting('SREGISTRY_MYCLIENT_ID')
```

This will either be the value set in the environment (first priority) or the settings file (second priority) and then `None` if not found. If you want to, on top of finding any result, save it to the secrets to be found the next time (so the user doesn't have to define it) then use `client._get_and_update_setting()`

```
setting = self._get_and_update_setting('SREGISTRY_MYCLIENT_ID')
```

Given that something is found in the environment, it will also update the secrets, and importantly, save it indexed by your client name.



```
from sregistry.auth import read_client_secrets

secrets=read_client_secrets()

secrets
{'base': 'http://127.0.0.1',
 'token': '3c00ebba888c238a50820bb9a1f38518c9360b31',
 'username': 'vsoch'}
```

If you need to write some settings there (please use environment variables and give the user instructions for credentials and other secrets) then you can update secrets too.

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
