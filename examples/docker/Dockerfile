FROM continuumio/miniconda3

# docker build -t vanessa/sregistry-cli .

ENV PATH /opt/conda/bin:$PATH
LABEL maintainer vsochat@stanford.edu

RUN apt-get update && apt-get install -y git build-essential \
                   libtool \
                   squashfs-tools \
                   autotools-dev \
                   automake \
                   autoconf \
                   uuid-dev \
                   libssl-dev
WORKDIR /opt
RUN git clone https://www.github.com/singularityware/singularity.git
RUN git clone https://www.github.com/singularityhub/sregistry-cli

WORKDIR /opt/singularity
RUN ./autogen.sh && ./configure --prefix=/usr/local && make && make install

WORKDIR /opt/sregistry-cli
RUN /opt/conda/bin/pip install setuptools && \
    #/opt/conda/bin/pip install -r requirements.txt && \
    #/opt/conda/bin/pip install pyasn1==0.4.1 && \
    /opt/conda/bin/pip install dateutils &&
    /opt/conda/bin/python setup.py sdist && \
    /opt/conda/bin/python setup.py install && \
    apt-get clean

CMD ["/opt/conda/bin/sregistry"]
