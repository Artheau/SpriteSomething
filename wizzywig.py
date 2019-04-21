#This file will go away once it is fully tied into the GUI

import os
import json
from PIL import Image, ImageOps, ImageDraw
from lib.RomHandler import util
from lib.metroid3.metroid3 import M3Samus, Metroid3
from lib.layout import Layout

def main():
    if not os.path.isdir('images'):
        os.mkdir('images')
    def get_sfc_filename(path):
        for file in os.listdir(path):
            if file.endswith(".sfc") or file.endswith(".smc"):
                return os.path.join(path, file)
        else:
            raise AssertionError(f"There is no sfc file in directory {path}")

    game = Metroid3(get_sfc_filename(os.path.join("lib", "metroid3")),None)
    samus = M3Samus(game.rom_data, game.meta_data)

    full_layout = samus.export_PNG()
    full_layout.save("images/samus.png")

if __name__ == "__main__":
    main()