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
        self.sprites = {0x01: ("Samus", "M3Samus")}   #as (display name, class name)


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

        self.animations = {     #TODO: Organize this differently by separating out stance/facing/aim direction as different menus
                                    "Elevator (Power)": 0x00,
                                    "Elevator (Varia/Gravity)": 0x9B,

                                    "Stand right": 0x01,
                                    "Stand right, aim up": 0x03,
                                    "Stand right, aim diag up": 0x05,
                                    "Stand right, aim diag down": 0x07,
                                    "Stand, turning left": 0x25,
                                    "Stand, turn left, aim up": 0x8B,
                                    "Stand, turn left, aim diag up": 0x9C,
                                    "Stand, turn left, aim diag down": 0x8D,

                                    "Stand left": 0x02,
                                    "Stand left, aim up": 0x04,
                                    "Stand left, aim diag up": 0x06,
                                    "Stand left, aim diag down": 0x08,
                                    "Stand, turning right": 0x26,
                                    "Stand, turn right, aim up": 0x8C,
                                    "Stand, turn right, aim diag up": 0x9D,
                                    "Stand, turn right, aim diag down": 0x8E,

                                    "Run right": 0x09,
                                    "Run right, aim diag up": 0x0F,
                                    "Run right, aim forward": 0x0B,
                                    "Run right, aim diag down": 0x11,

                                    "Run left": 0x0A,
                                    "Run left, aim diag up": 0x10,
                                    "Run left, aim forward": 0x0C,
                                    "Run left, aim diag down": 0x12,

                                    "Jump begin, right": 0x4B,
                                    "Jump begin, right, aim up": 0x55,
                                    "Jump begin, right, aim diag up": 0x57,
                                    "Jump begin, right, aim diag down": 0x59,
                                    "Jump right": 0x4D,
                                    "Jumping forward, right": 0x51,
                                    "Jump right, aim up": 0x15,
                                    "Jump right, aim diag up": 0x69,
                                    "Jump right, aim forward": 0x13,
                                    "Jump right, aim diag down": 0x6B,
                                    "Jump right, aim down": 0x17,
                                    "Jump, turning left": 0x2F,
                                    "Jump, turn left, aim up": 0x8F,
                                    "Jump, turn left, aim diag up": 0x9E,
                                    "Jump, turn left, aim diag down": 0x91,
                                    "Standing from jump right": 0xA4,
                                    "Standing from jump right, aim up": 0xE0,
                                    "Standing from jump right, aim diag up": 0xE2,
                                    "Standing from jump right, aim forward": 0xE6,
                                    "Standing from jump right, aim diag down": 0xE4,
                                    
                                    "Jump begin, left": 0x4C,
                                    "Jump begin, left, aim up": 0x56,
                                    "Jump begin, left, aim diag up": 0x58,
                                    "Jump begin, left, aim diag down": 0x5A,
                                    "Jump left": 0x4E,
                                    "Jumping forward, left": 0x52,
                                    "Jump left, aim up": 0x16,
                                    "Jump left, aim diag up:": 0x6A,
                                    "Jump left, aim forward": 0x14,
                                    "Jump left, aim diag down": 0x6C,
                                    "Jump left, aim down": 0x18,
                                    "Jump, turning right": 0x30,
                                    "Jump, turn right, aim up": 0x90,
                                    "Jump, turn right, aim diag up": 0x9F,
                                    "Jump, turn right, aim diag down": 0x92,
                                    "Standing from jump left": 0xA5,
                                    "Standing from jump left, aim up": 0xE1,
                                    "Standing from jump left, aim diag up": 0xE3,
                                    "Standing from jump left, aim forward": 0xE7,
                                    "Standing from jump left, aim diag down": 0xE5,

                                    "Spin jump right": 0x19,
                                    "Space jump right": 0x1B,
                                    "Screw attack right": 0x81,
                                    "Walljump right": 0x83,
                                    "Standing from spin jump, right": 0xA6,

                                    "Spin jump left": 0x1A,
                                    "Space jump left": 0x1C,
                                    "Screw attack left": 0x82,
                                    "Walljump left": 0x84,
                                    "Standing from spin jump, left": 0xA7,

                                    "Morphing right": 0x37,
                                    "Morphball right": 0x1D,
                                    "Morphball roll right": 0x1E,
                                    "Morphball fall right": 0x31,
                                    "Unmorphing right": 0x3D,
                                    
                                    "Morphing left": 0x38,
                                    "Morphball left": 0x41,
                                    "Morphball roll left": 0x1F,
                                    "Morphball fall left": 0x32,
                                    "Unmorphing left": 0x3E,

                                    "Springball right": 0x79,
                                    "Springball roll right": 0x7B,
                                    "Springball fall right": 0x7D,
                                    "Springball jump right": 0x7F,

                                    "Springball left": 0x7A,
                                    "Springball roll left": 0x7C,
                                    "Springball fall left": 0x7E,
                                    "Springball jump left": 0x80,

                                    "Crouching from stand, right": 0x36,
                                    "Crouching from stand, right, aim diag up": 0x71,
                                    "Crouching from stand, right, aim diag down": 0x73,
                                    "Crouch right": 0x27,
                                    "Crouch right, aim up": 0x85,
                                    "Standing from crouch, right": 0x35,
                                    "Crouch, turning left": 0x43,

                                    "Crouching from stand, left": 0x35,
                                    "Crouching from stand, left, aim diag up": 0x72,
                                    "Crouching from stand, left, aim diag down": 0x74,
                                    "Crouch left": 0x28,
                                    "Crouch left, aim up": 0x86,
                                    "Standing from crouch, left": 0x36,
                                    "Crouch, turning right": 0x44,

                                    "Crouching from stand right, aim up": 0xF1,
                                    "Crouching from stand left, aim up": 0xF2,
                                    "Crouching from stand right, aim diag up": 0xF3,
                                    "Crouching from stand left, aim diag up": 0xF4,
                                    "Crouching from stand right, aim diag down": 0xF5,
                                    "Crouching from stand left, aim diag down": 0xF6,
                                    "Crouch, turn left, aim up": 0x97,
                                    "Crouch, turn right, aim up": 0x98,
                                    "Crouch, turn left, aim diag down": 0x99,
                                    "Crouch, turn right, aim diag down": 0x9A,
                                    "Crouch, turn left, aim diag up": 0xA2,
                                    "Crouch, turn left, aim diag up": 0xA3,
                                    "Standing from crouch right, aim up": 0xF7,
                                    "Standing from crouch left, aim up": 0xF8,
                                    "Standing from crouch right, aim diag up": 0xF9,
                                    "Standing from crouch left, aim diag up": 0xFA,
                                    "Standing from crouch right, aim diag down": 0xFB,
                                    "Standing from crouch left, aim diag down": 0xFC,

                                    "Fall right": 0x29,
                                    "Fall right, aim up": 0x2B,
                                    "Fall right, aim diag up": 0x6D,
                                    "Fall right, aim forward": 0x67,
                                    "Fall right, aim diag down": 0x6F,
                                    "Fall right, aim down": 0x2D,
                                    "Fall, turn left": 0x87,

                                    "Fall left": 0x2A,
                                    "Fall left, aim up": 0x2C,
                                    "Fall left, aim diag up": 0x6E,
                                    "Fall left, aim forward": 0x68,
                                    "Fall left, aim diag down": 0x70,
                                    "Fall left, aim down": 0x2E,
                                    "Fall, turn right": 0x88,

                                    "Fall, turn left, aim up": 0x93,
                                    "Fall, turn right, aim up": 0x94,
                                    "Fall, turn left, aim down": 0x95,
                                    "Fall, turn right, aim down": 0x96,
                                    "Fall, turn left, aim diag up": 0xA0,
                                    "Fall, turn right, aim diag up": 0xA1,

                                    "Moonwalk away from right": 0x49,
                                    "Moonwalk away from right, aim diag up": 0x76,
                                    "Moonwalk away from right, aim diag down": 0x78,
                                    "Moonjump, turn left": 0xBF,
                                    "Moonjump, turn left, aim diag up": 0xC1,
                                    "Moonjump, turn left, aim diag down": 0xC3,

                                    "Moonwalk away from left": 0x4A,
                                    "Moonwalk away from left, aim diag up": 0x75,
                                    "Moonwalk away from left, aim diag down": 0x77,
                                    "Moonjump, turn right": 0xC0,
                                    "Moonjump, turn right, aim diag up": 0xC2,
                                    "Moonjump, turn right, aim diag down": 0xC4,

                                    "Bonk right": 0x53,
                                    "Bonk right, roll out": 0x50,

                                    "Bonk left": 0x54,
                                    "Bonk left, roll out": 0x4F,

                                    "Grapple clockwise": 0xB2,
                                    "Grapple counterclockwise": 0xB3,
                                    "Grappled to right wall": 0xB8,
                                    "Grappled to left wall": 0xB9,

                                    "Grabbed left": 0xBA,
                                    "Grabbed left, aim diag up": 0xBB,
                                    "Grabbed left, aim forward": 0xBC,
                                    "Grabbed left, aim diag down": 0xBD,
                                    "Grabbed left, struggling": 0xBE,

                                    "Grabbed right": 0xEC,
                                    "Grabbed right, aim diag up": 0xED,
                                    "Grabbed right, aim forward": 0xEE,
                                    "Grabbed right, aim diag down": 0xEF,
                                    "Grabbed right, struggling": 0xF0,
                                    
                                    "Superjump begin right": 0xC7,
                                    "Superjump begin left": 0xC8,
                                    "Superjump right": 0xC9,
                                    "Superjump left": 0xCA,
                                    "Superjump vertical right": 0xCB,
                                    "Superjump vertical left": 0xCC,

                                    "Crystal flash right": 0xD3,
                                    "Crystal flash end, right": 0xD7,
                                    "Crystal flash left": 0xD4,
                                    "Crystal flash end, left": 0xD8,

                                    "X-ray right": 0xD5,
                                    "X-ray crouch right": 0xD9,
                                    "X-ray left": 0xD6,
                                    "X-ray crouch left": 0xDA,

                                    "Drained right": 0xE8,
                                    "Supplication right": 0xEA,

                                    "Drained left": 0xE9,
                                    "Supplication left": 0xEB,            

                                    #these are not unique poses, and once WYSIWYG is implemented, these can be removed from the menu
                                    "DEBUG: Ran into right wall": 0x89,
                                    "DEBUG: Ran into right wall, aim diag up": 0xCF,
                                    "DEBUG: Ran into right wall, aim diag down": 0xD1,
                                    "DEBUG: Ran into left wall": 0x8A,
                                    "DEBUG: Ran into left wall, aim diag up": 0xD0,
                                    "DEBUG: Ran into left wall, aim diag down": 0xD2,
                                    "DEBUG: Superjump diagonal right": 0xCD,
                                    "DEBUG: Superjump diagonal left": 0xCE,
        }

    def get_timed_sprite_palette(self, suit_type):   #for use in rendering the sprite
        raise NotImplementedError()

    def get_sprite_palette(self, suit_type):     #for displaying the palette in the GUI, not for rendering
        raise NotImplementedError()

    def set_sprite_palette(self, variant_type, suit_type):
        raise NotImplementedError()

    def get_sprite_frame(animation_ID, frame):
        raise NotImplementedError()

    def get_sprite_animation(animation_ID):
        raise NotImplementedError()







