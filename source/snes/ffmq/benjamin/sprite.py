import importlib
import itertools
import json
from PIL import Image
from source.meta.classes.spritelib import SpriteParent
from source.meta.common import common

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.load_plugins()

        self.ben_globals = {}
        self.ben_globals["petrified_palette"] = [
            # (  0,  0,  0),
            ( 33, 33, 33),
            (206,206,206),
            (173,173,173),
            (132,132,132),
            (206,206,206),
            (173,173,173),
            (132,132,132)
        ]

    def import_cleanup(self):
        '''
        Post-import cleanup
        '''
        self.load_plugins()
        self.equipment = self.plugins.equipment_test(False)
        # self.equipment = self.plugins.equipment_test(True)
        if hasattr(self, "images"):
            self.images["transparent"] = Image.new("RGBA",(0,0),0)
            self.images = dict(self.images,**self.equipment)

    def get_palette(self, palettes, default_range=[], frame_number=0):
        palette_indices = None
        this_palette = []
        range_end = 8
        for i in range(1,range_end):
            this_palette.append((0,0,0))

        if "petrified_mail" in palettes:
            this_palette = self.ben_globals["petrified_palette"]
        else:
            palette_indices = list(range(1,range_end))     #start with normal mail and modify it as needed

        if palette_indices and \
            len(self.master_palette) >= len(palette_indices):
            for i,_ in enumerate(palette_indices):
                this_palette[i] = self.master_palette[palette_indices[i]]

        return this_palette
