# Singularity Hub Client

These sections will detail use of the Singularity Hub clients for `sregistry`, which is
the default backend client to use given that no other environment variables are set. For a detailed list of
the environment variables and settings that you can configure, see the [getting started](../getting-started) pages. 
For the globally shared commands (e.g., "add", "get", "inspect," "images," and any others that are defined for all clients)
see the [commands](../getting-started/commands.md) documentation. Here we will review the set of commands that are
specific to the Singularity Hub client:

 - *pull*: `[remote->local]` pull an image from the Singularity Hub registry to the local database and storage.
 - *list*: `[remote]` list all image collections in Singularity Hub

Each of these commands will be detailed with examples in the various [client walkthroughs](../clients), and if you are implementing an endpoint, there are also details about how you should "fill in the space" to
implement your custom client.


## Pull
The most likely thing that you would want to do with the client is pull an image. And
if you have just installed sregistry and done nothing else, this is the default client
that is used. The only difference between this pull and the Singularity pull is that
this pull will be saved to your local database. This means you can easily find and
manage images later. Here is how to pull:

```
sregistry pull vsoch/hello-world
[client|hub] [database|/home/vanessa/.singularity/sregistry.db]
Progress |===================================| 100.0% 
[container] vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f
Success! /home/vanessa/.singularity/shub/vsoch/hello-world:latest@ed9755a0871f04db3e14971bec56a33f.simg
```

Notice how the image is saved (and named) under it's collection folder, and with the full path corresponding
to all information about the version we could find. @vsoch might change this storage strategy to have the full
image path correspond to include the collection too - it's not decided if a folder for each collection is the best
way to go. [What do you think](https://www.github.com/singularityhub/sregistry-cli/issues)?

## Inspect
After you pull the image, you can easily inspect it. This includes metadata extracted from
the Singularity Hub API, along with from the image (if Singularity was installed on the host
that downloaded it).

```
sregistry inspect vsoch/hello-world
[client|hub] [database|/home/vanessa/.singularity/sregistry.db]
/home/vanessa/.singularity/shub/vsoch/hello-world:latest.simg
{
    "client": "hub",
    "collection": "vsoch",
    "collection_id": 2,
    "created_at": "2017-12-26 16:31:15",
    "id": 2,
    "image": "/home/vanessa/.singularity/shub/vsoch/hello-world:latest.simg",
    "metrics": {
        "data": {
            "attributes": {
                "deffile": "Bootstrap: docker\nFrom: ubuntu:14.04\n\n%runscript\n\nexec echo \"Tacotacotaco\"\n",
                "environment": "# Custom environment shell code should follow\n\n",
                "help": null,
                "labels": {
                    "org.label-schema.build-date": "2017-10-18T13:54:37+00:00",
                    "org.label-schema.build-size": "341MB",
                    "org.label-schema.schema-version": "1.0",
                    "org.label-schema.usage.singularity.deffile": "Singularity",
                    "org.label-schema.usage.singularity.deffile.bootstrap": "docker",
                    "org.label-schema.usage.singularity.deffile.from": "ubuntu:14.04",
                    "org.label-schema.usage.singularity.version": "2.4-feature-squashbuild-secbuild.g217367c"
                },
                "runscript": "#!/bin/sh \n\n\nexec echo \"Tacotacotaco\"\n",
                "test": null
            },
            "type": "container"
        }
    },
    "name": "hello-world",
    "tag": "latest",
    "uri": null,
    "url": null,
    "version": "22aa66e0c80847c676f34f35e70ea066"
}
```

Notice that the client is relevant to Singularity Hub. You could imagine at some point using
different clients to retrieve images with possibly the same (without version) names, in which case
this keeps them separate. It's less important for this use case, and more important so that in the future when you want to do some operation with this image, we know the backend to use to perform it.


Don't forget that the Singularity Hub client also supports the [global client commands](../getting-started/commands.md)

#########################################
# Pull
#########################################

# Let's initiaelize a client, and look at the commands offered
cli = Client()

# What kind of client? Since we didn't set anything special, it's for SHub
type(cli)
# sregistry.main.hub.Client

# Pull works just as it would with Singularity, but we don't need the uri
image = cli.pull('vsoch/hello-world')
# Progress |===================================| 100.0%
# Success! vsoch-hello-world-latest.simg
image
'vsoch-hello-world-latest.simg'

# You can also pull a list of images, note that you get a list back
images = cli.pull(['vsoch/hello-world', 'singularityhub/hello-registry'])
# Progress |===================================| 100.0% 
# Success! vsoch-hello-world-latest.simg
# Progress |===================================| 100.0% 
# Success! singularityhub-hello-registry-latest.simg

images
# ['vsoch-hello-world-latest.simg', 'singularityhub-hello-registry-latest.simg']
# It's recommended to do in serial, so if one fails you can still get
# the finished paths to the others.


#########################################
# Search
#########################################

# Search is a tool to search or list a *remote* registry. Here is how you
# run it for Singularity HUb to see all container collections
rows = cli.search()

# You can also query by a container - note this currently just supports
# knowing the full name
cli.search('vsoch/hello-world')
# Containers vsoch/hello-world
# 1  [name]	vsoch/hello-world
# 2  [date]	Oct 18, 2017 01:06PM
# 3  vsoch/hello-world:latest



###################################################################
# Push
###################################################################

from singularity.registry.client import Client

sreg = Client()    # Singularity Registry Client
                   # Default base: 127.0.0.1
                   # Secrets: $HOME/.sregistry OR
                   # $SREGISTRY_CLIENT_SECRETS


# Push an image, this is the path on your filesystem
image_path = 'vsoch-hello-world-master.img'

# This is the tag, and image name you want in the registry
image_tag = 'rawr'
image_name = 'vsoch/dinosaurs'

response = sreg.push(path=image_path,
                     name=image_name,
                     tag=image_tag)

# DEBUG Headers found: Content-Type
# [================================] 391/391 MB - 00:00:00
# Upload finished! [Return status 201 created]


###################################################################
# Query
###################################################################
