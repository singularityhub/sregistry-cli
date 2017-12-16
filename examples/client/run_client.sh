#!/bin/bash

# Interact with Singularity Registry, bash

# This is a simple script to use the singularity command line tool to 
# obtain a manifest and download an image. You will need to install first
# After installing the client

which sregistry
sregistry --help

###################################################################
# Singularity Hub
###################################################################

sregistry list
sregistry list --help
sregistry list vsoch/hello-world

sregistry pull
sregistry pull --help
sregistry pull vsoch/hello-world



###################################################################
# Singularity Registry
#
# The only difference is that when using a registry with some
# authentication, we need to set our credentials file in 
# the environment
# 
###################################################################

export SREGISTRY_CLIENT_SECRETS=$HOME/.sregistry

###################################################################
# Push
###################################################################

sregistry push vsoch-hello-world-master.simg --name dinosaur/avocado --tag delicious
sregistry push vsoch-hello-world-master.simg --name meowmeow/avocado --tag nomnomnom
sregistry push vsoch-hello-world-master.simg --name dinosaur/avocado --tag whatinthe


###################################################################
# List
###################################################################

# All collections
sregistry list

# A particular collection
sregistry list dinosaur

# A particular container name across collections
sregistry list /avocado

# A named container, no tag
sregistry list dinosaur/avocado

# A named container, with tag
sregistry list dinosaur/avocado:delicious

# Show me environment
sregistry list dinosaur/avocado:delicious --env

# Add runscript
sregistry list dinosaur/avocado:delicious --e --r

# Definition recipe (Singularity) and test
sregistry list dinosaur/avocado:delicious --d --t

# All of them
sregistry list dinosaur/avocado:delicious --e --r --d --t

###################################################################
# Delete
###################################################################

sregistry delete dinosaur/avocado:delicious
sregistry list

###################################################################
# Pull
###################################################################

sregistry pull dinosaur/avocado:delicious


###################################################################
# Labels
###################################################################

# All labels
sregistry labels

# A specific key
sregistry labels --key maintainer

# A specific value
sregistry labels --value vanessasaur

# A specific key and value
sregistry labels --key maintainer --value vanessasaur
