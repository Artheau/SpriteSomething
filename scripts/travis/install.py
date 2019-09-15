import os
import subprocess

TRAVIS_OS_NAME = os.environ.get("TRAVIS_OS_NAME") or "TRAVIS_OS_NAME"
PYTHON_EXECUTABLE = "python3" if TRAVIS_OS_NAME == "osx" else "python"
PIP_EXECUTABLE = "pip" if TRAVIS_OS_NAME == "windows" else "pip3"

subprocess.check_call([PYTHON_EXECUTABLE,"-m","pip","install","--upgrade","pip"])

subprocess.check_call([PIP_EXECUTABLE,"--version"])
if PIP_EXECUTABLE == "pip3":
	subprocess.check_call([PIP_EXECUTABLE,"install","-U","wheel"])
subprocess.check_call([PIP_EXECUTABLE,"install","-r","./app_resources/meta/manifests/pip_requirements.txt"])
