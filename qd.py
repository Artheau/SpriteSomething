from PIL import Image

from string import ascii_uppercase

import json
import os

coords = {}
dims = {
  "src": {
    "x": 0,
    "y": 0,
    "w": 16,
    "h": 16
  },
  "dst": {
    "x": 2,
    "y": 2,
    "w": 16,
    "h": 16,
    "spacer": 2
  }
}
col = 0
ltrs = [ltr for ltr in ascii_uppercase]
for ltr in ["AA", "AB"]:
  ltrs.append(ltr)
for ltr in ltrs:
    for col in range(0,8):
        coords[f"{ltr}{col}"] = {
          "src": {
            "x": dims["src"]["x"],
            "y": dims["src"]["y"],
            "w": dims["src"]["w"],
            "h": dims["src"]["h"]
          },
          "dst": {
            "x": dims["dst"]["x"],
            "y": dims["dst"]["y"],
            "w": dims["dst"]["w"],
            "h": dims["dst"]["h"]
          }
        }
        dims["src"]["x"] += dims["src"]["w"]  # nudge SRC x right WIDTH
        dims["dst"]["x"] += dims["dst"]["w"] + dims["dst"]["spacer"]  # nudge DST x right WIDTH + SPACER
    dims["src"]["x"] = 0                                        # reset SRC x to 0
    dims["dst"]["x"] = dims["dst"]["spacer"]                    # reset DST x to SPACER
    dims["src"]["y"] += dims["src"]["h"]      # nudge SRC y down HEIGHT
    dims["dst"]["y"] += dims["dst"]["h"] + dims["dst"]["spacer"]  # nudge DST y down HEIGHT + SPACER
# print(json.dumps(coords, indent=2))

dims["src"]["x"] = \
dims["src"]["y"] = \
0
dims["dst"]["x"] = dims["dst"]["spacer"]

# print(json.dumps(dims,indent=2))

for ltr in ["F", "G", "R", "S", "S2", "T"]:
    cols = range(0, 3 if ltr[:1] in "RST" else 5)
    h = 16 if ltr in "FRT" else 8
    for col in cols:
        coord = coords[f"{ltr[:1]}{col}"]
        coords[f"compiled-{ltr}{col}"] = {
          "src": {
            "x": coord["src"]["x"],
            "y": coord["src"]["y"] + (8 if "2" in ltr else 0),
            "w": coord["src"]["w"],
            "h": h
          },
          "dst": {
            "x": dims["dst"]["x"],
            "y": dims["dst"]["y"],
            "w": dims["dst"]["w"],
            "h": h
          }
        }
        dims["dst"]["x"] += dims["dst"]["w"] + dims["dst"]["spacer"]  # nudge DST x right WIDTH + SPACER
    dims["dst"]["x"] = dims["dst"]["spacer"]                    # reset DST x to SPACER
    dims["dst"]["y"] += dims["dst"]["h"]  # nudge DST y down HEIGHT
    if ltr[:1] in "GS":
        dims["dst"]["y"] += 4
    if "2" in ltr:
        dims["dst"]["y"] -= (4 + 8)

appsheets = os.path.join(
    ".",
    "resources",
    "app",
    "snes",
    "zelda3",
    "link",
    "sheets"
)
usersheets = os.path.join(
    ".",
    "resources",
    "user",
    "snes",
    "zelda3",
    "link",
    "sheets"
)

with Image.open(os.path.join(appsheets, "link.png")) as img:
    exploded = Image.open(os.path.join(appsheets, "qd", "mask.png")).convert("RGBA")
    for [cell, cdata] in coords.items():
        # print((
        #   cdata["src"],
        #   cdata["dst"]
        # ))
        exploded.paste(
            img.crop(
                (
                    cdata["src"]["x"],
                    cdata["src"]["y"],
                    cdata["src"]["x"] + cdata["src"]["w"],
                    cdata["src"]["y"] + cdata["src"]["h"]
                )
            ),
            (cdata["dst"]["x"], cdata["dst"]["y"])
        )
    if not os.path.isdir(
        os.path.join(usersheets)
    ):
        os.makedirs(
            os.path.join(usersheets)
        )
    exploded.save(os.path.join(usersheets, "exploded.png"))
