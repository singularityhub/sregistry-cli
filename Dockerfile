FROM continuumio/miniconda3

#########################################
# Singularity Registry Global Client
# 
# docker build -t vanessa/sregistry-cli .
# docker run vanessa/sregistry-cli
#########################################

RUN mkdir /code
ADD . /code
RUN /opt/conda/bin/pip install setuptools
RUN /opt/conda/bin/pip install scif

RUN scif install /code/sregistry-cli.scif
ENTRYPOINT ["scif"]

ENV PATH /usr/local/bin:$PATH
LABEL maintainer vsochat@stanford.edu

RUN apt-get update && apt-get install -y git build-essential \
                   libtool \
                   squashfs-tools \
                   libarchive-dev \
                   autotools-dev \
                   automake \
                   autoconf \
                   uuid-dev \
                   libssl-dev

RUN /opt/conda/bin/pip install dateutils

# Install Singularity
WORKDIR /opt
RUN git clone https://www.github.com/singularityware/singularity.git
WORKDIR singularity
RUN ./autogen.sh && ./configure --prefix=/usr/local && make && make install

WORKDIR /code

RUN /opt/conda/bin/pip install -e .
