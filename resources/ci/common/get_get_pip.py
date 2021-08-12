import common
import argparse
import json
import os
import ssl
import subprocess # do stuff at the shell level
import urllib.request

env = common.prepare_env()

CI_SETTINGS = {}
manifest_path = os.path.join("resources","app","meta","manifests","ci.json")
if (not os.path.isfile(manifest_path)):
  raise AssertionError("Manifest not found: " + manifest_path)
with(open(manifest_path)) as ci_settings_file:
  CI_SETTINGS = json.load(ci_settings_file)

def get_get_pip(PY_VERSION):
  try:
    import pip
  except ImportError:
    print("Getting pip getter!")
    #make the request!
    url = "https://bootstrap.pypa.io/get-pip.py"
    context = ssl._create_unverified_context()
    req = urllib.request.urlopen(url, context=context)
    got_pip = req.read().decode("utf-8")

    with(open("get-pip.py", "w")) as g:
      req = urllib.request.Request(
        url,
        data = None,
        headers = {
          "User-Agent": CI_SETTINGS["common"]["get_get_pip"]["ua"]
        }
      )
      req = urllib.request.urlopen(req, context=context)
      data = req.read().decode("utf-8")
      g.write(data)

    # get executables
    #  python
    #   linux/windows: python
    #   macosx:        python3
    PYTHON_EXECUTABLE = "python3" if "osx" in env["OS_NAME"] else "python"
    if PY_VERSION is None:
      PY_VERSION = 0

    if float(PY_VERSION) > 0:
      PYTHON_EXECUTABLE = "py"

    print("Getting pip!")
    args = [
      env["PYTHON_EXE_PATH"] + PYTHON_EXECUTABLE,
      '-' + str(PY_VERSION),
      "get-pip.py"
    ]
    if PY_VERSION == 0:
      del args[1]
    subprocess.check_call(args)


def main():
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('--py', default=0)
  command_line_args = parser.parse_args()
  PY_VERSION = vars(command_line_args)["py"]

  try:
    import pip
    print("pip is installed")
  except ImportError:
    get_get_pip(PY_VERSION)

if __name__ == "__main__":
  main()
