import importlib
import itertools
import json
from PIL import Image
from source.meta.classes.spritelib import SpriteParent
from source.meta.common import common

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.link_globals = {
          "greyscale_mail": [
            (190,190,190),  # lt mail
            (255,255,255),  # skin
            (117,117,117),  # dk mail
          ]
        }

    def get_palette(self, palettes, default_range=[], frame_number=0):
        '''
        Get palette based on input strings and frame number
        '''
        palette_indices = None
        this_palette = []
        range_end = 4
        for i in range(1,range_end):
            this_palette.append((0,0,0))

        #start with power suit and modify as needed
        palette_indices = list(range(1,range_end))
        for i,_ in enumerate(palette_indices):
            if palette_indices[i] in range(0,range_end):
                if "blue_mail" in palettes:
                    #skip to second set
                    palette_indices[i] += 4
                if "red_mail" in palettes:
                    #skip to third set
                    palette_indices[i] += 8

        if palette_indices:
            for i,_ in enumerate(palette_indices):
                this_palette[i] = self.master_palette[palette_indices[i]]

        if "greyscale_mail" in palettes:
            this_palette = self.link_globals["greyscale_mail"]

        return this_palette
