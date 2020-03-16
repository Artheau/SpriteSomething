import common
import os         # for env vars
import subprocess # do stuff at the shell level

env = common.prepare_env()

# get executables
#  python
#   linux/windows: python
#   macosx:        python3
#  pip
#   linux/macosx: pip3
#   windows:      pip
PYTHON_EXECUTABLE = "python3" if "osx" in env["OS_NAME"] else "python"
PIP_EXECUTABLE = "pip" if "windows" in env["OS_NAME"] else "pip3"
PIP_EXECUTABLE = "pip" if "osx" in env["OS_NAME"] and "actions" in env["CI_SYSTEM"] else PIP_EXECUTABLE

# upgrade pip
subprocess.check_call([PYTHON_EXECUTABLE,"-m","pip","install","--upgrade","pip"])

# pip version
subprocess.check_call([PIP_EXECUTABLE,"--version"])
# if pip3, install wheel
if PIP_EXECUTABLE == "pip3":
	subprocess.check_call([PIP_EXECUTABLE,"install","-U","wheel"])
# install listed dependencies
subprocess.check_call([PIP_EXECUTABLE,"install","-r","./resources/app/meta/manifests/pip_requirements.txt"])
