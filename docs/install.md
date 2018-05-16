---
layout: default
title: Installation
pdf: true
permalink: /install
toc: false
---

# Local Install

To install from the Github repository:

```bash
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli
python setup.py install
```

And you can also install from pip:

```bash
# Client and Database
pip install sregistry[all]

# Client only
pip install sregistry[all-basic]
```

Given that the current endpoints are limited, you will do ok with the above 
method. However, when the time comes to install specific modules, you would do
that by specifying the ones you want, e.g.,

```bash
pip install -e .[myclient]
```

To install from pip (granted that @vsoch has updated, this is likely only for
major versions, and it's usually best during development to install from the 
repository).

```bash
pip install sregistry
```

or for a particular extra client:

```bash
pip install sregistry[myclient]
```

# Docker
You can use Singularity Registry Global clients via Docker. Importantly, you need to
run the commands with the `--privileged` flag.

```bash
$ docker run --privileged vanessa/sregistry-cli pull shub://vsoch/hello-world
```

If you need to build the container locally:

```bash
$ docker build -t vanessa/sregistry-cli .
```

# Singularity
Singularity no longer supports running Singularity inside Singularity, and so some commands
will not work as desired. For example:

```bash
 ./sregistry.simg pull shub://vsoch/hello-world
[client|hub] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Progress |===================================| 100.0% 
2.5.1-master.gd6e81547
ERROR  : Singularity is not running with appropriate privileges!
ERROR  : Check installation path is not mounted with 'nosuid', and/or consult manual.
ABORT  : Retval = 255

ERROR Return Code 255: ("\x1b[91mERROR  : Singularity is not running with appropriate privileges!\n\x1b[0m\x1b[91mERROR  : Check installation path is not mounted with 'nosuid', and/or consult manual.\n\x1b[0m\x1b[31mABORT  : Retval = 255\n\x1b[0m",)
[container][update] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
Success! /home/vanessa/.singularity/shub/vsoch-hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg
```

You could run with sudo, but that might defeat the purpose. Most functions should work, and
missing is adding the inspection of the container to the database. It can, of course,
easily be obtained by inspecting the container image directly.

To activate a particular client endpoint, thanks to the [Standard Container Integration Format](https://containersftw.github.io/SCI-F/)
you can just use an `--app` flag instead:

```bash
$ singularity run --app registry sregistry-cli
```

# Clients Available
Singularity Registry Global Client is developed to give you maximum flexibility to install only what you need. For this, you have many different options for installing the software. if you use the above method, you will install the full client and storage, meaning that you can push and pull images to many different clients (Google vs. Singularity Registry) and you can keep a local database file for keeping track of your images. However, it might be that you want to install dependencies for just one client. Remember for all of the pip commands below, you can install with a local repository, or remote.

Install all clients

```bash
# Local repository
pip install -e .[all]

# From pypi
pip install sregistry[all]
```


```bash
# Local repository
pip install -e .[myclient]

# From pypi
pip install sregistry[myclient]
```

And here are your options.

## Clients and Storage
The first set includes `sqlalchemy` so that you can manage a local database of images across clients.
```bash
# Singularity Registry
pip install sregistry[registry]

# Google Storage
pip install sregistry[google-storage]

# Google Drive
pip install sregistry[google-drive]
```

## Clients Only
These do **not** include `sqlalchemy`, meaning you can push and pull, but that's it. There is no database to add records to or store metadata in. 

```bash
# Singularity Registry
pip install sregistry[registry-basic]

# Google Storage
pip install sregistry[google-storage-basic]

# Google Drive
pip install sregistry[google-drive-basic]
```

Clients for Singularity Hub and Nvidia are not detailed here as they don't require additional library dependencies.

