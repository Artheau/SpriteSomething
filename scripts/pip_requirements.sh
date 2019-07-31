#!/bin/bash

set -ev

#windows doesn't always have this by default like the others
if [ "${TRAVIS_OS_NAME}" != "windows" ] then;
	pip3 install -U pip wheel
fi

#install listed requirements
pip install -r "./app_resources/meta/manifests/pip_requirements.txt"
