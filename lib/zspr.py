class Zspr():     #Base for ZSPR files
    def __init__(self):
        self._sprite_data = bytearray()       #raw sprite imagery bytes
        self._palette_data = bytearray()          #raw palette bytes
        self._sprite_name = ""                #name of sprite
        self._sprite_author_name = ""         #name of author
        self._sprite_author_name_short = ""   #short name of author (sanitized for rom injection, possibly for use in credits)

    def get_raw_sprite_data(self):            #Get raw sprite imagery bytes
        return self._sprite_data

    def set_raw_sprite_data(data):            #Set raw sprite imagery bytes
        self._sprite_data = data

    def get_raw_palette_data():               #Get raw palette bytes
        return self._palette_data

    def set_raw_palette_data(data):           #Set raw palette bytes
        self._palette_data = data

    def get_sprite_name():                 #Get name of sprite
        return self._sprite_name

    def set_sprite_name(name):            #Set name of sprite
        self._sprite_name = name

    def get_author_name():                #Get name of Author
        return self._sprite_author_name

    def set_author_name(name):            #Set name of Author
        self._sprite_author_name = name

    def get_author_name_short():           #Get short name of Author
        return self._sprite_author_name_short

    def set_author_name_short(name):       #Set short name of Author (sanitized for rom injection, possibly for use in credits)
        ALLOWED_CHARACTERS = ''.join(string.ascii_letters,string.digits,' ')  #for now, allow letters, numbers, and spaces
        sanitized_name = ''.join([x for x in name if x in ALLOWED_CHARACTERS])
        self._sprite_author_name_short = sanitized_name

    def get_background_image(background_name):
        if background_name in self.background_images:
            return Image.open(self.background_images[background_name])
        else:
            raise AssertionError(f"received call to get_background_image but could not find image for {background_name}")

    def get_sprite_frame(animation_ID, frame):      #a static pose that is held for exactly one frame
        raise AssertionError("function get_sprite_frame() called on root ZSPR class directly")

    def get_sprite_animation(animation_ID):   #get set of sprite frames that comprise a full animation sequence
        raise AssertionError("function get_sprite_animation() called on root ZSPR class directly")

    
          
class Zelda3(Zspr):   #ALttP Sprites
    def __init__(self):
        super().__init__()    #do the stuff from the inherited class
        self.background_images = {
                                    "On His Throne": "throne.png"
        }


class Link(Zelda3):   #ALttP Player Character Sprites
    def __init__(self):
        super().__init__()    #do the stuff from the inherited class

        self._SPRITE_DATA_SIZE = 0x7000
        self._sprite_data = bytearray([0 for _ in range(self._SPRITE_DATA_SIZE)])
        self._PALETTE_DATA_SIZE = 124
        self._palette_data = bytearray([0 for _ in range(self._PALETTE_DATA_SIZE)])

        self._INDIVIDUAL_PALETTE_SIZE = 30
        self.palette_types = {                         #if called as a list, returns the possible mail colors
                                                       #but also contains the offsets into the palette if used as a dict
                                    "green": 0
                                    "blue": 30
                                    "red": 60
                                    "bunny": 90
        }

        self.variant_types = {                          #named this way to be consistent with other games
                                    "gloveless": None
                                    "power_glove": 0
                                    "titans_mitt": 2
        }

        self._GLOVE_PALETTE_INDEX = 13
        self._GLOVE_PALETTE_OFFSET = 120

    def get_timed_sprite_palette(self, mail_color, gloves):   #for use in rendering the sprite
        palette = get_palette(mail_color)
        palette[self._GLOVE_PALETTE_INDEX:self._GLOVE_PALETTE_INDEX+2] = self.get_gloves_color(gloves)
        return [(0,palette)]   #the zero here indicates that this is a static palette, which all (implemented) Zelda palettes are

    def get_sprite_palette(self, mail_color):
        mail_color = lower(mail_color)     #no funny business with capital letters
        palette = bytearray([0,0])           #start with transparency color
        if mail_color in self.palette_types:
            offset = self.palette_types[mail_color]
            palette.append(self._palette_data[offset:offset+self._INDIVIDUAL_PALETTE_SIZE])
        else:
            raise AssertionError(f"in Link ZSPR module, received call to get_sprite_palette() with mail color {mail_color}")

        return palette

    def set_sprite_palette(self, palette, mail_color):
        mail_color = lower(mail_color)     #no funny business with capital letters

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
            palette[self._GLOVE_PALETTE_INDEX:self._GLOVE_PALETTE_INDEX+2] = self._palette_data[offset:offset+2]
        else:
            raise AssertionError(f"in Link ZSPR module, received call to get_gloves_color() with glove color {gloves}")

    def get_sprite_frame(animation_ID, frame):
        raise NotImplementedError()

    def get_sprite_animation(animation_ID):
        raise NotImplementedError()
        

class Metroid3(Zspr):   #Super Metroid Sprites
    def __init__(self):
        super().__init__()    #do the stuff from the inherited class
        self.background_images = {
                                    "Title Screen": "title.png"
        }



class Samus(Metroid3):    # SM Player Character Sprites
    def __init__(self):
        super().__init__()    #do the stuff from the inherited class

        #TODO: Finish this class
        raise NotImplementedError()

        self._SPRITE_DATA_SIZE = ???
        self._sprite_data = bytearray([0 for _ in range(self._SPRITE_DATA_SIZE)])
        self._PALETTE_DATA_SIZE = ???
        self._palette_data = bytearray([0 for _ in range(self._PALETTE_DATA_SIZE)])

        self.palette_types = {                         #if called as a list, returns the possible suit types
                                    "power": ???
                                    "varia": ???
                                    "gravity": ???
        }

        self.variant_type = {
                                    "standard": ???
                                    "loader": ???
                                    "heat": ???
                                    "charge": ???
                                    "speed_boost": ???
                                    "speed_squat": ???
                                    "shine_spark": ???
                                    "screw_attack": ???
                                    "hyper_beam": ???
                                    "death_suit": ???
                                    "death_flesh": ???
                                    "crystal_flash": ???
                                    "sepia": ???
                                    "sepia_hurt": ???
                                    "sepia_alternate": ???
                                    "door": ???
                                    "xray": ???
                                    "file_select": ???
                                    "ship": ???
                                    "intro_ship": ???
                                    "outro_ship": ???

        }

        
    def get_timed_sprite_palette(self, suit_type, variant):   #for use in rendering the sprite
        raise NotImplementedError()

    def get_sprite_palette(self, suit_type, variant):
        raise NotImplementedError()

    def set_sprite_palette(self, palette, suit_type):
        raise NotImplementedError()

    def get_sprite_frame(animation_ID, frame):
        raise NotImplementedError()

    def get_sprite_animation(animation_ID):
        raise NotImplementedError()
    

#TODO: Move this to its own file
'''
class Game {
  var RomHandler rom;	// Manages reading/writing rom
  var ZSPR{} sprites;	// { "Link": ZSPR.Zelda3.Link(), "Samus": ZSPR.Metroid3.Samus() }

  var string name;	// The Legend of Zelda: A Link to the Past; Super Metroid
  var string nameShort;	// Zelda3; Metroid3
  var string nameAbbr;	// Z3; M3
}
'''