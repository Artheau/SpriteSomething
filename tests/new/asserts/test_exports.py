#pylint: disable=subprocess-run-check

'''
Run tests
'''
from shutil import copy

import importlib        # dynamic sprite imports
import unittest         # tests
import json             # parsing JSON objects
import os               # os pathing
import subprocess
import tempfile         # temp for objects
import sys

from tests.new.common import DATA  # get pathdata

global VERBOSE
VERBOSE = True
# VERBOSE = False

global RESULTS
RESULTS = {
    "pf": [],
    "failures": []
}

def get_module_version(module, mode):
    '''
    Get module version data
    '''
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
        settingsPath = os.path.join(
            ".",
            "resources",
            "user",
            "meta",
            "manifests",
            "settings.json"
        )
        if os.path.isfile(settingsPath):
            with open(settingsPath, "r", encoding="utf-8") as settingsFile:
                settings = json.load(settingsFile)
                args = settings["py"]
                PIPEXE = settings["pip"]
                PIP_FLOAT_VERSION = settings["versions"]["pip"]["version"][1]
        else:
            print("PipLine not found!")
            sys.exit(1)

    ret = ""
    ver = ""
    if mode == "latest":
        if float(PIP_FLOAT_VERSION) >= 21.2:
            ret = subprocess.run(
                [
                    *args,
                    "-m",
                    PIPEXE,
                    "index",
                    "versions",
                    module
                ],
                capture_output=True,
                text=True
            )
            lines = ret.stdout.strip().split("\n")
            lines = lines[2::]
            vers = (list(map(lambda x: x.split(' ')[-1], lines)))
            if len(vers) > 1:
                ver = vers[1]
        elif float(PIP_FLOAT_VERSION) >= 21.1:
            ret = subprocess.run(
                [
                    *args,
                    "-m",
                    PIPEXE,
                    "install",
                    f"{module}=="
                ],
                capture_output=True,
                text=True
            )
        elif float(PIP_FLOAT_VERSION) >= 20.3:
            ret = subprocess.run(
                [
                    *args,
                    "-m",
                    PIPEXE,
                    "install",
                    "--use-deprecated=legacy-resolver",
                    f"{module}=="
                ],
                capture_output=True,
                text=True
            )
        elif float(PIP_FLOAT_VERSION) >= 9.0:
            ret = subprocess.run(
                [
                    *args,
                    "-m",
                    PIPEXE,
                    "install",
                    f"{module}=="
                ],
                capture_output=True,
                text=True
            )
        elif float(PIP_FLOAT_VERSION) < 9.0:
            ret = subprocess.run(
                [
                    *args,
                    "-m",
                    PIPEXE,
                    "install",
                    f"{module}==blork"
                ],
                capture_output=True,
                text=True
            )

        # if ver == "" and ret.stderr.strip():
        #     ver = (ret.stderr.strip().split("\n")[0].split(",")[-1].replace(')', '')).strip()

    elif mode == "installed":
        summary = subprocess.run(
            [
                *args,
                "-m",
                PIPEXE,
                "show",
                f"{module}"
            ],
            capture_output=True,
            text=True
        )
        summary = summary.stdout.strip().split("\n")
        ver = summary[1].split(":")[1].strip()

    return ver


class ExportAudit(unittest.TestCase):
    '''
    Export Tests
    '''
    def set_Up(self, *args):
        '''
        Set Up the Test
        '''
        self.platID = args[1] if len(args) > 1 else "snes"
        self.gameID = args[2] if len(args) > 2 else "zelda3"
        self.spriteID = args[3] if len(args) > 3 else "link"

        libref = f"source.{self.platID}.{self.gameID}.{self.spriteID}.sprite"
        DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]["lib"] = importlib.import_module(libref)

    def same(self, file1, file2):
        '''
        Are these the same?
        '''
        return file1.read() == file2.read()

    def test_exports(self):
        '''
        Test the exports
        '''
        for [platID, plat] in DATA.items():
            for [gameID, game] in plat["games"].items():
                for [spriteID, _] in game["sprites"].items():
                    self.set_Up(self, platID, gameID, spriteID)
                    if VERBOSE:
                        heading = f"{self.platID}/{self.gameID}/{self.spriteID}"
                        print(heading)
                        print("-" * 70)
                    for filext in DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]["paths"]["resource"]["sheetexts"].keys():
                        self.run_export(filext)
                    if VERBOSE:
                        print("")

    def run_export(self, filext):
        '''
        Make an export
        '''
        spriteData = DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]
        spriteLibrary = spriteData["lib"]

        if filext in spriteData["paths"]["resource"]["sheetexts"]:
            importExt = filext
            exportExt = filext

            if importExt == "rdc":
                importExt = "png"
            if importExt in ["4bpp", "palette", "zhx"]:
                print(f"{importExt} not supported by Tests!")
                return
            if importExt not in ["png", "bmp"] and spriteData["view-only"]:
                print(f"{self.spriteID} is a WIP!")
                return

            sprite = {
                "import": {
                    importExt: spriteLibrary.Sprite(
                        spriteData["paths"]["resource"]["sheetexts"][importExt],
                        {
                            "name": self.spriteID.capitalize(),
                            "folder name": self.spriteID,
                            "input": spriteData["input"]
                        },
                        spriteData["paths"]["resource"]["subpath"],
                        self.spriteID
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
                    tempFile
                )
            elif filext == "png":
                sprite["export"][exportExt] = sprite["import"][importExt].save_as_PNG(
                    tempFile
                )
            elif filext == "rdc":
                sprite["export"][exportExt] = sprite["import"][importExt].save_as_RDC(
                    tempFile
                )

            # file = {
            #     "import": { importExt: None },
            #     "export": { exportExt: None }
            # }

            match = False

            with open(
                spriteData["paths"]["resource"]["sheetexts"][filext],
                "rb"
            ) as importFile:
                with open(tempFile, "rb") as exportFile:
                    # Run the files to the end?
                    imImg = importFile.seek(0, os.SEEK_END)
                    exImg = exportFile.seek(0, os.SEEK_END)
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
                verb = "do" + ("" if match else "n't")
                print(
                    f"{importExt.ljust(4)} -> {exportExt.ljust(5)}: " + \
                    f"{(filext.upper() + 's').ljust(5 + 1)}" + \
                    verb + \
                    " match",
                    ("" if match else ("\t" + tempFile))
                )

            if not match:
                if not os.path.exists(os.path.join(".", "failures")):
                    os.makedirs(os.path.join(".", "failures"))

                RESULTS["failures"].append(
                    {
                        "input": spriteData["paths"]["resource"]["sheetexts"][filext],
                        "output": tempFile
                    }
                )

                with open(
                    os.path.join(
                        ".",
                        "failures",
                        "errors.txt"
                    ),
                    "a",
                    encoding="utf-8"
                ) as errorFile:
                    err = f"{self.platID}/{self.gameID}/{self.spriteID}/{importExt}-{exportExt}" + "\n"
                    errorFile.write(err)
                    errorFile.write(json.dumps(RESULTS) + "\n")

                destFile = os.path.join(
                    ".",
                    "failures",
                    os.path.basename(tempFile)
                )
                copy(
                    tempFile,
                    destFile
                )

                if exception:
                    sys.exit(1)

            RESULTS["pf"].append('.' if match else "F")


if __name__ == "__main__":
    module = "pillow"
    print(
        f"{module}\t" +\
        f"{get_module_version(module, 'installed')}\t" + \
        f"{get_module_version(module, 'latest')}"
    )
    if VERBOSE:
        print("EXPORTS")
        print('.' * 70)

    unittest.main(warnings="ignore")
