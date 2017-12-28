Bootstrap: docker
From: continuumio/miniconda3

# sudo singularity build sregistry.simg Singularity


#######################################
# Global
#######################################

%runscript
    exec /opt/conda/bin/sregistry "$@"


#######################################
# Singularity Hub
#######################################

%appenv hub
    SREGISTRY_CLIENT=hub
    export SREGISTRY_CLIENT


#######################################
# Singularity Registry
#######################################

%appenv registry
    SREGISTRY_CLIENT=registry
    export SREGISTRY_CLIENT


%labels
    maintainer vsochat@stanford.edu

%post
    apt-get update && apt-get install -y git build-essential \
                   libtool \
                   squashfs-tools \
                   autotools-dev \
                   automake \
                   autoconf \
                   uuid-dev \
                   libssl-dev

    /opt/conda/bin/pip install dateutils

    # Install Singularity
    cd /opt && git clone https://www.github.com/singularityware/singularity.git && cd singularity
    ./autogen.sh && ./configure --prefix=/usr/local && make && make install

    # Install SRegistry Global
    cd /opt && git clone -b add/globus https://www.github.com/singularityhub/sregistry-cli
    cd sregistry-cli
    /opt/conda/bin/pip install setuptools

    # This installs all "install extras"
    /opt/conda/bin/pip install -e .
