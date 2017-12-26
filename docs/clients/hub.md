# Singularity Hub Client

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

#

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
