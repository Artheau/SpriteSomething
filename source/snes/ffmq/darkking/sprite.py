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

    def import_cleanup(self):
        '''
        Post-import cleanup
        '''
        self.load_plugins()
        if hasattr(self, "images"):
            self.images = dict(self.images,**self.plugins.pseudoimages_test(False))
