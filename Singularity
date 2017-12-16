Bootstrap: docker
From: continuumio/miniconda3

# sudo singularity build sregistry.simg Singularity

%runscript
    exec /opt/conda/bin/sregistry "$@"

%apprun sregistry
    exec /opt/conda/bin/sregistry "$@"

%labels
    maintainer vsochat@stanford.edu

%post
    apt-get update && apt-get install -y git
    /opt/conda/bin/pip install dateutils

    # Install Singularity
    cd /opt && git clone https://www.github.com/singularityware/singularity.git && cd singularity
    ./autogen.sh && ./configure --prefix=/usr/local && make && make install

    # Install SRegistry Global
    cd /opt && git clone https://www.github.com/singularityhub/sregistry-cli
    cd sregistry-cli
    /opt/conda/bin/pip install setuptools
    /opt/conda/bin/python setup.py install
