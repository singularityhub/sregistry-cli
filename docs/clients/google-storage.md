---
layout: default
title: Singularity Hub Client
pdf: true
permalink: /client-google-storage
toc: false
---

# SRegistry Client: Google Storage

These sections will detail use of the Google Storage client for `sregistry`, which is a connection to a Google Storage
cloud bucket. 

## Getting Started
If you are using the sregistry image, the client is likely already installed. If you want to install this natively (or build a custom container) the command to install the module extras is:

```
pip install sregistry[google-storage]

# or locally
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli
pip install -e .[google-storage]
```

The next steps we will take are to first set up authentication, and then define your Storage Bucket (and other settings) via environment variables. 

### Environment
Singularity Registry Global Client works by way of obtaining information from the environment, which are cached when appropriate for future use. For Google Storage, you will first need to [set up authentication](https://cloud.google.com/docs/authentication/getting-started) by following those steps. It comes down to creating a file and saving it on your system with the variable name `GOOGLE_APPLICATION_CREDENTIALS`. This variable will be found and used every time you use the storage Client, without needing to save anything to the secrets.

Thus, the complete list of this required variable (and other options, with defaults shown) are the following:

 - [GOOGLE_APPLICATION_CREDENTIALS](https://cloud.google.com/docs/authentication/getting-started) should point to the file provided.
 - [SREGISTRY_GOOGLE_STORAGE_BUCKET](https://cloud.google.com/storage/docs/json_api/v1/buckets): is the name for the bucket you want to create. If not provided, we use your username prefixed with "sregistry."

Notice that the first variable is not prefixed with `SREGISTRY_` and this is because it is already defined for the Google namespace, and use by `sregistry`.

For a detailed list of other (default) environment variables and settings that you can configure, see the [getting started](../getting-started) pages.  For the globally shared commands (e.g., "add", "get", "inspect," "images," and any others that are defined for all clients) see the [commands](../getting-started/commands.md) documentation. Here we will review the set of commands that are specific to the Google Storage client:

 - [pull](#pull): `[remote->local]` pull an image from the Singularity Hub registry to the local database and storage.
 - [search](#search): `[remote]` list all image collections in Singularity Hub
 - [record](#record): `[remote->local]` obtain metadata and image paths for a remote image and save to the database, but don't pull the container to storage.


## Pull

## Inspect

## Search

## Record

<div>
    <a href="/sregistry-cli/"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-registry.html"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
