#!/bin/bash

set -ev

if [ "${TRAVIS_OS_NAME}" != "windows" ]; then
	pip3 --version;
	pip3 install -U wheel;
fi

${PYTHON_EXECUTABLE} -m pip install -r "./app_resources/meta/manifests/pip_requirements.txt"
