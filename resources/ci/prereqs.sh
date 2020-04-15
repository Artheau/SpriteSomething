#!/bin/bash

sudo apt-get install python3-dev python3-pil python3-pil.imagetk python3-setuptools python3-tk curl
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
python3 -m pip install --upgrade pip
python3 -m pip install testresources
pip3 install -U wheel
pip3 install -r "./resources/app/meta/manifests/pip_requirements.txt"
