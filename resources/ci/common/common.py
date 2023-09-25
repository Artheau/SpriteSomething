# pylint: disable=invalid-name
"""common stuff for ci scripts"""

import json
import os   # for env vars
import stat  # file statistics
import sys  # default system info
from json.decoder import JSONDecodeError

CI_SETTINGS = {}
manifest_path = os.path.join(
    "resources",
    "app",
    "meta",
    "manifests",
    "ci.json"
)
if not os.path.isfile(manifest_path):
    raise AssertionError("Manifest not found: " + manifest_path)
with(open(manifest_path, encoding="utf-8")) as ci_settings_file:
    CI_SETTINGS = {}
    try:
        CI_SETTINGS = json.load(ci_settings_file)
    except JSONDecodeError as e:
        raise ValueError("CI Settings file malformed!")

UBUNTU_VERSIONS = CI_SETTINGS["common"]["common"]["ubuntu"]
DEFAULT_EVENT = "event"
DEFAULT_REPO_SLUG = '/'.join(CI_SETTINGS["common"]["common"]["repo"])
FILENAME_CHECKS = CI_SETTINGS["common"]["common"]["filenames"]
FILESIZE_CHECK = int(CI_SETTINGS["common"]["common"]["filesize"]) * 1024 * 1024


def strtr(strng, replace):
    """Implementation of php's strtr()"""
    buf, i = [], 0
    while i < len(strng):
        for s, r in replace.items():
            if strng[i:len(s)+i] == s:
                buf.append(r)
                i += len(s)
                break
        else:
            buf.append(strng[i])
            i += 1
    return ''.join(buf)


def convert_bytes(num):
    """Take number of bytes and convert to string with units measure"""
    for x in ["bytes", "KB", "MB", "GB", "TB", "PB", "YB"]:
        if num < 1024.0:
            return f"{num:3.1f} {x}"
            # return "%3.1f %s" % (num, x)
        num /= 1024.0
    return 0


def file_size(file_path):
    """Get filesize of file at path"""
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)
    return 0


