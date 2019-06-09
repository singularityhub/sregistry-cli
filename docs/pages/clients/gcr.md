---
layout: default
title: Google Container Cloud
pdf: true
permalink: /client-gcr
toc: false
---

# Singularity Global Client: Google Container Cloud

These sections will detail of how to connect with the Google Container Cloud using the Singularity Global client. The backend here is actually the same as [docker](/sregistry-cli/client-docker), and the authentication is slightly different. We won't go over every call here (see the Docker pages for the rest) but we will show you how to authenticate here.

## Using GCloud
If you are familiar with the gcloud client, you might know that when you are logged in, you can use a command like this to pull an image:

```bash
$ gcloud docker -- pull gcr.io/deepvariant-docker/deepvariant:0.5.0
```

The sregistry equivalent would then be:

```bash
$ sregistry pull docker://gcr.io/deepvariant-docker/deepvariant:0.5.0
```

If you have a docker config.json on your computer, this command might be sufficient! If not, then you will want to try setting the following environment variables.


```bash
SREGISTRY_DOCKERHUB_USERNAME='_token'
SREGISTRY_DOCKERHUB_BASE="gcr.io"
SREGISTRY_DOCKERHUB_PASSWORD='mysecretpass'
export SREGISTRY_DOCKERHUB_PASSWORD SREGISTRY_DOCKERHUB_BASE SREGISTRY_DOCKERHUB_USERNAME
```

Then you should be able to pull the image, and proceed using the client via the standard [docker commands](/sregistry-cli/client-docker). Continue reading there to see them.


<div>
    <a href="/sregistry-cli/client-dropbox"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-storage"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
