import os
import subprocess

# get os name
TRAVIS_OS_NAME = os.getenv("TRAVIS_OS_NAME") or "TRAVIS_OS_NAME"

# get executables
#  python
#   linux/windows: python
#   macosx:        python3
#  pip
#   linux/macosx: pip3
#   windows:      pip
PYTHON_EXECUTABLE = "python3" if TRAVIS_OS_NAME == "osx" else "python"
PIP_EXECUTABLE = "pip" if TRAVIS_OS_NAME == "windows" else "pip3"

# upgrade pip
subprocess.check_call([PYTHON_EXECUTABLE,"-m","pip","install","--upgrade","pip"])

# pip version
subprocess.check_call([PIP_EXECUTABLE,"--version"])
# if pip3, install wheel
if PIP_EXECUTABLE == "pip3":
	subprocess.check_call([PIP_EXECUTABLE,"install","-U","wheel"])
# install listed dependencies
subprocess.check_call([PIP_EXECUTABLE,"install","-r","./resources/app/meta/manifests/pip_requirements.txt"])
