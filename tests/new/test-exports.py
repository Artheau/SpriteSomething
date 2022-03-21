from common import DATA  # get pathdata
import importlib        # dynamic sprite imports
import unittest         # tests
import json             # parsing JSON objects
import os               # os pathing
import platform
import subprocess
import sys
import tempfile         # temp for objects
import traceback

global VERBOSE
VERBOSE = True
# VERBOSE = False

global RESULTS
RESULTS = []

try:
    from PIL import ImageChops
except ModuleNotFoundError as e:
    print(e)
    try:
        from Pillow import ImageChops
    except ModuleNotFoundError as e:
        print(e)


def get_module_version(module):
    # pip index versions [module]                             // >= 21.2
    # pip install [module]==                                  // >= 21.1
    # pip install --use-deprecated=legacy-resolver [module]== // >= 20.3
    # pip install [module]==                                  // >=  9.0
    # pip install [module]==blork                             // <   9.0
    args = ""
    PIPEXE = ""
    PIP_FLOAT_VERSION = ""

    if args == "" or \
            PIPEXE == "" or \
            PIP_FLOAT_VERSION == "":
        with open(os.path.join(".", "resources", "user", "meta", "manifests", "settings.json"), "r") as settingsFile:
            settings = json.load(settingsFile)
            args = settings["py"]
            PIPEXE = settings["pip"]
            PIP_FLOAT_VERSION = settings["versions"]["pip"]["version"][1]

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
            print("-" * 70)
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

            if VERBOSE:
                print("%s -> %s : %s do%s match%s" % (
                    importExt.ljust(4),
                    exportExt.ljust(4),
                    (filext.upper() + 's').ljust(4 + 1),
                    "" if match else "n't",
                    "" if match else ("\t" + tempFile)
                ))

            RESULTS.append('.' if match else "F")


if __name__ == "__main__":
    module = "pillow"
    print("%s\t%s" % (module, get_module_version("pillow")))
    if VERBOSE:
        print('.' * 70)

    for [platID, plat] in DATA.items():
        for [gameID, game] in plat["games"].items():
            for [spriteID, sprite] in game["sprites"].items():
                libref = f"source.{platID}.{gameID}.{spriteID}.sprite"
                DATA[platID]["games"][gameID]["sprites"][spriteID]["lib"] = importlib.import_module(libref)
                if VERBOSE:
                    print("EXPORTS")
                    print("=" * 70)
                export = ExportAudit(platID, gameID, spriteID)
                export.test_exports()

    if "F" in RESULTS:
        print(''.join(RESULTS))
        exit(1)
