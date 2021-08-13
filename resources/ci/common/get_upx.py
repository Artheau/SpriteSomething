import common
import json
import os               # for env vars
import sys              # for path
import urllib.request   # for downloads
from shutil import unpack_archive

# only do stuff if we don't have a UPX folder

def get_upx():
  CI_SETTINGS = {}
  manifest_path = os.path.join("resources","app","meta","manifests","ci.json")
  if (not os.path.isfile(manifest_path)):
    raise AssertionError("Manifest not found: " + manifest_path)
  with(open(manifest_path)) as ci_settings_file:
    CI_SETTINGS = json.load(ci_settings_file)

  if not os.path.isdir("./upx"):
      # get env vars
      env = common.prepare_env()
      # set up download url
      UPX_VERSION = os.getenv("UPX_VERSION") or str(CI_SETTINGS["common"]["get_upx"]["version"])
      UPX_SLUG = ""
      UPX_FILE = ""
      if "windows" in env["OS_NAME"]:
          UPX_SLUG = "upx-" + UPX_VERSION + "-win64"
          UPX_FILE = UPX_SLUG + ".zip"
      else:
          UPX_SLUG = "upx-" + UPX_VERSION + "-amd64_linux"
          UPX_FILE = UPX_SLUG + ".tar.xz"
      UPX_URL = "https://github.com/upx/upx/releases/download/v" + \
          UPX_VERSION + '/' + UPX_FILE

      if "osx" not in env["OS_NAME"]:
          print(f"Getting UPX: {UPX_FILE}")
          with open("./" + UPX_FILE, "wb") as upx:
              UPX_REQ = urllib.request.Request(
                  UPX_URL,
                  data=None
              )
              UPX_REQ = urllib.request.urlopen(UPX_REQ)
              UPX_DATA = UPX_REQ.read()
              upx.write(UPX_DATA)

          unpack_archive(UPX_FILE, "./")

          os.rename("./" + UPX_SLUG, "./upx")
          os.remove("./" + UPX_FILE)

  print("UPX should " +
      ("not " if not os.path.isdir("./upx") else "") +
      "be available.")


def main():
  get_upx()

if __name__ == "__main__":
  main()
else:
  raise AssertionError("Script improperly used as import!")
