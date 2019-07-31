#!/bin/bash

set -ev

#get archive utility
choco install archiver

#get python
choco install python

#export path of python
export PATH=/c/Python37:/c/Python37/Scripts:$PATH

#get pip getter
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

#get pip
${PYTHON_EXECUTABLE} get-pip.py
${PYTHON_EXECUTABLE} -m pip install --upgrade pip
