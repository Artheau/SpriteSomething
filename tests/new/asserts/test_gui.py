from source.meta.gui import gui #need to import the GUI to test it
from tests.new.common import DATA

import importlib        # dynamic sprite imports
import unittest         # tests
import json             # parsing JSON objects
import os               # os pathing
import platform
import subprocess
import sys
import tempfile         # temp for objects
import tkinter as tk
import traceback

global VERBOSE
VERBOSE = True
# VERBOSE = False

global RESULTS
RESULTS = {
    "pf": [],
    "failures": []
}

class GUIAudit(unittest.TestCase):
    def set_Up(self, *args):
        self.platID = len(args) > 1 and args[1] or "snes"
        self.gameID = len(args) > 2 and args[2] or "zelda3"
        self.spriteID = len(args) > 3 and args[3] or "link"

        libref = f"source.{self.platID}.{self.gameID}.{self.spriteID}.sprite"
        DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]["lib"] = importlib.import_module(libref)

        spriteData = DATA[self.platID]["games"][self.gameID]["sprites"][self.spriteID]
        spriteLibrary = spriteData["lib"]

        sheet = {}
        sheetexts = DATA[self.platID] \
            ["games"] \
            [self.gameID] \
            ["sprites"] \
            [self.spriteID] \
            ["paths"] \
            ["resource"] \
            ["sheetexts"]
        for ext in ["png","bmp"]:
            if ext in sheetexts:
                sheet = sheetexts[ext]

        pseudo_command_line_args = {
            "sprite": sheet
        }

        #make the GUI in skeleton form (no looping)
        print("Emulated DISPLAY: %s" % os.getenv("DISPLAY","None"))
        pseudo_root = tk.Tk()
        pseudo_root.withdraw()
        self.GUI_skeleton = gui.SpriteSomethingMainFrame(pseudo_root, pseudo_command_line_args)

    def test_gui(self):
        # for [platID, plat] in DATA.items():
        #     for [gameID, game] in plat["games"].items():
        #         for [spriteID, sprite] in game["sprites"].items():
        #             if VERBOSE:
        #                 heading = f"{platID}/{gameID}/{spriteID}"
        #                 print(heading)
        #                 print("-" * 70)
        # self.set_Up(self, platID, gameID, spriteID)
        self.set_Up(self)
        self.minitest_photoimage_does_not_accept_png_files()
        self.minitest_zoom_function_does_not_crash_app()
        self.minitest_destroy_gui()

    def minitest_photoimage_does_not_accept_png_files(self):
        #make sure the photoimage wrapper is not bypassed #TODO: move to its own test
        try:
            temp = tk.PhotoImage(file=os.path.join("resources","app","meta","icons","blank.png"))   #any PNG file can be used here
            self.assertFalse("The wrapper in gui_common.py to prevent PNG files from going to PhotoImage has been disabled, maybe by a tk import?")
        except AssertionError:
            try:
                temp = tk.PhotoImage(file=os.path.join("resources","app","meta","icons","app.gif"))   #any GIF file can be used here
                self.assertTrue(True)
            except AssertionError:
                self.assertFalse("tk.PhotoImage is not accepting GIF files.  Has it been rerouted?")

    def minitest_zoom_function_does_not_crash_app(self):
        #TODO: tie this test to the button press hooks directly
        self.GUI_skeleton.current_zoom = 1.7
        self.GUI_skeleton.game.update_background_image()
        self.GUI_skeleton.update_sprite_animation()

    def minitest_destroy_gui(self):
        self.GUI_skeleton.save_working_dirs()
        self.GUI_skeleton.save_ani_settings()

if __name__ == "__main__":
    if VERBOSE:
        print("GUI")
        print('.' * 70)

    unittest.main()
