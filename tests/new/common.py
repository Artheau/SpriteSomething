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
                        for spriteID in os.listdir(GAMEPATH):
                            # ignore meta, __pycache__
                            if spriteID not in ["meta", "varia", "__pycache__"]:
                                SPRITEPATH = os.path.join(GAMEPATH, spriteID)
                                if os.path.isdir(SPRITEPATH):
                                    SHEETSPATH = os.path.join(rsourceApp, spriteID, "sheets")
                                    DATA[platID]["games"][gameID]["sprites"][spriteID] = {
                                        "paths": {
                                            "source": SPRITEPATH,
                                            "resource": {
                                                "subpath": os.path.join(rsourceSub, spriteID),
                                                "app": os.path.join(rsourceApp, spriteID),
                                                "sheet": {
                                                    "root": SHEETSPATH
                                                },
                                                "sheetexts": {}
                                            }
                                        }
                                    }
                                    for sheet in os.listdir(SHEETSPATH):
                                        if f"{spriteID}." in sheet:
                                            DATA[platID]["games"][gameID]["sprites"][spriteID]["paths"]["resource"]["sheetexts"][os.path.splitext(sheet)[1][1::]] = os.path.join(SHEETSPATH, sheet)
                                    # print(f">  {spriteID}")

# print(json.dumps(DATA, indent=2))
