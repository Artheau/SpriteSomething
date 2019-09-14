import subprocess

subprocess.check_call("pip --version")
subprocess.check_call("pip install -r ./app_resources/meta/manifests/pip_requirements.txt")
