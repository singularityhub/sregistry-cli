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

echo "Step 1: Installing Git Dependency"
sudo apt-get update && apt-get install -y git curl


################################################################################
# Google Metadata
#
# Maintain build routine in builders repository, so minimal changes needed to
# sregistry client.

echo "Step 2: Preparing Metadata"

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

# TODO: We should parse this into a logfile

METADATA="http://metadata/computeMetadata/v1/instance/attributes"
HEAD="Metadata-Flavor: Google"

SREGISTRY_BUILDER_KILLHOURS=$(curl ${METADATA}/SREGISTRY_BUILDER_KILLHOURS -H "${HEAD}")
SREGISTRY_BUILDER_REPO=$(curl ${METADATA}/SREGISTRY_BUILDER_REPO -H "${HEAD}")
SREGISTRY_BUILDER_BRANCH=$(curl ${METADATA}/SREGISTRY_BUILDER_BRANCH -H "${HEAD}")
SREGISTRY_BUILDER_RUNSCRIPT=$(curl ${METADATA}/SREGISTRY_BUILDER_RUNSCRIPT -H "${HEAD}")
SREGISTRY_BUILDER_COMMIT=$(curl ${METADATA}/SREGISTRY_BUILDER_COMMIT -H "${HEAD}")
FOLDER=$(basename $REPO)

# Commit

echo "Step 3: Cloning Repository"
git clone -b "${SREGISTRY_BUILDER_BRANCH}" "${SREGISTRY_BUILDER_REPO}" && cd "${FOLDER}"

if [ -x "${SREGISTRY_BUILDER_COMMIT}" ]; then
    git checkout "${SREGISTRY_BUILDER_COMMIT}" .
else
    SREGISTRY_BUILDER_COMMIT=$(git log -n 1 --pretty=format:"%H")
fi

echo "Using commit ${SREGISTRY_BUILDER_COMMIT}"

# Run build

if [ -f "${SREGISTRY_BUILDER_RUNSCRIPT}" ]; then
    echo "Building ${SREGISTRY_BUILDER_RUNSCRIPT}... here we go!"
    timeout -s KILL ${SREGISTRY_BUILDER_KILLHOURS}h exec "${SREGISTRY_BUILDER_RUNSCRIPT}"
else
    echo "Cannot find ${SREGISTRY_BUILDER_RUNSCRIPT}"
    ls
fi

# Builder must bring self down
suicide()
