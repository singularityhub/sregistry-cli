---
layout: default
title: Singularity Hub Client
pdf: true
permalink: /client-google-drive
toc: false
---

# SRegistry Client: Google Drive

These sections will detail use of the Google Drive client for `sregistry`, which is a connection to your Google Drive. 

[![asciicast](https://asciinema.org/a/155025.png)](https://asciinema.org/a/155025?speed=3)

## Getting Started
If you are using the [sregistry image](https://www.singularity-hub.org/collections/379), the client is likely already installed. If you want to install this natively (or build a custom container) the command to install the module extras is:

```
pip install sregistry[google-drive]

# or locally
git clone https://www.github.com/singularityhub/sregistry-cli.git
cd sregistry-cli
pip install -e .[google-drive]
```

You will also need to [create a Google Drive credential](https://console.developers.google.com/start/api?id=drive) that will allow you to authenticate and connect to drive. Note that this step is different from the [GOOGLE_APPLICATION_CREDENTIALS](https://cloud.google.com/docs/authentication/getting-started) that you use for Google Storage.

### Creating a Credential
In the Google Cloud Developers console, select the blue button for "Create Credentials" and then "Oauth Client ID." You then can select "Other" and give it a name and it will create a client key and secret for you. At this point, you want to download the json file for it, put it somewhere secure on your computer, and export the path to it in your environment:

```
SREGISTRY_GOOGLE_DRIVE_CREDENTIALS=/path/to/google-drive-secrets.json
export SREGISTRY_GOOGLE_DRIVE_CREDENTIALS
```

After you do this, you will have a file that will allow you to register your client. When you start the client, it will give you a URL to open your browser and give permission to access your Google Drive. Note that the redirect will send you to this webpage, and after accepting send a code back to the client to update your credential. The code is used to generate a token and refresh token that can be used automatically or updated when needed when it expires. The store for the token is determined by the [environment variables you have set](/sregistry-cli/getting-started#environment-variables-list).

### Environment
Singularity Registry Global Client works by way of obtaining information from the environment, which are cached when appropriate for future use. For Google Drive, you are required to [create secrets](https://console.developers.google.com/start/api?id=drive) and then exporting them to the environment:

 - [SREGISTRY_GOOGLE_DRIVE_CREDENTIALS](https://console.developers.google.com/start/api?id=drive): This should be an OAuth Client of type Other, and the full path to file downloaded on your host to it. This is the result of the steps from the [section above](#creating-a-credential)
 - [SREGISTRT_GOOGLE_DRIVE_ROOT](): This is the root folder to use (and create if doesn't exist) in your drive for containers, since likely you have much other content there. If not set, it defaults to `sregistry`. Note that you can use this variable not only for a base, but if you have different groups of containers to maintain (even with the same collection / container uris). For example, I might set a base for development containers to be different than one for production, and that coincides to different root folders in my Google Drive path.

### Fun Environment
By default, your Google Drive containers will have a robot icon. Here he is:

<img src="/sregistry-cli/img/robot.png" width="600px"><br>

But you can choose your own custom thumbnail! Simply export the `SREGISTRY_THUMBNAIL` variable. If you are sharing containers and want some kind of branding, this is a good way to do that.

```
# Globally (or in bash profile)
SREGISTRY_THUMBNAIL = /path/to/myrobot.png
export SREGISTRY_THUMBNAIL

# One off command
SREGISTRY_THUMBNAIL = /path/to/myrobot.png sregistry shell
```

Have fun! For a detailed list of other (default) environment variables and settings that you can configure, see the [getting started](../getting-started) pages. 


## Commands
Now that you have your environment set up, it's time to test out the commands! Remember that there are globally shared commands (e.g., "add", "get", "inspect," "images") that are shared by all clients, and we won't (re-discuss) them here. But if you need a reminder, see the [commands](../getting-started/commands.md) documentation.

Here we will review the set of commands that are specific to the Google Drive client. Google Drive is really special because it was the inspiration for the "share" command.

 - [pull](#pull): `[remote->local]` pull an image from the Singularity Hub registry to the local database and storage.
 - [search](#search): `[remote]` list all image collections in Singularity Hub
 - [record](#record): `[remote->local]` obtain metadata and image paths for a remote image and save to the database, but don't pull the container to storage.
 - [share](share): Share a container! This means sharing a container like you would a file in Google Drive, and the recipient getting an email about the shared container.

For all of the examples below, we will export our client preference to be `google-drive`

```
SREGISTRY_CLIENT=google-drive
export SREGISTRY_CLIENT
```
but note that you could just as easily define the variable for one command:

```
SREGISTRY_CLIENT=google-drive sregistry shell
```

## Shell
After we have exported `SREGISTRY_CLIENT` above, if you are looking to interact with a shell for the google-storage `sregistry` client, just ask for it. If you forgot to export your credentials file, you will be reminded:

```
sregistry shell
ERROR You must export SREGISTRY_GOOGLE_DRIVE_CREDENTIALS to use Google Drive client
https://singularityhub.github.io/sregistry-cli/client-google-drive
```

Then when you export the path, it will load. If you don't have a credential store, your browser will open and ask you to authenticate first, e.g..

```
sregistry shell

Your browser has been opened to visit:

    https://accounts.google.com/o/oauth2/auth?access_type=offline&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&client_id=294329414046-50iddkj7p3olk657hhj47q388aj1oo31.apps.googleusercontent.com&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive&response_type=code

If your browser is on a different machine then exit and re-run this
application with the command-line parameter

  --noauth_local_webserver

Created new window in existing browser session.
Authentication successful.
```

If you already have a store (or disabled keeping one) it will open directly to the shell:

```
sregistry shell
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
Python 3.5.2 |Anaconda 4.2.0 (64-bit)| (default, Jul  2 2016, 17:53:06) 
Type "copyright", "credits" or "license" for more information.

IPython 5.1.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
```

Here we see straight away that we are interacting with a folder at the root of our drive called "sregistry" (the default) and the google-drive client. The printing of this folder without error means a successful connection to your drive.


## Search
The most exciting new function added, thanks to Google Drive, is the ability to share! So let's show it first. First we can look at the containers available to us in our drive. This is what search is for, and we can be brief and then jump to share:


```
sregistry search
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
[drive://sregistry] Containers
   [drive://sregistry] 		[id]	[uri]
1  1LuHUUhEMiWulnJiqBF0-5DgiJvSsvuPq	vsoch/hello-world:latest@846442ecd7487f99fce3b8fb68ae15af
2  1HO6Y4cmC9UeLizSUptyZA28KQ5mNvCTw	vsoch/hello-world:latest@846442ecd7487f99fce3b8fb68ae15af
3  1qOVpMmk4nAg0IX0rG_QT_GT5VpV5cKUe	expfactory/expfactory:master
```

We don't have very many, so I can confidently search for "expfactory" and know that the first returned result is that third image. If I wanted to just search for this query, I could get a bunch more metadata about it:


```
sregistry search expfactory
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
[drive://sregistry] Found 1 containers
expfactory/expfactory:master
id         1qOVpMmk4nAg0IX0rG_QT_GT5VpV5cKUe
tag        master
uri        expfactory/expfactory:master
type       container
name       expfactory/expfactory:master.simg
image      expfactory
version    846442ecd7487f99fce3b8fb68ae15af
storage    expfactory/expfactory:master.simg
collection expfactory
org.label-schema.usage /.singularity.d/runscript.help
org.label-schema.build-size 544MB
org.label-schema.build-date 2017-11-07T15:08:18+00:00
org.label-schema.schema-version 1.0
org.label-schema.usage.singularity.deffile Singularity
org.label-schema.usage.singularity.version 2.4-feature-squashbuild-secbuild.g818b648
org.label-schema.usage.singularity.deffile.from ubuntu:14.04
org.label-schema.usage.singularity.runscript.help /.singularity.d/runscript.help
org.label-schema.usage.singularity.deffile.bootstrap docker

```

Old news! Let's get to the fun... the new "share" function!

## Share
The most exciting new function added, thanks to Google Drive, is the ability to share! Let's use the share command to send to container we found above to my (or someone else's) email:

```
sregistry share --email vsochat@stanford.edu expfactory
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
expfactory
Share to vsochat@stanford.edu complete: 09522476006874428495!
```

Now when I look in my inbox... hoho!

<img src="/sregistry-cli/img/google-drive-share.png" width="800px"><br>

And how about sharing with a friend? Yes, this in fact did happen - it was received on a smart phone and added to drive.

>> Share them from a car? <br>
>> Or share them in a bar?  <br>
>> Share them on a plane, <br>
>> ...or whilst in Spain! <br>
>> No matter where you are... <br>
>> your containers are never far! <br>

<img src="/sregistry-cli/img/google-drive-share-phone.png" width="400px"><br>


**Note** to future self, do not allow self to write "poetry" at 1:00am.

But you want to know what is most exciting? The share has a robot thumbnail. That you can customize by exporting a path to `SREGISTRY_THUMBNAIL` on your host, however you please! Let's look at him again, because we can.

<img src="/sregistry-cli/img/google-drive-robot.png" width="400px"><br>


If you don't feel sheer joy and life completion from having robots in your Google Drive, I'm not sure anything can help you now, my friend. Okay, let's now bring down the excitement and go back to square one... time to review the basics! Starting with a push.


## Push
Here we have an image on my Desktop. let's push it to Google Drive.

```
sregistry push --name vsoch/hello-world:pancakes vsoch-hello-world-master-latest.simg
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f.simg
```

This push is a little different - I opted to use the robot spinner instead of the progress bar.

Now let's search our remote to see the record that was added:

```
sregistry search
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
[drive://sregistry] Containers
   [drive://sregistry] 		[id]	[uri]
1  1WUnfqLMxemo1QiFz3G0dFrVmYNs78-mt	vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f
2  1cTzw47GstQxF4NXrpdzxIoRwn7ZjCz1J	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
3  1qOVpMmk4nAg0IX0rG_QT_GT5VpV5cKUe	expfactory/expfactory:master
5  1HO6Y4cmC9UeLizSUptyZA28KQ5mNvCTw	vsoch/hello-world:latest@846442ecd7487f99fce3b8fb68ae15af
```

Yes, I've been testing the same image many times, and naming it the same thing :). Note that it's currently a bug I anticipate that pushing the same image will result in TWO equally named files. What we need to do is first query based on the metadata and then perform an update instead of create. It's too late to start now, but if you want to jump on it please [open an issue and go for it!](https://www.github.com/singularityhub/sregistry-cli/issues)

At this point you have remote records, but no images locally. You could do a "get" or an "inspect".

Note that if you try to manually upload images to your Google Drive, they won't be found by the client. This is because in order to be identified as containers, they have a value in their properties (metadata) for `type:container`. Thus, if you use some different method to add containers to your Google Drive `sregistry` folder, you should minimally set this metadata.


## Get
For a remote image record, if you do a "get" you will be given the remote url:

```
sregistry get expfactory/expfactory:master
https://www.googleapis.com/drive/v3/files/1qOVpMmk4nAg0IX0rG_QT_GT5VpV5cKUe?alt=media
```

If you don't want to get the url but you want to look at all metadata, then use "inspect."

## Inspect
Of course you can inspect an image (here we will inspect the image we just pushed above), and you will see a ton of goodness:

```
sregistry inspect expfactory/expfactory:master
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
expfactory/expfactory:master
https://www.googleapis.com/drive/v3/files/1qOVpMmk4nAg0IX0rG_QT_GT5VpV5cKUe?alt=media
{
    "client": "google-drive",
    "collection": "expfactory",
    "collection_id": 2,
    "created_at": "2018-01-01 05:38:25",
    "id": 6,
    "image": null,
    "metrics": {
        "id": "1qOVpMmk4nAg0IX0rG_QT_GT5VpV5cKUe",
        "name": "expfactory/expfactory:master.simg",
        "properties": {
            "collection": "expfactory",
            "image": "expfactory",
            "org.label-schema.build-date": "2017-11-07T15:08:18+00:00",
            "org.label-schema.build-size": "544MB",
            "org.label-schema.schema-version": "1.0",
            "org.label-schema.usage": "/.singularity.d/runscript.help",
            "org.label-schema.usage.singularity.deffile": "Singularity",
            "org.label-schema.usage.singularity.deffile.bootstrap": "docker",
            "org.label-schema.usage.singularity.deffile.from": "ubuntu:14.04",
            "org.label-schema.usage.singularity.runscript.help": "/.singularity.d/runscript.help",
            "org.label-schema.usage.singularity.version": "2.4-feature-squashbuild-secbuild.g818b648",
            "storage": "expfactory/expfactory:master.simg",
            "tag": "master",
            "type": "container",
            "uri": "expfactory/expfactory:master",
            "version": "846442ecd7487f99fce3b8fb68ae15af"
        }
    },
    "name": "expfactory",
    "tag": "master",
    "uri": "expfactory/expfactory:master",
    "url": "https://www.googleapis.com/drive/v3/files/1qOVpMmk4nAg0IX0rG_QT_GT5VpV5cKUe?alt=media",
    "version": ""
}
```

One thing I'm not happy about is the subtle differences between the metadata data structures between clients. A lot of this has to do with having different APIs, but I think we can generally do better. Please [post an issue](https://www.github.com/singularityhub/sregistry-cli/issues) if you have ideas!


### Record
Finally, if you don't have a record locally but want to get one that already exists, then use record. Here I look at images on the remote:

```
sregistry search
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
[drive://sregistry] Containers
   [drive://sregistry] 		[id]	[uri]
1  1WUnfqLMxemo1QiFz3G0dFrVmYNs78-mt	vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f
2  1qOVpMmk4nAg0IX0rG_QT_GT5VpV5cKUe	expfactory/expfactory:master
```

Then I ask for the record based on the Google Drive id:

```
vanessa@vanessa-ThinkPad-T460s:~/Desktop$ sregistry record 1WUnfqLMxemo1QiFz3G0dFrVmYNs78-mt
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
Searching for 1WUnfqLMxemo1QiFz3G0dFrVmYNs78-mt in drive://sregistry
[container][new] vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f
```

The search is done and the record created, and I can see it (the last one with pancakes):

```
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
Containers:   [date]   [location]  [client]	[uri]
1  December 29, 2017	local 	   [google-drive]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
2  December 30, 2017	remote	   [google-storage]	expfactory/expfactory:metadata@846442ecd7487f99fce3b8fb68ae15af
3  December 30, 2017	local 	   [google-storage]	vsoch/avocados:tacos@ed9755a0871f04db3e14971bec56a33f
4  January 01, 2018	remote	   [google-drive]	expfactory/expfactory:master
5  January 01, 2018	remote	   [google-drive]	vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f
```

If you had an image already, it won't be replaced, but the record will be updated.


### Pull
With pull, we might have a record (or did a search to find a container that we liked, as shown above). In this case, instead of inspect or get, we just use pull.

```
sregistry pull vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f
[client|google-drive] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[folder][sregistry]
Searching for vsoch/hello-world:pancakes@ed9755a0871f04db3e14971bec56a33f in drive://sregistry
```

And then you have it locally. Be careful with download quotas for images with this method - I tested the same thing a bunch of times, and got an error about exceeding my quota. That probably means it's time to call it day! Happy New Year from @vsoch and the robots! :D

<div>
    <a href="/sregistry-cli/client-google-storage"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-registry"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
