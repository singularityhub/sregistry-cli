#!/bin/bash

################################################################################
# Instance Preparation
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#
#
# Copyright (C) 2018-2019 Vanessa Sochat.
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
################################################################################


# Not available in interface, but with interactive shell debugging
LOGFILE=/tmp/.shub-log

echo "Step 1: Installing Git Dependency" | tee -a $LOGFILE
sudo apt-get update && apt-get install -y git curl nginx | tee -a $LOGFILE
sudo service nginx start

################################################################################
# Google Metadata
#
# Maintain build routine in builders repository, so minimal changes needed to
# sregistry client.

echo "Step 2: Preparing Metadata"  | tee -a $LOGFILE

# Installation of Singularity, and custom build routines maintained separately
# to maximize community involvement & minimize needing change sregistry client

###############################################################################
# Kill Function
#
# https://cloud.google.com/compute/docs/access/create-enable-service-accounts-for-instances?hl=en_US
# Instance will kill after finish. Permissions are needed for doing so on the server

function suicide() {
    instance_name=$(hostname)
    metadata_url="http://metadata.google.internal/computeMetadata/v1/instance/zone"
    zone_metadata=$(curl ${metadata_url} -H "Metadata-Flavor:Google")
    IFS=$'/'
    zone_metadata_split=($zone_metadata)
    instance_zone="${zone_metadata_split[3]}"
    gcloud compute instances delete $instance_name --zone $instance_zone --quiet
}

# Builder then kills self :)

METADATA="http://metadata/computeMetadata/v1/instance/attributes"
HEAD="Metadata-Flavor: Google"

SREGISTRY_BUILDER_KILLHOURS=$(curl ${METADATA}/SREGISTRY_BUILDER_KILLHOURS -H "${HEAD}")
SREGISTRY_BUILDER_REPO=$(curl ${METADATA}/SREGISTRY_BUILDER_REPO -H "${HEAD}")
SREGISTRY_BUILDER_ID=$(curl ${METADATA}/SREGISTRY_BUILDER_ID -H "${HEAD}")
SREGISTRY_BUILDER_BUNDLE=$(curl ${METADATA}/SREGISTRY_BUILDER_BUNDLE -H "${HEAD}")
SREGISTRY_BUILDER_BRANCH=$(curl ${METADATA}/SREGISTRY_BUILDER_BRANCH -H "${HEAD}")
SREGISTRY_BUILDER_RUNSCRIPT=$(curl ${METADATA}/SREGISTRY_BUILDER_RUNSCRIPT -H "${HEAD}")
SREGISTRY_BUILDER_COMMIT=$(curl ${METADATA}/SREGISTRY_BUILDER_COMMIT -H "${HEAD}")
SREGISTRY_BUILDER_DEBUGHOURS=$(curl ${METADATA}/SREGISTRY_BUILDER_DEBUGHOURS -H "${HEAD}")

# This is the folder that has the config file in it
BUILDER_BUNDLE=$(dirname $SREGISTRY_BUILDER_BUNDLE)

echo "Metadata found:" | tee -a $LOGFILE
echo | tee -a $LOGFILE
echo "SREGISTRY_BUILDER_KILLHOURS: is ${SREGISTRY_BUILDER_KILLHOURS}
            The number of hours when the builder is automatically terminated.

        SREGISTRY_BUILDER_DEBUGHOURS: ${SREGISTRY_BUILDER_DEBUGHOURS}
            Given a non-zero exit status, the additional hours for debugging.

        SREGISTRY_BUILDER_ID: ${SREGISTRY_BUILDER_ID}
            The id of the builder bundle, corresponding to the relative path.
       
        SREGISTRY_BUILDER_REPO: ${SREGISTRY_BUILDER_REPO}
            The repository where the builder bundle is obtained.

        SREGISTRY_BUILDER_FILE: ${SREGISTRY_BUILDER_BUNDLE}
            The configuration file being used to drive the builder.

        SREGISTRY_BUILDER_BRANCH:  ${SREGISTRY_BUILDER_BRANCH}
            The branch checked out for the builder bundle repository.

        SREGISTRY_BUILDER_RUNSCRIPT: ${SREGISTRY_BUILDER_RUNSCRIPT}
            The entrypoint for the builder, or the script called to do the job.

        SREGISTRY_BUILDER_COMMIT: ${SREGISTRY_BUILDER_COMMIT}
            If defined, a commit to check out for the builder repository." | tee -a $LOGFILE


# Branch, default to master if not set

if [ ! -n "${SREGISTRY_BUILDER_BRANCH:-}" ]; then
    SREGISTRY_BUILDER_BRANCH="master"    
    echo "Setting builder repository branch to $SREGISTRY_BUILDER_BRANCH"
else
    echo "Found builder repository branch $SREGISTRY_BUILDER_BRANCH"
fi

# Work in $HOME

cd /tmp
echo "Step 3: Cloning Repository..." | tee -a $LOGFILE
echo "git clone -b ${SREGISTRY_BUILDER_BRANCH} ${SREGISTRY_BUILDER_REPO}" | tee -a $LOGFILE
git clone -b "${SREGISTRY_BUILDER_BRANCH}" "${SREGISTRY_BUILDER_REPO}" builders && cd builders


# Check out commit, if defined

if [ ! -n "${SREGISTRY_BUILDER_COMMIT:-}" ]; then
    SREGISTRY_BUILDER_COMMIT=$(git log -n 1 --pretty=format:"%H")
else
    git checkout "${SREGISTRY_BUILDER_COMMIT}" .
fi
echo "Using commit ${SREGISTRY_BUILDER_COMMIT}"

# Run build

if [ -d "${BUILDER_BUNDLE}" ]; then
    echo "Found builder bundle folder ${BUILDER_BUNDLE}"
    cd ${BUILDER_BUNDLE}
    ls | tee -a $LOGFILE
fi 

if [ -f "${SREGISTRY_BUILDER_RUNSCRIPT}" ]; then
    echo "Found runscript for build ${SREGISTRY_BUILDER_RUNSCRIPT}... here we go!" | tee -a $LOGFILE
    chmod 0755 ${SREGISTRY_BUILDER_RUNSCRIPT}
    timeout -s KILL ${SREGISTRY_BUILDER_KILLHOURS}h  ./"${SREGISTRY_BUILDER_RUNSCRIPT}" | tee -a $LOGFILE
    ret=$?

    # If return value is 0, shut down
    if [ $ret -eq "0" ]; then
        echo "Successful build! Terminating instance."
        suicide

    # If not, keep open for additional hours
    else
        echo "Unsuccessful build, will remain running for ${SREGISTRY_BUILDER_DEBUGHOURS}"
        sleep "${SREGISTRY_BUILDER_DEBUGHOURS}h"
    fi
else
    echo "Cannot find ${SREGISTRY_BUILDER_RUNSCRIPT}" | tee -a $LOGFILE
    ls | tee -a $LOGFILE
fi

suicide
