#!/bin/bash

################################################################################
# Instance Preparation
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#
#
# Copyright (C) 2018 The Board of Trustees of the Leland Stanford Junior
# University.
# Copyright (C) 2018 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################

sudo apt-get update && apt-get install -y git curl

# Not available in interface, but with interactive shell debugging
LOGFILE=/tmp/.shub-log
echo "Step 1: Installing Git Dependency" | tee -a $LOGFILE

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
BUILDER_BUNDLE=$(dirname $SREGISTRY_BUILDER_BUNDLE)

echo "Metadata found:" | tee -a $LOGFILE
echo | tee -a $LOGFILE
echo "SREGISTRY_BUILDER_KILLHOURS: is ${SREGISTRY_BUILDER_KILLHOURS}
            The number of hours when the builder is automatically terminated.

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

if [ -z "${SREGISTRY_BUILDER_BRANCH:-}" ]; then
    SREGISTRY_BUILDER_BRANCH="master"    
    echo "Setting builder repository branch to $SREGISTRY_BUILDER_BRANCH"
else
    echo "Found builder repository branch $SREGISTRY_BUILDER_BRANCH"
fi

echo "Step 3: Cloning Repository" | tee -a $LOGFILE
echo "git clone -b ${SREGISTRY_BUILDER_BRANCH} ${SREGISTRY_BUILDER_REPO}" | tee -a $LOGFILE
git clone -b "${SREGISTRY_BUILDER_BRANCH}" "${SREGISTRY_BUILDER_REPO}" builders && cd builders


# Check out commit, if defined

if [ -z "${SREGISTRY_BUILDER_COMMIT:-}" ]; then
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
    timeout -s KILL ${SREGISTRY_BUILDER_KILLHOURS}h exec "${SREGISTRY_BUILDER_RUNSCRIPT}" | tee -a $LOGFILE
else
    echo "Cannot find ${SREGISTRY_BUILDER_RUNSCRIPT}" | tee -a $LOGFILE
    ls | tee -a $LOGFILE
fi

# Builder must bring self down
suicide() | tee -a $LOGFILE