def prepare_env():
    """Prepare environment variables"""
    global DEFAULT_EVENT
    global DEFAULT_REPO_SLUG
    env = {}

    # get app version
    APP_VERSION = ""
    APP_VERSION_FILE = os.path.join(
        ".", *CI_SETTINGS["common"]["prepare_appversion"]["app_version"])
    if os.path.isfile(APP_VERSION_FILE):
        with open(APP_VERSION_FILE, "r", encoding="utf-8") as f:
            APP_VERSION = f.readlines()[0].strip()

    # ci data
    env["CI_SYSTEM"] = os.getenv("CI_SYSTEM", "")
    # git data
    env["BRANCH"] = os.getenv("TRAVIS_BRANCH", "")
    env["GITHUB_ACTOR"] = os.getenv(
        "GITHUB_ACTOR",
        CI_SETTINGS["common"]["common"]["actor"]
    )
    env["GITHUB_SHA"] = os.getenv("GITHUB_SHA", "")
    env["GITHUB_RUN_NUMBER"] = os.getenv("GITHUB_RUN_NUMBER", "")
    env["GITHUB_SHA_SHORT"] = env["GITHUB_SHA"]
    # commit data
    env["COMMIT_ID"] = os.getenv("TRAVIS_COMMIT", os.getenv("GITHUB_SHA", ""))
    env["COMMIT_COMPARE"] = os.getenv("TRAVIS_COMMIT_RANGE", "")
    # event data
    env["EVENT_MESSAGE"] = os.getenv("TRAVIS_COMMIT_MESSAGE", "")
    env["EVENT_LOG"] = os.getenv("GITHUB_EVENT_PATH", "")
    env["EVENT_TYPE"] = os.getenv(
        "TRAVIS_EVENT_TYPE",
        os.getenv(
            "GITHUB_EVENT_NAME",
            DEFAULT_EVENT
        )
    )
    # repo data
    env["REPO_SLUG"] = os.getenv(
        "TRAVIS_REPO_SLUG",
        os.getenv(
            "GITHUB_REPOSITORY",
            DEFAULT_REPO_SLUG
        )
    )
    env["REPO_USERNAME"] = ""
    env["REPO_NAME"] = ""

    # repo slug
    if '/' in env["REPO_SLUG"]:
        tmp = env["REPO_SLUG"].split('/')
        env["REPO_USERNAME"] = tmp[0]
        env["REPO_NAME"] = tmp[1]

    if not env["GITHUB_SHA"] == "":
        env["GITHUB_SHA_SHORT"] = env["GITHUB_SHA"][:7]

    # ci data
    env["BUILD_NUMBER"] = env["GITHUB_RUN_NUMBER"]
    print("Build Number: " + env["BUILD_NUMBER"])

    GITHUB_TAG = os.getenv("TRAVIS_TAG", os.getenv("GITHUB_TAG", ""))
    OS_NAME = os.getenv(
        "TRAVIS_OS_NAME",
        os.getenv(
            "OS_NAME",
            sys.platform
        )
    ).replace("macOS", "osx")
    OS_DIST = os.getenv("TRAVIS_DIST", "notset")
    OS_VERSION = ""

    if "win32" in OS_NAME or \
        "cygwin" in OS_NAME or \
        "msys" in OS_NAME:
        OS_NAME = "windows"
    elif "darwin" in OS_NAME:
        OS_NAME = "osx"
    elif "linux2" in OS_NAME:
        OS_NAME = "linux"

    if '-' in OS_NAME:
        OS_VERSION = OS_NAME[OS_NAME.find('-')+1:]
        OS_NAME = OS_NAME[:OS_NAME.find('-')]
        if OS_NAME in ("linux", "ubuntu"):
            if OS_VERSION in UBUNTU_VERSIONS:
                OS_VERSION = UBUNTU_VERSIONS[OS_VERSION]
            OS_DIST = OS_VERSION

    if OS_VERSION == "" and OS_DIST != "" and OS_DIST != "notset":
        OS_VERSION = OS_DIST

    print("GITHUB_TAG: " + GITHUB_TAG)

    # if we haven't appended the build number, do it
    if env["BUILD_NUMBER"] not in GITHUB_TAG:
        GITHUB_TAG = APP_VERSION
        # if the app version didn't have the build number, add it
        # set to <app_version>.<build_number>
        if env["BUILD_NUMBER"] not in GITHUB_TAG:
            GITHUB_TAG += '.' + env["BUILD_NUMBER"]

    for [label, value] in {
        "APP_VERSION": APP_VERSION,
        "GITHUB_TAG": GITHUB_TAG,
        "OS_NAME": OS_NAME,
        "OS_DIST": OS_DIST,
        "OS_VERSION": OS_VERSION
    }.items():
        env[label] = value
        print(f"{label}: {value}")

    return env


def prepare_filename(BUILD_FILENAME):
    """Build filename based on metadata"""
    env = prepare_env()

    DEST_FILENAME = ""

    # build the filename
    if not BUILD_FILENAME == "":
        os.chmod(BUILD_FILENAME, 0o755)
        fileparts = os.path.splitext(BUILD_FILENAME)
        DEST_SLUG = fileparts[0]
        DEST_EXTENSION = fileparts[1]
        DEST_SLUG = DEST_SLUG + '-' + env["GITHUB_TAG"] + '-' + env["OS_NAME"]
        if not env["OS_DIST"] == "" and not env["OS_DIST"] == "notset":
            DEST_SLUG += '-' + env["OS_DIST"]
        DEST_FILENAME = DEST_SLUG + DEST_EXTENSION
    return DEST_FILENAME


def find_binary(listdir):
    """Find a binary file if it's executable
         failing that, assume it's over 6MB"""
    global FILENAME_CHECKS
    global FILESIZE_CHECK

    BUILD_FILENAMES = []
    executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    for filename in os.listdir(listdir):
        filepath = os.path.join(listdir, filename)
        if os.path.isfile(filepath):
            if os.path.splitext(filename)[1] != ".py":
                st = os.stat(filepath)
                mode = st.st_mode
                big = st.st_size > FILESIZE_CHECK
                if (mode & executable) or big:
                    for check in FILENAME_CHECKS:
                        if check in filename:
                            BUILD_FILENAMES.append(filepath)
    return BUILD_FILENAMES


def main():
    """Entrypoint"""
    env = prepare_env()
    print(env)


if __name__ == "__main__":
    main()
