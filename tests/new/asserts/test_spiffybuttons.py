from tests.new.common import DATA

import importlib        # dynamic sprite imports
import unittest         # tests
import json             # parsing JSON objects
import os               # os pathing
import platform
import subprocess
import sys
import tempfile         # temp for objects
import traceback

from PIL import ImageChops

global VERBOSE
VERBOSE = True
# VERBOSE = False

global RESULTS
RESULTS = {
    "pf": [],
    "failures": []
}

class SpiffyButtonAudit(unittest.TestCase):
    def set_Up(self, *args):
        self.platID = len(args) > 1 and args[1] or "snes"
        self.gameID = len(args) > 2 and args[2] or "zelda3"
        self.spriteID = len(args) > 3 and args[3] or "link"

        libref = f"source.{self.platID}.{self.gameID}.{self.spriteID}.sprite"
        DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]["lib"] = importlib.import_module(libref)

        spriteData = DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]
        spriteLibrary = spriteData["lib"]

    def image_is_same(self, image1, image2):  #not a test; don't name this "test"
        diff = ImageChops.difference(image1, image2)
        image1_colors = {color:count for (count,color) in image1.getcolors()}
        image2_colors = {color:count for (count,color) in image2.getcolors()}
        #no bbox if they are the same
        return (diff.getbbox() is None) and (image1_colors == image2_colors) #AND they are drawing from the same palette (Pillow 7.0 made this line necessary)

    def test_spiffybuttons(self):
        for [platID, plat] in DATA.items():
            for [gameID, game] in plat["games"].items():
                for [spriteID, sprite] in game["sprites"].items():
                    self.set_Up(self, platID, gameID, spriteID)
                    if VERBOSE:
                        heading = ("%s/%s/%s" % (self.platID, self.gameID, self.spriteID))
                        print(heading)
                        print("-" * 70)
                    spiffy_manifest_path = os.path.join(
                        "resources",
                        "app",
                        platID,
                        gameID,
                        spriteID,
                        "manifests",
                        "spiffy-buttons.json"
                    )
                    found_spiffytests = False
                    if os.path.isfile(spiffy_manifest_path):
                        with open(spiffy_manifest_path) as spiffy_manifest:
                            spiffy_json = json.load(spiffy_manifest)
                            if "tests" in spiffy_json:
                                for [animation_name, animation_data] in list(spiffy_json["tests"].items()):
                                    found_spiffytests = True
                                    frame = animation_data["frame"] if "frame" in animation_data else 0
                                    palettes = animation_data["selections"] if "selections" in animation_data else []
                                    self.run_palette_audit(
                                        animation_name,
                                        frame,
                                        palettes
                                    )
                    if not found_spiffytests:
                        self.run_palette_audit()

    def run_palette_audit(self, animation_name="Stand", frame=0, PALETTES_TO_CHECK=[]):
        spriteData = DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]
        if spriteData["view-only"]:
            print(f"{self.spriteID} is a WIP!")
            print("")
            return
        spriteLibrary = spriteData["lib"]
        importExt = "png"
        if importExt not in spriteData["paths"]["resource"]["sheetexts"]:
            importExt = list(spriteData["paths"]["resource"]["sheetexts"].keys())[0]
        sprite = {
            "import": {
                importExt: spriteLibrary.Sprite(
                    spriteData["paths"]["resource"]["sheetexts"][importExt],
                    {"name": self.spriteID.capitalize(), "folder name": self.spriteID},
                    spriteData["paths"]["resource"]["subpath"],
                    self.spriteID
                )
            }
        }

        old_image = None
        for i,_ in enumerate(PALETTES_TO_CHECK):
            new_image = sprite["import"][importExt].get_image(animation_name, "right", frame, PALETTES_TO_CHECK[i], 0)[0]
            if old_image is not None:
                with self.subTest(new_palette = PALETTES_TO_CHECK[i], old_palette = PALETTES_TO_CHECK[i-1]):
                    self.assertFalse(self.image_is_same(old_image,new_image))
            old_image = new_image

if __name__ == "__main__":
    if VERBOSE:
        print("SPIFFY BUTTONS")
        print('.' * 70)

    unittest.main()
