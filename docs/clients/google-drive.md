---
layout: default
title: Singularity Hub Client
pdf: true
permalink: /client-google-drive
toc: false
---

# SRegistry Client: Google Drive

These sections will detail use of the Google Drive client for `sregistry`, which is a connection to your Google Drive. 

## Getting Started
If you are using the sregistry image, the client is likely already installed. If you want to install this natively (or build a custom container) the command to install the module extras is:

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

![../img/robot.png](../img/robot.png)

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
 - [share](share): Share a container!

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





## Push
If you don't have any images in your bucket, that is probably a good start to add some. In this case we will add an image sitting in our present working directory.

```
sregistry push --name vsoch/hello-world:latest vsoch-hello-world-master-latest.simg
[bucket][sregistry-vanessa]
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[container][update] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media
```

You will see again the connection to the bucket, and then a progress bar that shows the status of the upload, and the progress bar is replaced by the final container url. By default, this push command doesn't add a container to our local storage database, but just a record that it exists in Google. To see the record, you can list your images:

```
sregistry images
[bucket][sregistry-vanessa]
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
Containers:   [date]   [location]  [client]	[uri]
1  December 29, 2017	remote	   [google-storage]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
2  December 30, 2017	remote	   [google-storage]	expfactory/expfactory:test@846442ecd7487f99fce3b8fb68ae15af
```

At this point you have remote records, but no images locally. You could do a "get" or an "inspect".

Note that if you try to manually upload images to your Google Drive, they won't be found by the client. This is because in order to be identified as containers, they have a value in their properties (metadata) for `type:container`. Thus, if you use some different method to add containers to your Google Drive `sregistry` folder, you should minimally set this metadata.



## Get
For a remote image record, if you do a "get" you will be given the remote url:

```
sregistry get vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media
```

If you don't want to get the url but you want to look at all metadata, then use "inspect."

## Inspect
Of course you can inspect an image (here we will inspect the image we just pushed above), and you will see a ton of goodness:

```
sregistry inspect vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
[bucket][sregistry-vanessa]
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media
{
    "client": "google-storage",
    "collection": "vsoch",
    "collection_id": 1,
    "created_at": "2017-12-29 00:05:09",
    "id": 1,
    "image": null,
    "metrics": {
        "attributes": {
            "deffile": "Bootstrap: docker\nFrom: ubuntu:14.04\n\n%labels\nMAINTAINER vanessasaur\nWHATAMI dinosaur\n\n%environment\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n%files\nrawr.sh /rawr.sh\n\n%runscript\nexec /bin/bash /rawr.sh\n",
            "environment": "# Custom environment shell code should follow\n\nDINOSAUR=vanessasaurus\nexport DINOSAUR\n\n",
            "help": null,
            "labels": {
                "MAINTAINER": "vanessasaur",
                "WHATAMI": "dinosaur",
                "org.label-schema.build-date": "2017-10-15T12:52:56+00:00",
                "org.label-schema.build-size": "333MB",
                "org.label-schema.schema-version": "1.0",
                "org.label-schema.usage.singularity.deffile": "Singularity",
                "org.label-schema.usage.singularity.deffile.bootstrap": "docker",
                "org.label-schema.usage.singularity.deffile.from": "ubuntu:14.04",
                "org.label-schema.usage.singularity.version": "2.4-feature-squashbuild-secbuild.g780c84d"
            },
            "runscript": "#!/bin/sh \n\nexec /bin/bash /rawr.sh\n",
            "test": null
        },
        "branch": "master",
        "bucket": "sregistry-vanessa",
        "collection": "vsoch",
        "commit": "e279432e6d3962777bb7b5e8d54f30f4347d867e",
        "contentType": "application/octet-stream",
        "crc32c": "1FCMGQ==",
        "etag": "CIHy5PnTstgCEAE=",
        "generation": "1514668522289409",
        "id": "sregistry-vanessa/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg/1514668522289409",
        "image": "hello-world",
        "kind": "storage#object",
        "md5Hash": "7ZdVoIcfBNs+FJcb7FajPw==",
        "mediaLink": "https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media",
        "metageneration": "1",
        "name": "vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg",
        "selfLink": "https://www.googleapis.com/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg",
        "size": "65347615",
        "size_mb": "333",
        "storage": "vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg",
        "storageClass": "STANDARD",
        "tag": "latest",
        "timeCreated": "2017-12-30T21:15:22.270Z",
        "timeStorageClassUpdated": "2017-12-30T21:15:22.270Z",
        "type": "container",
        "updated": "2017-12-30T21:15:22.270Z",
        "uri": "vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f",
        "version": "ed9755a0871f04db3e14971bec56a33f"
    },
    "name": "hello-world",
    "tag": "latest",
    "uri": "vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f",
    "url": "https://www.googleapis.com/download/storage/v1/b/sregistry-vanessa/o/vsoch%2Fhello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg?generation=1514668522289409&alt=media",
    "version": "ed9755a0871f04db3e14971bec56a33f"
}
```

