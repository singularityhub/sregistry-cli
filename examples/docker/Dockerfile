FROM continuumio/miniconda3

# docker build -t vanessa/sregistry-cli .

ENV PATH /opt/conda/bin:$PATH
LABEL maintainer vsochat@stanford.edu

RUN apt-get update && apt-get install -y git && \
    /opt/conda/bin/conda install -y numpy scikit-learn cython pandas

WORKDIR /opt
RUN git clone https://www.github.com/singularityhub/sregistry-cli
WORKDIR sregistry-cli
RUN /opt/conda/bin/pip install setuptools && \
    #/opt/conda/bin/pip install -r requirements.txt && \
    #/opt/conda/bin/pip install pyasn1==0.4.1 && \
    /opt/conda/bin/python setup.py sdist && \
    /opt/conda/bin/python setup.py install && \
    apt-get clean

CMD ["/opt/conda/bin/sregistry"]
