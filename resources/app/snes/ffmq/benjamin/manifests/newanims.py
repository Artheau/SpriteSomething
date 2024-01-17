import json
import os

animPath = os.path.join(
    ".",
    "resources",
    "app",
    "snes",
    "ffmq",
    "benjamin",
    "manifests",
    "newanims.json"
)
with open(animPath, "r+", encoding="utf-8") as animFile:
    animJSON = json.load(animFile)
    for [dir, frames] in animJSON.items():
        for [fnum, frame] in enumerate(frames):
            if fnum >= (8 - 1):
                if "#name" in frame:
                    if "chain" in frame["#name"]:
                        for [tnum, tile] in enumerate(frame["tiles"]):
                            if "image" in tile:
                                if "claw0" in tile["image"]:
                                    tile["pos"][1] = (fnum - 0) * -4
                                    animJSON[dir][fnum]["tiles"][tnum] = tile
    animFile.seek(0)
    animFile.write(json.dumps(animJSON, indent=2))
