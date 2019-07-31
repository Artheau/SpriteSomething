#!/bin/bash

set -ev

#get pip getter
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

#get pip
${PYTHON_EXECUTABLE} get-pip.py
${PYTHON_EXECUTABLE} -m pip install --upgrade pip

#get archive utility
choco install archiver
