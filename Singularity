Bootstrap: docker
From: continuumio/miniconda3

%runscript
exec /opt/conda/bin/sregistry "$@"

%apprun sregistry
exec /opt/conda/bin/sregistry "$@"

%labels
maintainer vsochat@stanford.edu

%post
apt-get update && apt-get install -y git

# Dependncies
/opt/conda/bin/conda install -y numpy scikit-learn cython pandas

# Install Singularity Python
cd /opt
git clone https://www.github.com/singularityhub/sregistry-cli
cd sregistry-cli
/opt/conda/bin/pip install setuptools
/opt/conda/bin/pip install -r requirements.txt
/opt/conda/bin/pip install pyasn1==0.4.1
/opt/conda/bin/python setup.py sdist
/opt/conda/bin/python setup.py install
