---
layout: default
title: Singularity Google Compute Builder
pdf: true
permalink: /client-google-compute
toc: false
---

# Singularity Google Compute Builder

The Google Compute Builder is the first builder offered by the `sregistry` client! Using your Google Cloud
project you can deploy builds to Google Compute Engine and then have images saved in Google Storage. This
in essence is a mini "Singularity Hub" that you have complete control over. For the command line usage, continue
reading the Getting Started below!

## Quick Start
For the quickstart you need: 

 - your `GOOGLE_APPLICATION_CREDENTIALS` and `GOOGLE_CLOUD_PROJECT` exported to the environment
 - sregistry [installed](/sregistry-cli/install) with the `google-compute` client dependencies

If you want to set the Google Compute builder as your current active client:

```bash
$ sregistry backend activate google-compte
[activate] google-compute
$ sregistry backend status
[backend status]
There are 9 clients found in secrets.
active: google-compute
```

The following sections demonstrate the most common usage for the build commands! We also provide a [static demo](https://vsoch.github.io/sherlock_vep/) of the current builder interface.

```bash
# Export credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-secrets.json
export GOOGLE_CLOUD_PROJECT=vanessasur-us
export SREGISTRY_CLIENT=google-compute
```
```bash
# Install
$ pip install sregistry[google-compute]
```
```bash
# View Templates
$ sregistry build templates
```
```bash
# Save a template to customize
$ sregistry build templates /cloud/google/compute/ubuntu/securebuild-2.4.3.json > config.json
```
```bash
# Build with a repo with Singularity recipe in root
$ sregistry build https://www.github.com/vsoch/hello-world 
```
```bash
# Preview a Configuration for the same (don't launch builder)
$ sregistry build --preview https://www.github.com/vsoch/hello-world
```
```bash
# List instances
$ sregistry build instances

# List containers in storage
$ sregistry search
```
```bash
# Get detailed metadata for remote
$ sregistry search vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
```
```bash
# Pull a container
$ sregistry pull vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
```
```bash
# Look at images from compute locally
$ sregistry images | grep google-compute
```
```bash
# Look at metadata for local
$ sregistry inspect vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
```
```bash
# Look at latest log
$ sregistry build logs
```
```bash
# Look at specific logs
$ sregistry build logs vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d
```
```bash
# Run it!
$ singularity run $(sregistry get vsoch/hello-world:latest@3bac21df631874e3cbb3f0cf6fc9af1898f4cc3d)
RaawwWWWWWRRRR!! Avocado!
```

There is more to learn! 

 - For a more detailed tutorial, see the [Detailed Start](/sregistry-cli/client-google-compute-detail)
 - For interaction within Python, see the [Developer Tutorial](/sregistry-cli/client-google-compute-developer)
 - To learn about development of the builders, see docs on [The Builders](https://singularityhub.github.io/builders/)


<div>
    <a href="/sregistry-cli/clients"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-google-storage"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
