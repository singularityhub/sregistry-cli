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

## Getting Started
 - [Installation](install): quick steps to get up and running with the Singularity Registry Global Client. This includes a local installation, or the option to use a Singularity image.
 - [Global Commands](commands): While most clients support the same functions (e.g., `pull`) there are a few global commands that, given that they interact with the local user environment consistently across remote resources, are found regardless of the endpoint you connect to. This getting started guide will go through the basic usage for the local client, meaning functions that you can use to manage, inspect, and otherwise interact with images and metadata locally.

## Available Clients
 - [Singularity Hub](https://www.singularity-hub.org) [default] is a cloud hosted builder service to connect your Github repositories to, and Singularity recipes found within will be built and available via the Singularity command line and Singularity Global Client tools. If you are a scientist that values version control, collaboration, and image sharing and you don't have a build environment other than your local machine, this is the way to go!
 - [Singularity Registry](registry-client): is one level up from the global client, because it provides a complete web interface, and substantial database (postgresql) for management of Singularity images. This can be used by a user on a local machine, and is best suited for an institution that wants to host their own registry.

## Which should I use?
In the context below, each of these endpoints represents a remote service that you would interact with. It could be the case that you host your own Singulairty Registry, but then have the need to (still) interact with someone else's. By default, you will get the most commonly wanted, which is Singularity Hub.

*Singularity Hub*
If you have a **few container collections** and value **version control** and **collaboration on recipes** then you are encouraged to use [Singularity Hub](https://www.singularity-hub.org). It will build via commits, deployments, or manual triggers. [Read more](clients/hub.md). 

*Singularity Registry*
If you want **control** of your own registry, a nice web interface, (optionally) an ability to manage users, and can build on premise (or on your local machine), then you should use [Singularity Registry](https://www.github.com/singularityhub/sregistry). This means that you will serve a web portal like Singularity Hub for your container collections, and it can be customized for yourself or your institution. The files will live on the server (or personal computer) where you installed it, and you can use any of the plugins (e.g., LDAP) that come with it. This is also a nice option for the single user that wants to quickly organize and find images just via a deployment on localhost, but wants a little more than a small sqlite3 database.

## Getting Help
This is an open source project. Please contribute to the package, or post feedback and questions as <a href="https://github.com/singularityhub/sregistry-cli" target="_blank">issues</a>.

## Contributing
 - [Add a Client](contributing/client.md): How to contribute a new client, meaning a storage or other endpoint for Singularity images.
 - [Documentation](contributing/docs.md): How to help improve this documentation.

## License

This code is licensed under the Affero GPL, version 3.0 or later [LICENSE](LICENSE).


<div>
    <a href="/sregistry-cli/install"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
