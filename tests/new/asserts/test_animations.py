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

global VERBOSE
VERBOSE = True
# VERBOSE = False

global RESULTS
RESULTS = {
    "pf": [],
    "failures": []
}

class AnimationAudit(unittest.TestCase):
    def set_Up(self, *args):
        self.platID = len(args) > 1 and args[1] or "snes"
        self.gameID = len(args) > 2 and args[2] or "zelda3"
        self.spriteID = len(args) > 3 and args[3] or "link"

        libref = f"source.{self.platID}.{self.gameID}.{self.spriteID}.sprite"
        DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]["lib"] = importlib.import_module(libref)

        spriteData = DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]
        spriteLibrary = spriteData["lib"]

        with open(os.path.join(spriteData["paths"]["resource"]["app"],"manifests","animations.json")) as inFile:
            self.animations = json.load(inFile)
            if "$schema" in self.animations: #skip schema definition as it's not an animation
                del self.animations["$schema"]
        with open(os.path.join(spriteData["paths"]["resource"]["app"],"manifests","layout.json")) as inFile:
            self.layout = json.load(inFile)

    def test_animations(self):
        for [platID, plat] in DATA.items():
            for [gameID, game] in plat["games"].items():
                for [spriteID, sprite] in game["sprites"].items():
                    self.set_Up(self, platID, gameID, spriteID)
                    if VERBOSE:
                        heading = ("%s/%s/%s" % (self.platID, self.gameID, self.spriteID))
                        print(heading)
                        print("-" * 70)
                    self.run_animations_use_valid_image_names()
                    self.run_no_duplicate_image_definitions_in_layout()


    def run_animations_use_valid_image_names(self):
        #if this fails, it is because there is an animation in animations.json that references an image from layout.json that doesn't exist
        referenced_images = set()
        for animation in self.animations.values():
            for directed_animation in animation.values():
                for pose in directed_animation:  # directed_animation is a list, not a dict
                    for tile in pose["tiles"]:  # pose["tiles"] is a list, not a dict
                        if not tile["image"].startswith("optional_"):
                            referenced_images.add(tile["image"])
        supplied_images = set(self.layout["images"].keys())
        pseudo_images = "pseudoimages" in self.layout and set(self.layout["pseudoimages"]) or set()
        bad_image_references = referenced_images.difference(supplied_images.union(pseudo_images))
        self.assertTrue(0 == len(set(bad_image_references)))

    def run_no_duplicate_image_definitions_in_layout(self):
        #if this fails, it is because there are two images in the layout with the same name
        supplied_images = self.layout["images"].keys()
        self.assertTrue(len(set(supplied_images)) == len(supplied_images))

    #TODO: write this so that it properly handles images like cannons that aren't specifically in the main DMA block
    # def test_dma_sequence_includes_all_images_from_layout(self):
    # # if this fails, it is because there is a DMA sequence specified in the layout, but it doesn't include all of the images
    # supplied_images = self.samus_layout["images"].keys()
    # dma_sequence_images = self.samus_layout["dma_sequence"]
    # self.assertEqual(dma_sequence_images, supplied_images)

if __name__ == "__main__":
    if VERBOSE:
        print("ANIMATIONS")
        print('.' * 70)

    unittest.main()
