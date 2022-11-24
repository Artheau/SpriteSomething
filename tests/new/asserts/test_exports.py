from tests.new.common import DATA  # get pathdata

from shutil import copy

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
RESULTS = {
    "pf": [],
    "failures": []
}

try:
    from PIL import ImageChops
except ModuleNotFoundError as e:
    print(e)
    try:
        from Pillow import ImageChops
    except ModuleNotFoundError as e:
        print(e)


def get_module_version(module, mode):
    if mode == None:
        mode = "latest"
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
    if mode == "latest":
        if float(PIP_FLOAT_VERSION) >= 21.2:
            ret = subprocess.run([*args, "-m", PIPEXE, "index", "versions", module], capture_output=True, text=True)
            lines = ret.stdout.strip().split("\n")
            lines = lines[2::]
            vers = (list(map(lambda x: x.split(' ')[-1], lines)))
            if len(vers) > 1:
                ver = vers[1]
        elif float(PIP_FLOAT_VERSION) >= 21.1:
            ret = subprocess.run(
                [*args, "-m", PIPEXE, "install", f"{module}=="], capture_output=True, text=True)
        elif float(PIP_FLOAT_VERSION) >= 20.3:
            ret = subprocess.run([*args, "-m", PIPEXE, "install", "--use-deprecated=legacy-resolver", f"{module}=="], capture_output=True, text=True)
        elif float(PIP_FLOAT_VERSION) >= 9.0:
            ret = subprocess.run(
                [*args, "-m", PIPEXE, "install", f"{module}=="], capture_output=True, text=True)
        elif float(PIP_FLOAT_VERSION) < 9.0:
            ret = subprocess.run([*args, "-m", PIPEXE, "install", f"{module}==blork"], capture_output=True, text=True)

        # if ver == "" and ret.stderr.strip():
        #     ver = (ret.stderr.strip().split("\n")[0].split(",")[-1].replace(')', '')).strip()

    elif mode == "installed":
        summary = subprocess.run([*args, "-m", PIPEXE, "show", f"{module}" ], capture_output=True, text=True)
        summary = summary.stdout.strip().split("\n")
        ver = summary[1].split(":")[1].strip()

    return ver


class ExportAudit(unittest.TestCase):
    def set_Up(self, *args):
        self.platID = len(args) > 1 and args[1] or "snes"
        self.gameID = len(args) > 2 and args[2] or "zelda3"
        self.spriteID = len(args) > 3 and args[3] or "link"

        libref = f"source.{self.platID}.{self.gameID}.{self.spriteID}.sprite"
        DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]["lib"] = importlib.import_module(libref)

        spriteData = DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]
        spriteLibrary = spriteData["lib"]

    def same(self, file1, file2):
        return file1.read() == file2.read()

    def test_exports(self):
        for [platID, plat] in DATA.items():
            for [gameID, game] in plat["games"].items():
                for [spriteID, sprite] in game["sprites"].items():
                    self.set_Up(self, platID, gameID, spriteID)
                    if VERBOSE:
                        heading = ("%s/%s/%s" % (self.platID, self.gameID, self.spriteID))
                        print(heading)
                        print("-" * 70)
                    for filext in DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]["paths"]["resource"]["sheetexts"].keys():
                        self.run_export(filext)
                    if VERBOSE:
                        print("")

    def run_export(self, filext):
        spriteData = DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]
        spriteLibrary = spriteData["lib"]

        if filext in spriteData["paths"]["resource"]["sheetexts"]:
            importExt = filext
            exportExt = filext

            if importExt == "rdc":
                importExt = "png"
            if importExt in ["4bpp", "palette", "zhx"]:
                return

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
                "import": { importExt: None },
                "export": { exportExt: None }
            }

            match = False

            with open(spriteData["paths"]["resource"]["sheetexts"][filext], "rb") as importFile:
                with open(tempFile, "rb") as exportFile:
                    match = self.same(
                        importFile,
                        exportFile
                    )

            exception = False
            try:
                self.assertTrue(match)
            except:
                exception = True

            if VERBOSE or exception:
                print("%s -> %s : %s do%s match%s" % (
                    importExt.ljust(4),
                    exportExt.ljust(4),
                    (filext.upper() + 's').ljust(4 + 1),
                    "" if match else "n't",
                    "" if match else ("\t" + tempFile)
                ))

            if not match:
                if not os.path.exists(os.path.join(".", "failures")):
                    os.makedirs(os.path.join(".", "failures"))

                with open(os.path.join(".","failures","errors.txt"), "a") as errorFile:
                  err = (
                    "%s/%s/%s/%s-%s"
                    %
                    (
                      self.platID,
                      self.gameID,
                      self.spriteID,
                      importExt,
                      exportExt
                    )
                    + "\n"
                  )
                  errorFile.write(err)

                RESULTS["failures"].append(
                    {
                        "input": spriteData["paths"]["resource"]["sheetexts"][filext],
                        "output": tempFile
                    }
                )

                destFile = os.path.join(".", "failures", os.path.basename(tempFile))
                copy(
                    tempFile,
                    destFile
                )

                if exception:
                    exit(1)

            RESULTS["pf"].append('.' if match else "F")


if __name__ == "__main__":
    module = "pillow"
    print(
        "%s\t%s\t%s"
        %
        (
            module,
            get_module_version(module, "installed"),
            get_module_version(module, "latest")
        )
    )
    if VERBOSE:
        print("EXPORTS")
        print('.' * 70)

    unittest.main()
