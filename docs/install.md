---
layout: default
title: Installation
pdf: true
permalink: /install
toc: false
---

# Installation Local

To install from the Github repository:

```
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli
python setup.py install
```

We recommend for the latest features to use the development branch:

```
git clone -b development https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli
python setup.py install
```

Given that the current endpoints are limited, you will do ok with the above 
method. However, when the time comes to install specific modules, you would do
that by specifying the ones you want, e.g.,

```
pip install -e .[myclient]
```

To install from pip (granted that @vsoch has updated, this is likely only for
major versions, and it's usually best during development to install from the 
repository).

```
pip install sregistry
```

or for a particular extra client:

```
pip install sregistry[myclient]
```

For now, it's probably fastest and easiest to use the Singularity image.

# Clients Available
Singularity Registry Global Client is developed to give you maximum flexibility to install only what you need. For this, you have many different options for installing the software. if you use the above method, you will install the full client and storage, meaning that you can push and pull images to many different clients (Google vs. Singularity Registry) and you can keep a local database file for keeping track of your images. However, it might be that you want to install dependencies for just one client. Remember for all of the pip commands below, you can install with a local repository, or remote.

```
# Local repository
pip install -e .[myclient]

# From pypi
pip install [myclient]
```

And here are your options.

## Clients and Storage
The first set includes `sqlalchemy` so that you can manage a local database of images across clients.
```
# Singularity Registry
pip install sregistry[registry]

# Google Storage
pip install sregistry[google-storage]

# Google Drive
pip install sregistry[google-drive]
```

## Clients Only
These do **not** include `sqlalchemy`, meaning you can push and pull, but that's it. There is no database to add records to or store metadata in. 

```
# Singularity Registry
pip install sregistry[registry-basic]

# Google Storage
pip install sregistry[google-storage-basic]

# Google Drive
pip install sregistry[google-drive-basic]
```

Clients for Singularity Hub and Nvidia are not detailed here as they don't require additional library dependencies.


# Singularity
To build a singularity container

```
sudo singularity build sregistry-cli Singularity
```

And now anywhere in these pages where you run an sregistry command, instead just
reference the image:

```
./sregistry-cli
```

and to activate a particular client endpoint, thanks to the [Standard Container Integration Format](https://containersftw.github.io/SCI-F/)
you can just use an `--app` flag instead:

```
singularity run --app registry sregistry-cli
```

I (@vsoch) expect to be improving these docs (asciinemas!) and adding additional endpoints soon!
