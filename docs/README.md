---
layout: default
title: {{ site.name }}
pdf: true
permalink: /
---

<div style="float:right; margin-bottom:50px; color:#666">
</div>

<div>
    <img src="img/logo.png" style="float:left">
</div><br><br>


# Singularity Global Client
Welcome to the Singularity Global Client documentation! 

## What is the Singularity Global Client?
The core of this software is a *local* client for the single user to manage images. This means a local (flat file) database orchestrated with a storage folder that is friendly for use on a personal machine or shared resource.

## Why was it created?
The simplest use case of the Singularity Global Client is to provide the single user a local registry for containers, and to have the registry easily connect with other cloud storage services and hosted Singularity tools. It's understood that as a researcher or general developer you have many options for storage, and sometimes your choices are determined by what happens to be provided to you. Singularity, by way of needing to be installed on legacy systems, could never (realistically) implement every storage and endpoint connection that could be wanted. If it did, it would be very challenging to do without using modern libraries that are available on newer operating systems. Singularity Global Client intends to empower Singularity users to interact with containers across these storage types. It exposes a common interface to to connect to and interact with containers both from the command line and from within python (for developers).

Importantly, the Singularity Global Client does not have any dependency on Docker (the current deployment strategies for a Registry or Singularity Hub) and there is no need for extensive setup beyond installation and a single file (sqlite3) database. The user could install the library locally, or just pull a singularity image with it ready to go.

[![asciicast](https://asciinema.org/a/154519.png)](https://asciinema.org/a/154519?speed=4)

## Getting Started
 - [Installation](install): quick steps to get up and running with the Singularity Registry Global Client. This includes a local installation, or the option to use a Singularity image. You also have the option to install a "basic" client (meaning just moving images) or a client and storage (a local sqlachemy database).
 - [Global Commands](commands): While most clients support the same functions (e.g., `pull`) there are a few global commands that, given that they interact with the local user environment consistently across remote resources, are found regardless of the endpoint you connect to. This getting started guide will go through the basic usage for the local client, meaning functions that you can use to manage, inspect, and otherwise interact with images and metadata locally.

## Available Clients
The Singularity Global Client provides interfaces to [Singularity Hub](/sregistry-cli/client-hub), your self-hosted [Singularity Registry](/sregistry-cli/client-registry), [Google Storage](/sregistry-cli/client-google-storage), [Google Drive](/sregistry-cli/client-google-drive), [NVidia Container Cloud](/sregistry-cli/client-nvidia), [Docker](/sregistry-cli/client-docker), and [Dropbox](/sregistry-cli/client-dropbox). You can also start with the [client list here](/sregistry-cli/clients).

## Getting Help
This is an open source project. Please contribute to the package, or post feedback and questions as <a href="https://github.com/singularityhub/sregistry-cli" target="_blank">issues</a>.

## Contributing
 - [Add a Client](/sregistry-cli/contribute-client): How to contribute a new client, meaning a storage or other endpoint for Singularity images.
 - [Documentation](/sregistry-cli/contribute-docs): How to help improve this documentation.

## License

This code is licensed under the Affero GPL, version 3.0 or later [LICENSE](https://github.com/singularityhub/sregistry-cli/blob/master/LICENSE).


<div>
    <a href="/sregistry-cli/getting-started"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
