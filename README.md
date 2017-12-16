# Singularity Global Client

Hi Friends! Are your containers lonely? Singularity containers thrive in happiness when they are shared. This means that wherever you might have them in these cloudy places, they are easy to find and move around.

## What is this?

Singularity Global Client is an interface to interact with Singularity containers in many different storage locations. We are able to use modern APIs by way of providing and using the software within a Singularity container! For older architectures, we provide a [Singularity container](Singularity) for you to use instead.

The library is currently under heavy development, and it will be announced when the beta is ready. Stay tuned!

## What is this client for?

The Singularity Global client is based on a simple organizational model that is flexible to fit in with your storage options of choice. There are multiple different kinds of storage that you might want to use for your images (think of Singularity Registry vs. Dropbox, for example), and likely you are limited in your choosing based on the resources available to you. Why not just give you freedom to use any of those options, and move easily between them?

Toward this goal, the Singularity Global Client is an interface to pull, push, and authenticate with different storage backends so that you can be empowered to push and pull as you like. The following backends are included:


## What backend should I use?

### Singularity Hub
If you have a **few container collections** and value **version control** and **collaboration on recipes** then you are encouraged to use [Singularity Hub](https://www.singularity-hub.org), which works via commits or deployments from Github or manual triggers to build recipes from a repository. It will build your containers for you, and make them accessible for push and pull via `sregistry`. If you are a scientist and don't have a build environment other than your local machine, this is the way to go!

### Singularity Registry
If you want **control** of your own registry, a nice web interface, (optionally) an ability to manage users, and can build on premise (or on your local machine), then you should use [Singularity Registry](https://www.github.com/singularityhub/sregistry). This means that you will serve a web portal like Singularity Hub for your container collections, and it can be customized for yourself or your institution. The files will live on the server (or personal computer) where you installed it, and you can use any of the plugins (e.g., LDAP or Globus) that come with it. This is also a nice option for the single user that wants to quickly organize and find images just via a deployment on localhost.

### Personal Cloud Storage
If you have enough space and want storage for your personal images, then you can use services like Google Drive, Google Storage, and Dropbox. These 


[![asciicast](https://asciinisema.org/a/152866.png)](https://asciinema.org/a/152866?speed=3)

## Help and Contribution
This is an open source project. Please contribute to the package, or post feedback and questions as <a href="https://github.com/singularityhub/sregistry-cli" target="_blank">issues</a>.

## License

This code is licensed under the Affero GPL, version 3.0 or later [LICENSE](LICENSE).
