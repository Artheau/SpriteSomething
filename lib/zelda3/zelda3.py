import json
import os
from lib.game import Game
from lib.zspr import Zspr
from . import rom

class Zelda3(Game):
    def __init__(self, rom_filename, meta_filename):
        self.game_name = "The Legend of Zelda: A Link to the Past"
        self.game_nameShort = "Zelda3"
        self.game_nameAbbr =  "Z3"
        self.background_images = {}
        with open(os.path.join("resources",self.game_nameShort.lower(),"backgrounds","backgrounds.json")) as bgimg_file:
            bg_imgs = json.load(bgimg_file)
        for bg_img in bg_imgs:
            self.background_images[bg_img["filename"]] = bg_img["title"]
        for file in os.listdir(os.path.join("resources",self.game_nameShort.lower(),"backgrounds")):
            if not file.endswith(".json") and not file in self.background_images.keys():
                self.background_images[file] = file.capitalize().rpartition('.')[0]
        self.background_images = {v:k for k,v in self.background_images.items()}
        self.rom_data = None#rom.Zelda3RomHandler(rom_filename)
        self.meta_data = None
        self.sprites = {0x01: ("Link", "Z3Link")}   #as (display name, class name)

class Zelda3Sprite(Zspr):   #ALttP Sprites
    def __init__(self, *args):
        super().__init__(*args)    #do the stuff from the inherited class


class Z3Link(Zelda3Sprite):   #ALttP Player Character Sprites
    def __init__(self, *args):
        super().__init__(*args)    #do the stuff from the inherited class

        self._SPRITE_DATA_SIZE = 0x7000
        self._sprite_data = bytearray([0 for _ in range(self._SPRITE_DATA_SIZE)])
        self._PALETTE_DATA_SIZE = 124
        self._palette_data = bytearray([0 for _ in range(self._PALETTE_DATA_SIZE)])

        self._INDIVIDUAL_PALETTE_SIZE = 30
        self.palette_types = {                         #if called as a list, returns the possible mail colors
                                                       #but also contains the offsets into the palette if used as a dict
                                    "green": 0,
                                    "blue": 30,
                                    "red": 60,
                                    "bunny": 90,
        }

        self.variant_types = {                          #named this way to be consistent with other games
                                    "gloveless": None,
                                    "power_glove": 0,
                                    "titans_mitt": 2,
        }
        self.animations = {  #TODO
                                    "Walk": 0,
                                    "Breathe": 1,
        }

        self._GLOVE_PALETTE_INDEX = 13
        self._GLOVE_PALETTE_OFFSET = 120

    def get_timed_sprite_palette(self, mail_color, gloves):   #for use in rendering the sprite
        palette = self.get_sprite_palette(mail_color)
        palette[self._GLOVE_PALETTE_INDEX:self._GLOVE_PALETTE_INDEX+2] = self.get_gloves_color(gloves)
        return [(0,palette)]   #the zero here indicates that this is a static palette, which all (implemented) Zelda palettes are

    def get_sprite_palette(self, mail_color):
        mail_color = mail_color.lower()     #no funny business with capital letters
        palette = bytearray([0,0])           #start with transparency color
        if mail_color in self.palette_types:
            offset = self.palette_types[mail_color]
            palette.append(self._palette_data[offset:offset+self._INDIVIDUAL_PALETTE_SIZE])
        else:
            raise AssertionError(f"in Link ZSPR module, received call to get_sprite_palette() with mail color {mail_color}")

        return palette

    def set_sprite_palette(self, palette, mail_color):
        mail_color = mail_color.lower()     #no funny business with capital letters

        palette_length = len(palette)
        if palette_length == self._INDIVIDUAL_PALETTE_SIZE:
            pass
        elif palette_length == self._INDIVIDUAL_PALETTE_SIZE + 2:   #the transparency color was included
            palette = palette[1:]   #trim the transparency color
        else:
            raise AssertionError(f"in Link ZSPR module, received call to set_sprite_palette() with pallete of length {palette_length}")

        if mail_color in self.palette_types:
            offset = self.palette_types[mail_color]
            self._palette_data[offset:offset+self._INDIVIDUAL_PALETTE_SIZE] = palette
        else:
            raise AssertionError(f"in Link ZSPR module, received call to set_sprite_palette() with mail color {mail_color}")

    def get_gloves_color(self, gloves):
        if gloves == "gloveless":             #TODO: enumeration scheme
            pass
        elif gloves in self.variant_types:
            offset = self._GLOVE_PALETTE_OFFSET + self.variant_types[gloves]
            return self._palette_data[offset:offset+2]
        else:
            raise AssertionError(f"in Link ZSPR module, received call to get_gloves_color() with glove color {gloves}")

    def get_sprite_frame(self, animation_ID, frame, buttons):
        #Not raising an error so that we can test this functionality on the other libraries for now
        #print(f"Received call to activate animation number {hex(animation_ID)} for Link, but this is not implemented (yet).")
        return None, None

    def get_sprite_animation(self, animation_ID):
        raise NotImplementedError()
