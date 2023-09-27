import common
import json
import os               # for env vars
import platform
import ssl
import sys              # for path
import urllib.request   # for downloads
from json.decoder import JSONDecodeError
from shutil import unpack_archive



def get_upx():
    VERBOSE = False
    CI_SETTINGS = {}
    manifest_path = os.path.join("resources", "app", "meta", "manifests", "ci.json")
    if (not os.path.isfile(manifest_path)):
        raise AssertionError("Manifest not found: " + manifest_path)
    with(open(manifest_path)) as ci_settings_file:
        try:
            CI_SETTINGS = json.load(ci_settings_file)
        except JSONDecodeError as e:
            raise ValueError("CI Settings file malformed!")

    env = common.prepare_env()

    UPX_DIR = os.path.join(".", "upx")
    if "osx" not in env["OS_NAME"]:
        if not os.path.isdir(UPX_DIR):
            # get env vars
            env = common.prepare_env()
            # set up download url
            UPX_VERSION = os.getenv("UPX_VERSION") or str(
                CI_SETTINGS["common"]["get_upx"]["version"])
            UPX_SLUG = ""
            UPX_FILE = ""

            # print(
            #   "%s\n" * 5
            #   %
            #   (
            #     platform.architecture(),
            #     sys.maxsize <= 2**32 and "x86" or "x64",
            #     platform.machine(),
            #     platform.platform(),
            #     platform.processor()
            #   )
            # )

            # LINUX
            # amd64:        AMD 64-bit
            # arm:          ARM 32-bit mobile
            # arm64:        ARM 64-bit mobile
            # armeb:        ARM big endian
            # i386:         32-bit
            # mips:         MIPS big endian
            # mipsel:       MIPS little endian
            # powerpc:      PowerPC
            # powerpc64le:  PowerPC little endian

            # WINDOWS
            # win32, win64

            if "windows" in env["OS_NAME"]:
                arch = sys.maxsize <= 2**32 and "32" or "64"
                UPX_SLUG = "upx-" + UPX_VERSION + f"-win{arch}"
                UPX_FILE = UPX_SLUG + ".zip"
            else:
                arch = "_64" not in platform.machine() and "i386" or "amd64"
                UPX_SLUG = "upx-" + UPX_VERSION + f"-{arch}_linux"
                UPX_FILE = UPX_SLUG + ".tar.xz"

            UPX_USER = "upx"
            UPX_REPO = "upx"
            UPX_TAG = f"v{UPX_VERSION}"
            UPX_URL = (
                f"https://github.com/{UPX_USER}/{UPX_REPO}/releases/download/" +
                f"{UPX_TAG}/{UPX_FILE}"
            )

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
                    print("")
                except urllib.error.HTTPError as e:
                    print(f"UPX HTTP Code: {e.code}")
                    return

            if VERBOSE:
                print("Unpacking UPX archive")
            unpack_archive(UPX_FILE, os.path.join("."))
            if VERBOSE:
                files = os.listdir(".")
                for f in files:
                    if "upx" in f:
                        print(f + ('/' if os.path.isdir(f) else ""))
                print("")

            if VERBOSE:
                print("Renaming UPX folder")
            os.rename(os.path.join(".", UPX_SLUG), UPX_DIR)
            if VERBOSE:
                files = os.listdir(".")
                for f in files:
                    if "upx" in f:
                        print(f + ('/' if os.path.isdir(f) else ""))
                print("")

            if VERBOSE:
                print("Deleting UPX archive & keeping folder")
            os.remove(os.path.join(".", UPX_FILE))
            if VERBOSE:
                files = os.listdir(".")
                for f in files:
                    if "upx" in f:
                        print(f + ('/' if os.path.isdir(f) else ""))
                print("")

    print(
        "UPX should %sbe available."
        %
        (
            "" if (
                os.path.isdir(UPX_DIR) and
                (len(os.listdir(UPX_DIR)) > 0)
            ) else "not "
        )
    )


def main():
    get_upx()


if __name__ == "__main__":
    main()
else:
    raise AssertionError("Script improperly used as import!")