### Record
Finally, if you don't have a record locally but want to get one that already exists, then use record.

```
sregistry record vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
Searching for vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f in gs://sregistry-vanessa
[container][update] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
```

If you had an image already, it won't be replaced, but the record will be updated.


## Pull and Search
Now let's say that we pushed an image a while back to Google Storage, we have the record locally, and we want to get it. We could use "get" to get the url and then plug it into our special download logic, or we could instead want to pull the image to our local `sregistry` database. This would mean that the "remote" record gets updated to "local" because we actually have the image! How do we do that? We will go through two scenarios. In the first, we've totally forgotten about our local database (or it blew up) and we need to search the remote endpoint. In the second, we have our local database and just want to get one (pull).

### Search
A search without any parameters will essentially list all containers in the configured storage bucket. But how do we know what is a container?

>> a container is defined by having the metadata key "type" with value "container" and this is set by the upload (push) client.

Thus, if you do some fancy operation outside of using the client to upload containers to storage, make sure that you add this metadata value, otherwise they will not be found. Let's do a quick search to get our list in Google Storage. This action has no dependency on a local storage or database.

```
sregistry search
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
[gs://sregistry-vanessa] Containers
1      174 MB	/home/vanessa/desktop/expfactory:latest
2       62 MB	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
```

Then to look at details for a more specific search, let's try searching for "vsoch"

```
sregistry search vsoch
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
[gs://sregistry-vanessa] Found 1 containers
vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg 
id:      sregistry-vanessa/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg/1514668522289409
uri:     vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
updated: 2017-12-30 21:15:24.132000+00:00
size:    62 MB
md5:     7ZdVoIcfBNs+FJcb7FajPw==
```

### Pull
With pull, we might have a record (or did a search to find a container that we liked, as shown above). In this case, instead of inspect or get, we just use pull.

```
sregistry pull vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
Searching for vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f in gs://sregistry-vanessa
Progress |===================================| 100.0% 
[container][update] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
Success! /home/vanessa/.singularity/shub/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg
```

Did you notice that this was an update? The reason is because we already had the record in our database from when we pushed it in the first place, and the record was updated to now be for a local file:

```
sregistry images
sregistry images
[client|google-storage] [database|sqlite:////home/vanessa/.singularity/sregistry.db]
[bucket][sregistry-vanessa]
Containers:   [date]   [location]  [client]	[uri]
1  December 29, 2017	local 	   [google-storage]	vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
2  December 30, 2017	remote	   [google-storage]	expfactory/expfactory:test@846442ecd7487f99fce3b8fb68ae15af
```

and if we do a get, instead of the url we get the path to the file:

```
sregistry get vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
/home/vanessa/.singularity/shub/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg
```

You can also see in the pull output that on the backend of pull is the same search as you did before. This means that
if you want to be precise, you should ask for the complete uri (version included). If you aren't precise, it will do
a search across name fields and give you the first match. Be careful, my linux penguins.

<div>
    <a href="/sregistry-cli/client-google-drive"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry-cli/client-registry.html"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
