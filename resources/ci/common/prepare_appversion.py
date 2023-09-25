import common
import json
import os                 # for env vars
from json.decoder import JSONDecodeError
from shutil import copy   # file manipulation

def prepare_appversion():
  env = common.prepare_env()

  CI_SETTINGS = {}
  manifest_path = os.path.join(".","resources","app","meta","manifests","ci.json")
  if (not os.path.isfile(manifest_path)):
    raise AssertionError("Manifest not found: " + manifest_path)
  with(open(manifest_path)) as ci_settings_file:
    try:
        CI_SETTINGS = json.load(ci_settings_file)
    except JSONDecodeError as e:
        raise ValueError("CI Settings file malformed!")

  # set tag to app_version.txt
  with open(
      os.path.join(
          ".",
          *CI_SETTINGS["common"]["prepare_appversion"]["app_version"]
      ),
      "w+"
  ) as f:
      APP_VERSION = f.read()
      if env["GITHUB_TAG"].strip() != APP_VERSION.strip():
          f.seek(0)
          f.write(env["GITHUB_TAG"])
          f.truncate()
          print(f"Writing {env['GITHUB_TAG']} to AppVersion")

  if not os.path.isdir(os.path.join("..", "build")):
      os.mkdir(os.path.join("..", "build"))
  copy(
      os.path.join(".",*CI_SETTINGS["common"]["prepare_appversion"]["app_version"]),
      os.path.join("..", "build", "app_version.txt")
  )


def main():
  prepare_appversion()

if __name__ == "__main__":
  main()
else:
  raise AssertionError("Script improperly used as import!")
