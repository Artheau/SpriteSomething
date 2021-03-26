import common
import json
import os                 # for env vars
from shutil import copy   # file manipulation

env = common.prepare_env()

CI_SETTINGS = {}
with(open(os.path.join(".","resources","app","meta","manifests","ci.json"))) as ci_settings_file:
  CI_SETTINGS = json.load(ci_settings_file)

# set tag to app_version.txt
if not env["GITHUB_TAG"] == "":
    with open(os.path.join(".",*CI_SETTINGS["common"]["prepare_appversion"]["app_version"]), "w+") as f:
        _ = f.read()
        f.seek(0)
        f.write(env["GITHUB_TAG"])
        f.truncate()

if not os.path.isdir(os.path.join("..", "build")):
    os.mkdir(os.path.join("..", "build"))
copy(
    os.path.join(".",*CI_SETTINGS["common"]["prepare_appversion"]["app_version"]),
    os.path.join("..", "build", "app_version.txt")
)
