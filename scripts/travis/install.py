import os
import subprocess

TRAVIS_OS_NAME = os.environ.get("TRAVIS_OS_NAME") or "TRAVIS_OS_NAME"
PIP_EXECUTABLE = "pip3"
if TRAVIS_OS_NAME == "windows":
	PIP_EXECUTABLE = "pip"

subprocess.check_call(PIP_EXECUTABLE + " --version")
subprocess.check_call(PIP_EXECUTABLE + " install -r ./app_resources/meta/manifests/pip_requirements.txt")
