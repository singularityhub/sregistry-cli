---
layout: default
title: SRegistry Clients
pdf: true
permalink: /clients
toc: false
---

# Singularity Global Clients
Singularity Registry Global client has tutorials and walkthroughs for the following clients:

 - [Global Commands](/sregistry-cli/commands): commands for all clients.
 - [Amazon Elastic Container Registry](/sregistry-cli/client-aws): create your AWS ECR registry and pull images from it.
 - [Ceph Storage](/sregistry-cli/client-ceph): use [swift](http://docs.ceph.com/docs/jewel/radosgw/swift/python/) to interact with ceph storage.
 - [Docker Hub](/sregistry-cli/client-docker): interact with layers to build images from Docker Hub
 - [Dropbox](/sregistry-cli/client-dropbox): interact with images stored in Dropbox
 - [GitLab](/sregistry-cli/client-gitlab): pull your GitLab build artifacts
 - [Google Container Registry](/sregistry-cli/client-gcr): the same as docker. Here are tricks for authenticating if you have trouble.
 - [Google Storage](/sregistry-cli/client-google-storage): interact with images from Google Storage
 - [Google Drive](/sregistry-cli/client-google-drive): interact with images from Google Drive
 - [Globus](/sregistry-cli/client-globus): transfer images to/from a Globus endpoint
 - [Nvidia Container Registry](/sregistry-cli/client-nvidia): Nvidia Container registry serves Docker images
 - [Singularity Hub](/sregistry-cli/client-hub): the default endpoint will work (search and pull) images from Singularity Hub.
 - [Singularity Registry](/sregistry-cli/client-registry): to interact with an institution or personally hosted Singularity Registry.

## Builders
For a subset of the clients above, we have developed remote builders, meaning that
you can issue a command locally to use your remote credential to deploy a remote builder.
We provide details for builders here.

 - [Google Compute](/sregistry-cli/client-google-compute): Build an image on Google Compute and upload to Google Storage.


## Debugging
Troubleshooting is just as important as usage! Here are some quick guides to debugging common errors. If you have an error that isn't represented, please <a href="https://www.github.com/singularityhub/sregistry-cli/issues" target="_blank">reach out</a>.

 - [Docker Pulling Errors](/sregistry-cli/client-docker-debugging): walk through pulling a container from gcr.io and inspecting the manifest responses.
 - [Google Cloud Errors](/sregistry-cli/client-google-debugging) interact with the Google Cloud Python API to reveal underlying reasons you can't connect to a bucket or service.

<div>
    <a href="/sregistry-cli/getting-started"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/commands"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
