from lib.game import Game
from lib.zspr import Zspr
from . import rom

class Metroid3(Game):
    def __init__(self, rom_filename, meta_filename):
        self.game_name = "Super Metroid"
        self.game_nameShort = "Metroid3"
        self.game_nameAbbr =  "M3"
        self.background_images = {
                                    "Title Screen": "title.png",
                                    "Space Colony": "colony.png"
        }
        self.rom_data = rom.Metroid3RomHandler(rom_filename)
        self.meta_data = None
        self.sprites = {"Samus": M3Samus(self.rom_data, self.meta_data)}


class Metroid3Sprite(Zspr):   #Super Metroid Sprites
    def __init__(self):
        super().__init__()    #do the stuff from the inherited class



class M3Samus(Metroid3Sprite):    # SM Player Character Sprites
    def __init__(self, rom_data, meta_data):
        super().__init__()    #do the stuff from the inherited class

        self._SPRITE_DATA_SIZE = 500000             #I honestly don't know what this number should be until I do more napkin math
        self._sprite_data = bytearray([0 for _ in range(self._SPRITE_DATA_SIZE)])
        self._PALETTE_DATA_SIZE = (135*16*2)+(17*2)     #so many palettes...that's 135 just right there, along with stray colors
        self._palette_data = bytearray([0 for _ in range(self._PALETTE_DATA_SIZE)])

        self.palette_types = {                         #if called as a list, returns the possible suit types
                                    "power": 0,
                                    "varia": 1,
                                    "gravity": 2,
        }

        self.variant_type = {
                                    "standard": 0,
                                    "loader": 1,
                                    "heat": 2,
                                    "charge": 3,
                                    "speed_boost": 4,
                                    "speed_squat": 5,
                                    "shine_spark": 6,
                                    "screw_attack": 7,
                                    "hyper_beam": 8,
                                    "death_suit": 9,
                                    "death_flesh": 10,
                                    "crystal_flash": 11,
                                    "sepia": 12,
                                    "sepia_hurt": 13,
                                    "sepia_alternate": 14,
                                    "door": 15,
                                    "xray": 16,
                                    "file_select": 17,
                                    "ship": 18,
                                    "intro_ship": 19,
                                    "outro_ship": 20,
        }


