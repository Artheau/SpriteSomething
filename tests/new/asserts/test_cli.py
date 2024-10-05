# pylint: disable=invalid-name
# pylint: disable=no-self-use
"""CLI Unit Tests"""
from tests.new.common import DATA

import unittest         # tests
import os
from source.meta import cli

VERBOSE = True
# VERBOSE = False

class CLIAudit(unittest.TestCase):
    """CLI Unit Tests"""
    def set_Up(self, *args):
        """Set Up"""
        self.platID = len(args) > 1 and args[1] or "snes"
        self.gameID = len(args) > 2 and args[2] or "zelda3"
        self.spriteID = len(args) > 3 and args[3] or "link"

    def test_cli(self):
        for [platID, plat] in DATA.items():
            for [gameID, game] in plat["games"].items():
                for [spriteID, spriteData] in game["sprites"].items():
                    if VERBOSE:
                        heading = f"{platID}/{gameID}/{spriteID}"
                        print(heading)
                        print("-" * 70)
                    self.set_Up(self, platID, gameID, spriteID)
                    self.cli_suite(spriteData)

    def cli_suite(self, spriteData):
        """Run Test"""
        if spriteData["view-only"] or spriteData["is-archive"]:
            print("CLI not supported!")
            print("")
            return
        print("Testing CLI")
        spritePath = os.path.join(
            "resources",
            "app",
            self.platID,
            self.gameID,
            self.spriteID,
            "sheets"
        )
        spriteFile = ""
        for ext in ["png","bmp"]:
            if os.path.isfile(os.path.join(spritePath, f"{self.spriteID}.{ext}")):
                spriteFile = os.path.join(spritePath, f"{self.spriteID}.{ext}")

        self.assertTrue(spriteFile != "")

        defaultargs = {
            "cli": "1",
            "mode": None,
            "export-filename": None,
            "dest-filename": None,
            "src-filename": None,
            "src-filepath": None,
            "sprite": spriteFile
        }
        # Diags
        args = defaultargs
        args["mode"] = "diags"
        print("DIAGS")
        mainframe = cli.CLIMainFrame(args)

        print("")
        print("*" * 50)

        # Export Link as PNG
        args = defaultargs
        args["mode"] = "export"
        print("EXPORT")
        mainframe = cli.CLIMainFrame(args)

        print("")
        print("*" * 50)

        # Inject into nothing: FAIL
        args = defaultargs
        args["mode"] = "inject"
        print("INJECT Nothing")
        mainframe = cli.CLIMainFrame(args)

        print("")
        print("*" * 50)

        # Inject BULK into nothing: FAIL
        args = defaultargs
        args["mode"] = "inject-bulk"
        print("INJECT Bulk Nothing")
        mainframe = cli.CLIMainFrame(args)

        print("")
        print("*" * 50)

        # Inject BULK RANDOM into nothing: FAIL
        args = defaultargs
        args["mode"] = "inject-bulk-random"
        print("INJECT Bulk Random Nothing")
        mainframe = cli.CLIMainFrame(args)

        print("")
        print("*" * 50)

        # Inject RANDOM into nothing: FAIL
        args = defaultargs
        args["mode"] = "inject-random"
        print("INJECT Random Nothing")
        mainframe = cli.CLIMainFrame(args)

        print("")
        print("*" * 50)

        # Download SpriteSomething Sprites
        # Needs to get from Sprite-specific plugins
        args = defaultargs
        args["mode"] = "get-spritesomething-sprites"
        # print("GET Sprites")
        # mainframe = cli.CLIMainFrame(args)

if __name__ == "__main__":
    if VERBOSE:
        print("CLI")
        print('.' * 70)

    unittest.main()
