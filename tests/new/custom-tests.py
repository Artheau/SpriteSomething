from common import DATA  # get pathdata
from resources.ci.common import my_path
from resources.ci.common import common
import importlib  # dynamic sprite imports
import unittest  # tests
import json  # parsing JSON objects
import os  # os pathing
import platform
import subprocess
import sys
import tempfile  # temp for objects
import traceback


try:
    from PIL import ImageChops
except ModuleNotFoundError as e:
    print(e)
    try:
        from Pillow import ImageChops
    except ModuleNotFoundError as e:
        print(e)

env = common.prepare_env()  # get environment variables
WIDTH = 70  # width for labels


args = []
PIPEXE = ""
PYTHON_EXECUTABLE = os.path.splitext(sys.executable.split(os.path.sep).pop())[
    0]  # get command to run python
# get python version
PYTHON_VERSION = sys.version.split(" ")[0]
# get python major.minor version
PYTHON_MINOR_VERSION = '.'.join(PYTHON_VERSION.split(".")[:2])
PIP_VERSION = ""
PIP_FLOAT_VERSION = 0
VERBOSE = True
VERSIONS = {}


def get_module_version(module):
    # pip index versions [module]                             // >= 21.2
    # pip install [module]==                                  // >= 21.1
    # pip install --use-deprecated=legacy-resolver [module]== // >= 20.3
    # pip install [module]==                                  // >=  9.0
    # pip install [module]==blork                             // <   9.0
    global args
    global PIPEXE
    global PIP_FLOAT_VERSION
    ret = ""
    ver = ""

    if float(PIP_FLOAT_VERSION) >= 21.2:
        ret = subprocess.run([*args, "-m", PIPEXE, "index",
                             "versions", module], capture_output=True, text=True)
        lines = ret.stdout.strip().split("\n")
        lines = lines[2::]
        vers = (list(map(lambda x: x.split(' ')[-1], lines)))
        if len(vers) > 1:
            ver = vers[1]
    elif float(PIP_FLOAT_VERSION) >= 21.1:
        ret = subprocess.run(
            [*args, "-m", PIPEXE, "install", f"{module}=="], capture_output=True, text=True)
    elif float(PIP_FLOAT_VERSION) >= 20.3:
        ret = subprocess.run([*args, "-m", PIPEXE, "install", "--use-deprecated=legacy-resolver",
                             f"{module}=="], capture_output=True, text=True)
    elif float(PIP_FLOAT_VERSION) >= 9.0:
        ret = subprocess.run(
            [*args, "-m", PIPEXE, "install", f"{module}=="], capture_output=True, text=True)
    elif float(PIP_FLOAT_VERSION) < 9.0:
        ret = subprocess.run([*args, "-m", PIPEXE, "install",
                             f"{module}==blork"], capture_output=True, text=True)

    # if ver == "" and ret.stderr.strip():
    #     ver = (ret.stderr.strip().split("\n")[0].split(",")[-1].replace(')', '')).strip()

    return ver


def do_python():
    # get python debug info
    ret = subprocess.run([*args, "--version"], capture_output=True, text=True)
    if ret.stdout.strip():
        PYTHON_VERSION = ret.stdout.strip().split(" ")[1]
        PY_STRING = (
            "%s\t%s\t%s"
            %
            (
                ((isinstance(args[0], list) and " ".join(
                  args[0])) or args[0]).strip(),
                PYTHON_VERSION,
                sys.platform
            )
        )
        print(PY_STRING)
        print('.' * WIDTH)


def do_pip():
    global VERSIONS
    # get pip debug info
    ret = subprocess.run([*args, "-m", PIPEXE, "--version"],
                         capture_output=True, text=True)
    if ret.stdout.strip():
        if " from " in ret.stdout.strip():
            PIP_VERSION = ret.stdout.strip().split(" from ")[
                0].split(" ")[1]
            if PIP_VERSION:
                b, f, a = PIP_VERSION.partition('.')
                global PIP_FLOAT_VERSION
                PIP_FLOAT_VERSION = b+f+a.replace('.', '')
                PIP_LATEST = get_module_version("pip")

                VERSIONS["py"] = {"version": PYTHON_VERSION,
                                  "platform": sys.platform}
                VERSIONS["pip"] = {
                    "version": [
                        PIP_VERSION,
                        PIP_FLOAT_VERSION
                    ],
                    "latest": PIP_LATEST
                }

                PIP_STRING = (
                    "%s\t%s\t%s\t%s\t%s\t%s"
                    %
                    (
                        ((isinstance(args[0], list) and " ".join(
                            args[0])) or args[0]).strip(),
                        PYTHON_VERSION,
                        sys.platform,
                        PIP_EXECUTABLE,
                        PIP_VERSION,
                        PIP_LATEST
                    )
                )
                print(PIP_STRING)
                print('.' * WIDTH)


