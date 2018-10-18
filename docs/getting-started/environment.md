---
layout: default
title: Environment Variables
pdf: true
permalink: /environment
toc: false
---

## Environment Namespace

A quick summary of environment variables is shown below, and more details about 
specific variables provided after that.

| Variable              | Default                         | Definition                          |
|-----------------------|---------------------------------|-------------------------------------|
| SREGISTRY_DATABASE    | $HOME/.singularity              | The base folder for the sregistry database |
| SREGISTRY_CREDENTIALS_CACHE | $SREGISTRY_DATABASE       |
| SREGISTRY_STORAGE     | $HOME/.singularity/shub         | The folder *within* SREGISTRY_DATABASE to store images |
| SINGULARITY_DISABLE_CACHE| False                        | Disable caching of Singularity build objects |
| SREGISTRY_DISABLE     | False                           | Disable the database entirely, omits sqlalchemy dependency |
| SINGULARITY_CACHEDIR  | $HOME/.singularity              | We honor the Singularity client cache directory |
| SREGISTRY_CLIENT_SECRETS | $HOME/.sregistry             | a json file, with keys as clients, values are client-specific parameters |
| SREGISTRY_HTTPS_NOVERIFY | False                        | Turn off certificate verification (not recommended) |
| SREGISTRY_CLIENT | hub                                  | Remote client to interact with list with `sregistry backend ls` |
| SREGISTRY_TMPDIR    | temporary directory | A temporary folder to build and pull containers |
| SREGISTRY_THUMBNAIL | [install-dir]/database/robot.png  | A thumbnail for clients to use, if needed |
| SREGISTRY_DISABLE_CREDENTIAL_CACHE | False | Disable all caching of credentials (you will need to always set |
| SREGISTRY_PYTHON_THREADS | 9 | Number of threads to use for Multiprocessing (download of layers, generally) |
| MESSAGELEVEL    | INFO | a client level of verbosity. Must be one of `CRITICAL`, `ABORT`, `ERROR`, `WARNING`, `LOG`, `INFO`, `QUIET`, `VERBOSE`, `DEBUG`|


### Base Environment Defaults

The database path, an sqlite3 file, is determed based on the environment variable
`SREGISTRY_DATABASE`. If not found, it will be written to our singularity cache
folder, which is usually in our `$HOME`.

```
SREGISTRY_DATABASE
/home/vanessa/.singularity/sregistry.db
```

For storage of images, we use the same folder that Singularity will by default look for the cache.

```
SREGISTRY_STORAGE
/home/vanessa/.singularity/shub
```

And for either, if you want to change these locations you can export the variables. There is no
reason that the database file needs to live next to the image folder, for example, and you might
want to give it a unique name to a user, depending on your setup.

If you have exported the variable `SINGULARITY_DISABLE_CACHE`, an option with
the Singularity command line software to not cache anything, SRegistry will honor
this and not maintain a database. If you want to keep the cache but just disable
the SRegistry database, then export `SREGISTRY_DISABLE=yes`.


### Client Environment Variables
The `sregistry` client exposes a lot of customization through environment variables, 
so you as the user have the power to configure it exactly as you need, or stick 
to defaults that are reasonably set. In these sections, we will review the 
sets of environment variables for you to use across clients. If you want to
peek at the environment variables being set for some client, you can do that:

```bash
$ sregistry backend ls registry
registry
{
    "base": "http://127.0.0.1",
    "token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "username": "dinosaur"
}
```

If you are a developer, there is a suite of environment variables provided that are
intended to make interaction with existing functions easier! See our 
[client contribution guide](/sregistry-cli/contribute-client) 
for details on interacting with these environment variables.


#### Http and Authentication
While most of the authentication variables live with the clients, `sregistry` offers a few Global settings to be applied to all web requests.

 - **SREGISTRY_HTTPS_NOVERIFY** will [set verify to False](http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification) when you are making a request, and this means that the server you are using sregistry against has https enabled, but is using an untrusted (usually self-signed) certificate. This option should not be used in production, but is generally useful if you are working with a test server, or are debugging commands. See the [original issue](https://github.com/singularityhub/sregistry-cli/issues/56) for more details. Generally, we do not recommend that you use this more than occasionally. The server certificate in question should be added to your trusted certificates file.


#### Database and Storage
The database refers to the sqlite3 file used to store metadata, typically in the user's home, and the storage refers to the actual folder of images. You can control this behavior with the following environment variables.

 - *SREGISTRY_CLIENT*: Set the client (either as an export or runtime) to determine which endpoint you want to use. By default, Singularity Hub is used, and functions that are available for all commands (detailed in this section and also reviewed under [commands](/sregistry-cli/commands) are available.
 - *SREGISTRY_SHELL*: When you use `sregistry shell` it will default to looking for python, bpython, and then ipython. If you have preference for one or the other, set this variable. Note that it will persist in your `.sregistry` secrets, so if you change your mind you should set the variable again, or remove it from here.
 - *SINGULARITY_DISABLE_CACHE*: By default, `sregistry` honors your Singularity configuration, meaning that if you have disabled the cache entirely (coinciding with pulling / interacting with images in temporary locations) the `sregistry` client will not use a database or cache. If this variable is found as a derivate of y/yes/true, this means that we simply use the commands as tools to work with images locally.
 - *SREGISTRY_DISABLE*: If for some reason you don't want to disable your Singularity cache but you do want to disable the `sregistry` database and storage, set this to one of y/yes/true.
 - *SREGISTRY_DATABASE*: The `sregistry` has two parts - a database file (sqlite3) and a storage location for the images. This variable should be to a folder where you want the application to live. By default, it will use the same Singularity cache folder (`$HOME/.singularity`), meaning that you would find the database at `$HOME/.singularity/sregistry.db` alongside your docker, metadata, and shub folders.
 - *SREGISTRY_PYTHON_THREADS*: the number of threads to allocate to the worker (if used, typically is useful for download of layers). Defaults to 9.
 - *SREGISTRY_STORAGE*: The storage of images is **drumroll** exactly the same as your Singularity cache for Singularity images! If your `SREGISTRY_DATABASE` is set to `$HOME/.singularity`, then the storage goes into `$HOME/.singularity/shub`. The one difference is that with `sregistry` we create a folder one level up that coincides with the collection name. For example:


```
tree $HOME/.singularity.shub

/home/vanessa/.singularity/shub/
├── expfactory
│   └── expfactory-master:v2.0.simg
└── vsoch
    ├── hello-pancakes:latest.simg
    └── hello-world:latest.simg
```

The organization is trivial for `sregistry` because images are interacted with via uri (unique resource identifier). This is also a way to distinguish images that you have pulled via Singularity into the cache (and aren't in your database) from those retrieved with `sregistry`, and organized and present in the database. For future versions of Singularity it would be ideal to give the user an option to add images in this format (and possibly add to the database, if the integration is available).

#### Credentials and Settings
Credentials broadly refer to tokens and secrets (authentication and refresh tokens, for example) needed by various clients to authenticate you to their services. The `sregistry` client has two storage strategies for handling credentials and settings.

 - [SREGISTRY_CLIENT_SECRETS](#): is a file that is accessible to all clients, and is indexed by the client name (e.g., `google-storage`. This is a file where you can expect to keep parameters for different clients, and likely details about these settings are provided in the [client documentation](/sregistry-cli/clients). This is also where, if you manage or use a singularity registry, you are instructed to keep your token. The default location of this json file is at `$HOME/.sregistry`, and if you want to change that, simply define this variable. If you don't use or host a registry and the default location is good, you don't need to set this variable.
 - [SREGISTRY_DISABLE_CREDENTIAL_CACHE](#): if you want to disable caching credentials entirely, meaning that you will not take advantage of refresh tokens (not recommended) you can export this variable as some derivative of yes/y/true. Note that an alternative would be to use the client as you need, and then manually delete the file.
 - [SREGISTRY_DISABLE_CREDENTIAL_<client>](#): It might be the case that you want to disable credential caching on a per-client basis. To do this, just export the variable above with the client that you want to disable.
 - [SREGISTRY_CREDENTIALS_CACHE](#) By default, we use the database folder (`SREGISTRY_DATABASE`) as the credentials cache folder, and create a subfolder `.sregistry` in it for the client-specific credential files. This means that, by default, the `google-drive` client would use the file `$HOME/.singularity/.sregistry/google-drive` for it's refresh tokens, and the path `$HOME/.singularity/.sregistry` is the default path that you can override with `SREGISTRY_CREDENTIALS_CACHE`. If you are ok with the defaults, there is no need to set this.


#### Temporary Locations

For most clients, if we need to pull (or build) a container, we will do so in a temporary
location that defaults to the result of `tempfile.mkdtemp()`, meaning a temporary folder.
If you choose, you can export this to be a different location by setting `SREGISTRY_TMPDIR`.
This will be used for all actions other than those that are driven by Singularity, which has
its own environment variable namespace for pull and cache locations (e.g., `SINGULARITY_CACHEDIR`).
If you want to customize:

 - **The cache for docker layers** you want to export `SINGULARITY_CACHEDIR`

<div>
    <a href="/sregistry-cli/getting-started"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/commands"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
