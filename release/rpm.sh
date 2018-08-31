#!/bin/bash

# This is intended to be run alongside a command to package to pypi
python setup.py bdist_rpm --spec-only --pre-install release/pre-install.sh
