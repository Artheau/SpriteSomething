'''
Sprite
'''
from source.meta.classes.spritelib import SpriteParent

class Sprite(SpriteParent):
    '''
    Sprite
    '''
    def __init__(self, filename, manifest_dict, my_subpath):
        super().__init__(filename, manifest_dict, my_subpath)
        self.load_plugins()
