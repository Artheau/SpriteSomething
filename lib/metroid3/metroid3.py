from lib.game import Game
from lib.zspr import Zspr

class Metroid3(Game):
    def __init__(self):
        self.game_name = "Super Metroid"
        self.game_nameShort = "Metroid3"
        self.game_nameAbbr =  "M3"
        self.background_images = {
                                    "Title Screen": "title.png"
        }
        self.rom_data = None#RomHandler()
        self.meta_data = None
        self.sprites = {"Samus": M3Samus(self.rom_data, self.meta_data)}


class Metroid3Sprite(Zspr):   #Super Metroid Sprites
    def __init__(self):
        super().__init__()    #do the stuff from the inherited class



class M3Samus(Metroid3Sprite):    # SM Player Character Sprites
    def __init__(self, rom_data, meta_data):
        super().__init__()    #do the stuff from the inherited class

        #TODO: Finish this class
        raise NotImplementedError()

        self._SPRITE_DATA_SIZE = 0#TODO
        self._sprite_data = bytearray([0 for _ in range(self._SPRITE_DATA_SIZE)])
        self._PALETTE_DATA_SIZE = 0#TODO
        self._palette_data = bytearray([0 for _ in range(self._PALETTE_DATA_SIZE)])

        self.palette_types = {                         #if called as a list, returns the possible suit types
                                    "power": 0,#TODO
                                    "varia": 0,#TODO
                                    "gravity": 0,#TODO
        }

        self.variant_type = {
                                    "standard": 0,#TODO
                                    "loader": 0,#TODO
                                    "heat": 0,#TODO
                                    "charge": 0,#TODO
                                    "speed_boost": 0,#TODO
                                    "speed_squat": 0,#TODO
                                    "shine_spark": 0,#TODO
                                    "screw_attack": 0,#TODO
                                    "hyper_beam": 0,#TODO
                                    "death_suit": 0,#TODO
                                    "death_flesh": 0,#TODO
                                    "crystal_flash": 0,#TODO
                                    "sepia": 0,#TODO
                                    "sepia_hurt": 0,#TODO
                                    "sepia_alternate": 0,#TODO
                                    "door": 0,#TODO
                                    "xray": 0,#TODO
                                    "file_select": 0,#TODO
                                    "ship": 0,#TODO
                                    "intro_ship": 0,#TODO
                                    "outro_ship": 0,#TODO
        }


