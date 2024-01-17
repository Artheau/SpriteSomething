import json
import os
import sys
if not os.path.exists("source"):
    os.chdir("..")
    if not os.path.exists("source"):
        raise AssertionError("cannot find the root folder from the tests")

sys.path.append(os.getcwd())

DATA = {}

SOURCEPATH = os.path.join(".", "source")
# cycle through platforms
for platID in os.listdir(SOURCEPATH):
    PLATPATH = os.path.join(SOURCEPATH, platID)
    # only care if it's a dir
    if os.path.isdir(PLATPATH):
        # ignore meta, __pycache__
        if platID not in ["meta", "__pycache__"]:
            DATA[platID] = {
                "paths": {
                    "source": PLATPATH
                },
                "games": {}
            }
            # print(f"{platID}")
            # cycle through gameIDs
            for gameID in os.listdir(PLATPATH):
                GAMEPATH = os.path.join(PLATPATH, gameID)
                # only care if it's a dir
                if os.path.isdir(GAMEPATH):
                    # ignore meta, __pycache__
                    if gameID not in ["meta", "__pycache__"]:
                        rsourceSub = os.path.join(platID, gameID)
                        rsourceApp = os.path.join(".", "resources", "app", rsourceSub)
                        DATA[platID]["games"][gameID] = {
                            "paths": {
                                "source": GAMEPATH,
                                "resource": {
                                    "subpath": rsourceSub,
                                    "app": rsourceApp
                                }
                            },
                            "sprites": {}
                        }
                        # print(f"> {gameID}")
                        with open(os.path.join(rsourceApp, "manifests", "manifest.json"), "r", encoding="utf-8") as gameManifest:
                            spriteData = json.load(gameManifest)
                            for [spriteID, spriteManifest] in spriteData.items():
                                if spriteID not in ["$schema"]:
                                    spriteFolder = spriteManifest["folder name"]
                                    is_archive = bool("is-archive" in spriteManifest and spriteManifest["is-archive"])
                                    view_only = bool("view-only" in spriteManifest and spriteManifest["view-only"])
                                    SPRITEPATH = os.path.join(GAMEPATH, spriteFolder)
                                    if os.path.isdir(SPRITEPATH):
                                        SHEETSPATH = os.path.join(rsourceApp, spriteFolder, "sheets")
                                        DATA[platID]["games"][gameID]["sprites"][spriteFolder] = {
                                            "paths": {
                                                "source": SPRITEPATH,
                                                "resource": {
                                                    "subpath": os.path.join(rsourceSub, spriteFolder),
                                                    "app": os.path.join(rsourceApp, spriteFolder),
                                                    "sheet": {
                                                        "root": SHEETSPATH
                                                    },
                                                    "sheetexts": {}
                                                }
                                            },
                                            "input": spriteManifest["input"],
                                            "is-archive": is_archive,
                                            "view-only": view_only
                                        }
                                        for sheet in os.listdir(SHEETSPATH):
                                            if f"{spriteFolder}." in sheet:
                                                DATA[platID]["games"][gameID]["sprites"][spriteFolder]["paths"]["resource"]["sheetexts"][os.path.splitext(sheet)[1][1::]] = os.path.join(SHEETSPATH, sheet)
                                        # print(f">  {spriteFolder}")

# print(json.dumps(DATA, indent=2))
