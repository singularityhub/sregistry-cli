---
layout: default
title: SRegistry Global Clients: Globus
pdf: true
permalink: /client-registry
toc: false
---

# SRegistry Global Clients: Globus
The `globus` client for `sregistry` is based on the idea to share a user's local storage (the images) via a Globus account. This connection allows the user to directly request images from other Globus connected registries, or any endpoints that have Singularity images. In order to set up this integration, you should be familiar with setting up a Globus personal endpoint, and for this installation example we will walk through doing this on your local machine for the registry storage folder where the Globus endpoint will live.

## How does SRegistry Global Client work with Globus?
We assume that the user has set up the registry storage as a Globus share. When the user issues a pull, push, or other command relevant to a remote endpoint, the endpoint in question is sniffed (not sure how this should look, [posted issue here](https://github.com/globus/globus-sdk-python/issues/270)) for the simple file organization that would identify it is a sregistry storage (a "shub" folder with collections inside. The user is able to retrieve images from that folder, and if push is allowed (writable) to also push images there.

If Globus is ever able to serve content via https, we could also not require the host endpoint to be a share, but that's for later to think about.

# Getting Started
If you haven't already, make sure the globus module is installed. If you are using the Singularity image, it should be included.

```
pip install sregistry[globus]
```

## 1. Create an Endpoint
We will be following the instructions to set up a [globus connect personal](https://www.globus.org/globus-connect-personal) that will serve the Registry, specifically using the linux [instructions for the command line](https://docs.globus.org/how-to/globus-connect-personal-linux/#globus-connect-personal-cli). For me, that looked something like the following:

```
wget https://s3.amazonaws.com/connect.globusonline.org/linux/stable/globusconnectpersonal-latest.tgz
cd /home/vanessa/Documents/
tar xzf /home/vanessa/Downloads/globusconnectpersonal-latest.tgz 
cd globusconnectpersonal-2.3.3/
```

I added the folder to my path so it would be found on my computer, in all shells, everywhere! *evil laugh*.

```
# In $HOME/.profile
PATH=$PATH:/home/vanessa/Documents/globusconnectpersonal-2.3.3
export PATH

# then on command line
source $HOME/.profile
which globusconnectpersonal 
/home/vanessa/Documents/globusconnectpersonal-2.3.3/globusconnectpersonal
```

The documentation doesn't do a good job to mention it, but the next command requires installing the [globus client](https://docs.globus.org/cli/installation/):

```
pip install globus-cli

# check install 
which globus

# login
globus login
```

After the above you should have a browser window open up to log you into the client. Then you can proceed with creating a personal endpoint. It comes down to generating a named endpoint and key, and then running a command to set it up:

```
globus endpoint create --personal my-linux-laptop
globusconnectpersonal -setup <setup-key>

# search for your newly created endpoint
globus endpoint search --filter-scope my-endpoints
```

### What is an endpoint?
Let's stop for a second here and talk super specific things, because I at first did this wrong and was just lost in the wildness. When you create an endpoint, you are saying "my entire laptop is a thing that people can connect to." Your endpoint is your laptop. It's not a single spot on your laptop or a folder, that's something else that you setup on your laptop and this is called a **share.** So the "globus flow" (or whatever you want to call it) looks like this:

 - Create personal endpoint on laptop (the entire thing!)
 - Limit global sharing for that endpoint (we will do this next, this is setting permissions)
 - Define specific **shares** or folders to use for transactions.

We just finished the first bullet, now let's move to the second.

### Permissions
We need to next set permissions for what people can and cannot see on our endpoint. You could arguably just leave as is, but I wanted to limit all sharing to just be reading of my storage folder. I opened this file:

```
vim ~/.globusonline/lta/config-paths
```

and changed the following:

```
~/,0,1
#to
~/.singularity/shub,0,0
```

I *think* the 0,0 means read only. It kind of looks like a little face with a carrot nose, so I'm very distracted as I write this. Then start your endpoint, and see metadata about it:

```
globusconnectpersonal -start &

globusconnectpersonal -statusGlobus Online:   connected
Transfer Status: idle
```

I think you would want to stop and start the endpoint after this change. Note that when I made changes and tried a `globuspersonalconnect -ls <endpoint_id>`, I didn't see any output. I have faith! It doesn't hurt to do a restart:

```
globusconnectpersonal -stop
globusconnectpersonal -start &
```

NOTE: This seems to be a bug that the default endpoint command hides hidden files, and we wouldn't want this to be the case . I'm pausing here for now until this can be resolved.

Finally, make sure to grab your endpoint's id, because we will need to add it to the application to be aware of next. I don't know of the "best way" to search for an endpoint, but I used my email to find it.

```
globus endpoint search vsochat
ID                                   | Owner                | Display Name          
------------------------------------ | -------------------- | ----------------------
74f0809a-d11a-11e7-962c-22000a8cbd7d | vsochat@stanford.edu | vanessasaurus-endpoint
```

or you could search with a filter like "my-endpoints"

```
globus endpoint search --filter-scope my-endpoints
```

## 2. Commands
Here we will review the set of commands that are specific to the SRegistry Globus client:

 - *pull*: `[remote->local]` is a common use case. It says "get this remote registry image and pull it from there to my storage."
 - *push*: `[local->remote]` takes an image on your host and pushes to the registry (if you have permission).
 - *record*: `[remote->local]` obtain metadata and image paths for a remote image and save to the database, but don't pull the container to storage.
 - *search*: `[remote]`: list containers for a remote endpoint, optionally with a search term.
 - *delete*: `[remote]`: delete an image from a remote endpoint if you have the correct credential (note this isn't implemented yet for the registry, but is noted here as a todo).


## Sanity Checks

## Pull

## Record

## Record and Pull

## Inspect

## Search

<div>
    <a href="/sregistry-cli/"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-hub.html"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
