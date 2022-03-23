import common
import json
import os               # for env vars
import platform
import subprocess
import ssl
import sys              # for path
import urllib.request   # for downloads
from shutil import unpack_archive

# only do stuff if we don't have a UPX folder


def get_upx():
    VERBOSE = True
    CI_SETTINGS = {}
    manifest_path = os.path.join(
        "resources", "app", "meta", "manifests", "ci.json")
    if (not os.path.isfile(manifest_path)):
        raise AssertionError("Manifest not found: " + manifest_path)
    with(open(manifest_path)) as ci_settings_file:
        CI_SETTINGS = json.load(ci_settings_file)

    if not os.path.isdir(os.path.join(".", "upx")):
        # get env vars
        env = common.prepare_env()
        # set up download url
        UPX_VERSION = os.getenv("UPX_VERSION") or str(
            CI_SETTINGS["common"]["get_upx"]["version"])
        UPX_SLUG = ""
        UPX_FILE = ""

        print(
          "%s\n" * 5
          %
          (
            platform.architecture(),
            sys.maxsize <= 2**32 and "x86" or "x64",
            platform.machine(),
            platform.platform(),
            platform.processor()
          )
        )

        if "windows" in env["OS_NAME"]:
            arch = sys.maxsize <= 2**32 and "32" or "64"
            UPX_SLUG = "upx-" + UPX_VERSION + f"-win{arch}"
            UPX_FILE = UPX_SLUG + ".zip"
        else:
            arch = platform.machine().lower()
            UPX_SLUG = "upx-" + UPX_VERSION + f"-{arch}_linux"
            UPX_FILE = UPX_SLUG + ".tar.xz"

        UPX_URL = "https://github.com/upx/upx/releases/download/v" + \
            UPX_VERSION + '/' + UPX_FILE

        if "osx" not in env["OS_NAME"]:
            print(f"Getting UPX: {UPX_FILE}")
            with open(os.path.join(".", UPX_FILE), "wb") as upx:
                print(f"Hitting URL: {UPX_URL}")
                try:
                    context = ssl._create_unverified_context()
                    UPX_REQ = urllib.request.urlopen(
                      UPX_URL,
                      context=context
                    )
                    UPX_DATA = UPX_REQ.read()
                    upx.write(UPX_DATA)
                except urllib.error.HTTPError as e:
                    print(f"UPX HTTP Code: {e.code}")

            if VERBOSE:
                print("")
                print("Unpacking UPX")
            unpack_archive(UPX_FILE, os.path.join("."))
            if VERBOSE:
                subprocess.run(
                    [
                        "ls",
                        "-d",
                        "upx*"
                    ]
                )
                print("")

            if VERBOSE:
                print("Moving UPX")
            os.rename(os.path.join(".", UPX_SLUG), os.path.join(".", "upx"))
            if VERBOSE:
                subprocess.run(
                    [
                        "ls",
                        "-d",
                        "upx*"
                    ]
                )
                print("")

            if VERBOSE:
                print("Deleting UPX Archive")
            os.remove(os.path.join(".", UPX_FILE))
            if VERBOSE:
                subprocess.run(
                    [
                        "ls",
                        "-d",
                        "upx*"
                    ]
                )
                print("")

    print(
        "UPX should " +
        ("not " if not os.path.isdir(os.path.join(".", "upx")) else "") +
        "be available."
    )


def main():
    get_upx()


if __name__ == "__main__":
    main()
else:
    raise AssertionError("Script improperly used as import!")
