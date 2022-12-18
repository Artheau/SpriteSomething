# pylint: disable=invalid-name
# pylint: disable=no-self-use
"""CLI Unit Tests"""
import unittest         # tests
import os
from source.meta import cli

VERBOSE = True
# VERBOSE = False

class CLIAudit(unittest.TestCase):
    """CLI Unit Tests"""
    def set_Up(self, *args):
        """Set Up"""
        pass

    def test_cli(self):
        """Run Test"""
        print("Testing CLI")
        defaultargs = {
            "cli": "1",
            "lang": None,
            "mode": None,
            "export-filename": None,
            "dest-filename": None,
            "src-filename": None,
            "src-filepath": None,
            "sprite": os.path.join("resources","app","snes","zelda3","link","sheets","link.zspr")
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
