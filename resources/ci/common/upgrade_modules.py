import os
import subprocess

pipline = ""
with open(os.path.join(".","resources","user","meta","manifests","pipline.txt"),"r") as piplineFile:
  pipline = piplineFile.read()

modules = []
with open(os.path.join(".","resources","app","meta","manifests","pip_requirements.txt"),"r") as requirementsFile:
  modules = requirementsFile.read().split("\n")

for module in modules:
    if module.strip() != "" and "=" not in module:
        print(f"Upgrading: {module.strip()}")
        ret = subprocess.run(
            "%s %s %s %s"
            %
            (
                pipline,
                "install",
                "--upgrade",
                f"{module.strip()}"
            ),
            capture_output=True,
            text=True
        )
