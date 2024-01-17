'''
Sprite
'''
from source.meta.classes.spritelib import SpriteParent

class Sprite(SpriteParent):
    '''
    Sprite
    '''
    def __init__(self, filename, manifest_dict, my_subpath, _):
        super().__init__(filename, manifest_dict, my_subpath, _)
        self.load_plugins()
        self.overhead = False
        self.palette_globals = {}
        self.palette_globals["one_area"] = [
            (255, 181,   0),
            (189, 115,   0),
            ( 99,  41,   0),
            (184, 200, 184), # changes
            (128, 128, 120), # changes
            ( 96,  88,  80), # changes
            ( 40,  40,  40), # changes
            (140, 239,  16),
            (222,  58, 148),
            (255, 255, 255),
            (  0,   0,   0),
            (255, 255, 255),
            ( 41,  58, 140),
            (255, 255, 255),
            (  0,   0,   0)
        ]
        self.palette_globals["two_area"] = [
            (255, 181,   0),
            (189, 115,   0),
            ( 99,  41,   0),
            (168, 200, 208), # changes
            (112, 128, 144), # changes
            ( 80,  88, 104), # changes
            ( 24,  40,  64), # changes
            (140, 239,  16),
            (222,  58, 148),
            (255, 255, 255),
            (  0,   0,   0),
            (255, 255, 255),
            ( 41,  58, 140),
            (255, 255, 255),
            (  0,   0,   0)
        ]
        self.palette_globals["three_area"] = [
            (255, 181,   0),
            (189, 115,   0),
            ( 99,  41,   0),
            (152, 152, 176), # changes
            (104, 104, 128), # changes
            ( 64,  64,  88), # changes
            ( 24,  24,  48), # changes
            (140, 239,  16),
            (222,  58, 148),
            (255, 255, 255),
            (  0,   0,   0),
            (255, 255, 255),
            ( 41,  58, 140),
            (255, 255, 255),
            (  0,   0,   0)
        ]
        self.palette_globals["four_area"] = [
            (255, 181,   0),
            (189, 115,   0),
            ( 99,  41,   0),
            (222, 173, 189), # changes
            (156, 107, 123), # changes
            (115,  74,  82), # changes
            ( 49,  33,  41), # changes
            (140, 239,  16),
            (222,  58, 148),
            (255, 255, 255),
            (  0,   0,   0),
            (255, 255, 255),
            ( 41,  58, 140),
            (255, 255, 255),
            (  0,   0,   0)
        ]
        self.palette_globals["five_area"] = [
            (255, 181,   0),
            (189, 115,   0),
            ( 99,  41,   0),
            (173, 123, 189), # changes
            (115,  66, 123), # changes
            ( 82,  41,  82), # changes
            ( 25,   8,  41), # changes
            (140, 239,  16),
            (222,  58, 148),
            (255, 255, 255),
            (  0,   0,   0),
            (255, 255, 255),
            ( 41,  58, 140),
            (255, 255, 255),
            (  0,   0,   0)
        ]
        self.palette_globals["green"] = [
            (140, 239,  16),
            ( 74, 173,  58),
            ( 41,  82,   0),
            (222, 173, 189), # changes
            (156, 107, 123), # changes
            (115,  74,  82), # changes
            ( 49,  33,  41), # changes
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (255, 255, 255),
            (255, 181,   0),
            (255,   0,   0),
            (  0,   0,   0)
        ]
        self.palette_globals["red"] = [
            (230, 173, 230),
            (222,  58, 148),
            (181,   0,  49),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (255, 255, 255),
            (  0,   0,   0)
        ]
        self.palette_globals["blue"] = [
            (148, 173, 230),
            ( 58, 115, 230),
            ( 25,  66, 156),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (255, 255, 255),
            (  0,   0,   0)
        ]

    def get_palette(self, palettes, default_range=[], frame_number=0):
        this_palette = []
        for i in range(1,16):
            this_palette.append((0,0,0))

        for palette_name in palettes:
            if palette_name in self.palette_globals:
                this_palette = self.palette_globals[palette_name]

        return this_palette
