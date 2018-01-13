Bootstrap: docker
From: continuumio/miniconda3

# sudo singularity build sregistry.simg Singularity


#######################################
# Global
#######################################

%runscript
    exec /opt/conda/bin/sregistry "$@"


#######################################
# Google Cloud Storage
#######################################

%appenv google-storage
    SREGISTRY_CLIENT=google-storage
    export SREGISTRY_CLIENT
%apprun google-storage
    exec /opt/conda/bin/sregistry "$@"



#######################################
# Google Cloud Drive
#######################################

%appenv google-drive
    SREGISTRY_CLIENT=google-drive
    export SREGISTRY_CLIENT
%apprun google-drive
    exec /opt/conda/bin/sregistry "$@"



#######################################
# Singularity Hub
#######################################

%appenv hub
    SREGISTRY_CLIENT=hub
    export SREGISTRY_CLIENT
%apprun hub
    exec /opt/conda/bin/sregistry "$@"


#######################################
# Singularity Registry
#######################################

%appenv registry
    SREGISTRY_CLIENT=registry
    export SREGISTRY_CLIENT
%apprun registry
    exec /opt/conda/bin/sregistry "$@"


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
    cd /opt && git clone https://www.github.com/singularityhub/sregistry-cli
    cd sregistry-cli
    /opt/conda/bin/pip install setuptools

    # This installs all "install extras"
    /opt/conda/bin/pip install -e .
    /opt/conda/bin/pip install -e .[google-drive]
    /opt/conda/bin/pip install -e .[google-storage]
