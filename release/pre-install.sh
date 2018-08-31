#!/bin/sh

# This is intended to be packaged with the rpm, for install on a centos or similar host
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip install -r requirements.txt