class ExportAudit(unittest.TestCase):
    def __init__(self, platID, gameID, spriteID):
        self.platID = platID or "snes"
        self.gameID = gameID or "zelda3"
        self.spriteID = spriteID or "link"

    def same(self, file1, file2):
        return file1.read() == file2.read()

    def test_exports(self):
        if VERBOSE:
            heading = ("%s/%s/%s" % (self.platID, self.gameID, self.spriteID))
            print(heading)
            print("-" * len(heading))
        for filext in DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]["paths"]["resource"]["sheetexts"].keys():
            self.test_export(filext)
        if VERBOSE:
            print("")

    def test_export(self, filext):
        spriteData = DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]
        spriteLibrary = spriteData["lib"]

        if filext in spriteData["paths"]["resource"]["sheetexts"]:
            importExt = filext
            exportExt = filext

            if importExt == "rdc":
                importExt = "png"

            sprite = {
                "import": {
                    importExt: spriteLibrary.Sprite(
                        spriteData["paths"]["resource"]["sheetexts"][importExt],
                        {"name": self.spriteID.capitalize()},
                        spriteData["paths"]["resource"]["subpath"]
                    )
                },
                "export": {}
            }
            sprite["import"][importExt].metadata = {
                "sprite.name": self.spriteID.capitalize(),
                "author.name": "Nintendo",
                "author.name-short": "Nintendo"
            }

            _, tempFile = tempfile.mkstemp(suffix='.' + exportExt)

            if filext == "zspr":
                sprite["export"][exportExt] = sprite["import"][importExt].save_as_ZSPR(
                    tempFile)
            elif filext == "png":
                sprite["export"][exportExt] = sprite["import"][importExt].save_as_PNG(
                    tempFile)
            elif filext == "rdc":
                sprite["export"][exportExt] = sprite["import"][importExt].save_as_RDC(
                    tempFile)

            file = {
                "import": {
                    importExt: open(
                        spriteData["paths"]["resource"]["sheetexts"][filext], "rb")
                },
                "export": {
                    exportExt: open(tempFile, "rb")
                }
            }
            match = self.same(
                file["import"][importExt],
                file["export"][exportExt]
            )

            if VERBOSE or not match:
                print("%s -> %s : %s do%s match%s" % (
                    importExt.ljust(4),
                    exportExt.ljust(4),
                    (filext.upper() + 's').ljust(4 + 1),
                    "" if match else "n't",
                    "" if match else ("\t" + tempFile)
                ))
                if not VERBOSE and not match:
                    exit(1)


if __name__ == "__main__":
    # figure out pip executable
    PIP_EXECUTABLE = "pip" if "windows" in env["OS_NAME"] else "pip3"
    PIP_EXECUTABLE = "pip" if "osx" in env["OS_NAME"] and "actions" in env["CI_SYSTEM"] else PIP_EXECUTABLE

    PIP_VERSION = ""  # holder for pip's version

    success = False
    # foreach py executable
    for PYEXE in ["py", "python3", "python"]:
        if success:
            continue

        args = []
        # if it's the py launcher, specify the version
        if PYEXE == "py":
            PYEXE = [PYEXE, "-" + PYTHON_MINOR_VERSION]
            # if it ain't windows, skip it
            if "windows" not in env["OS_NAME"]:
                continue

        # build executable command
        if isinstance(PYEXE, list):
            args = [*PYEXE]
        else:
            args = [PYEXE]

        try:
            do_python()  # print python debug data

            # foreach py executable
            for PIPEXE in ["pip3", "pip"]:
                do_pip()        # print pip debug data
                # upgrade pip
                ret = subprocess.run(
                    [*args, "-m", PIPEXE, "install", "--upgrade", "pip"], capture_output=True, text=True)
                # get output
                if ret.stdout.strip():
                    # if it's not already satisfied, update it
                    if "already satisfied" not in ret.stdout.strip():
                        print(ret.stdout.strip())
                        do_pip()
                        success = True
                else:
                    success = True

        # if something else went fucky, print it
        except Exception as e:
            traceback.print_exc()

    module = "pillow"
    print("%s\t%s" % (module, get_module_version("pillow")))
    print('.' * WIDTH)

    for [platID, plat] in DATA.items():
        for [gameID, game] in plat["games"].items():
            for [spriteID, sprite] in game["sprites"].items():
                libref = f"source.{platID}.{gameID}.{spriteID}.sprite"
                DATA[platID]["games"][gameID]["sprites"][spriteID]["lib"] = importlib.import_module(
                    libref)
                export = ExportAudit(platID, gameID, spriteID)
                export.test_exports()
