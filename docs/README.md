# Singularity Global Client

The simplest use case of the Singularity Global Client is to provide the single user a local registry for containers, and to have the registry easily connect with other cloud storage servies and hosted Singularity tools. It's understood that as a researcher or general developer you have many options for storage, and singularity global client intends to make it easy to connect to them, both from the command line and from within python (for developers).

## Getting Started

 - [Global Commands](getting-started/README.md): While most clients support the same functions (e.g., `pull`) there are a few global commands that, given that they interact with the local user environment consistently across remote resources, are found regardless of the endpoint you connect to.


## Available Clients
 - [Singularity Global Client](clients/local.md): A *local* client for the single user to manage images. There is no dependency on Docker, or need for extensive setup beyond installation and a single file (sqlite3) database. This would work well on a personal machine or the home node of your cluster.
 - [Singularity Registry](clients/registry.md): is one level up from the global client, because it provides a complete web interface, and substantial database (postgresql) for management of Singularity images. This can be used by a user on a local machine, and is best suited for an institution that wants to host their own registry.
 - [Singularity Hub](https://www.singularity-hub.org) is a cloud hosted builder service to connect your Github repositories to, and Singularity recipes found within will be built and available via the Singularity command line and Singularity Global Client tools. If you are a scientist that values version control, collaboration, and image sharing and you don't have a build environment other than your local machine, this is the way to go!

## Under Development Clients
 - [Globus](clients/globus.md): For users of Globus, this integration will allow for saving and sharing images via Globus endpoints.


## Which should I use?
In the context below, each of these endpoints represents a remote service that you would interact with. It could be the case that you host your own Singulairty Registry, but then have the need to (still) interact with someone else's.

*Singularity Hub*
If you have a **few container collections** and value **version control** and **collaboration on recipes** then you are encouraged to use [Singularity Hub](https://www.singularity-hub.org). It will build via commits, deployments, or manual triggers. [Read more](clients/hub.md). 

*Singularity Registry*
If you want **control** of your own registry, a nice web interface, (optionally) an ability to manage users, and can build on premise (or on your local machine), then you should use [Singularity Registry](https://www.github.com/singularityhub/sregistry). This means that you will serve a web portal like Singularity Hub for your container collections, and it can be customized for yourself or your institution. The files will live on the server (or personal computer) where you installed it, and you can use any of the plugins (e.g., LDAP) that come with it. This is also a nice option for the single user that wants to quickly organize and find images just via a deployment on localhost, but wants a little more than a small sqlite3 database.

## Help and Contribution
This is an open source project. Please contribute to the package, or post feedback and questions as <a href="https://github.com/singularityhub/sregistry-cli" target="_blank">issues</a>.


## License

This code is licensed under the Affero GPL, version 3.0 or later [LICENSE](LICENSE).
