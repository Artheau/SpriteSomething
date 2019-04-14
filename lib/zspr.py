#working off of MT's template
#this file contains classes that wrap all of the modifiable data for the sprites

class Zspr():     #Base for ZSPR files
    def __init__(self, rom_data, meta_data):
        self._sprite_data = bytearray()       #raw sprite imagery bytes
        self._palette_data = bytearray()      #raw palette bytes
        self._sprite_name = ""                #name of sprite
        self._sprite_author_name = ""         #name of author
        self._sprite_author_name_short = ""   #short name of author (sanitized for rom injection, possibly for use in credits)

        self.rom_data = rom_data                #remember how to access the rom handler
        self.meta_data = meta_data              #remember how to access the meta data

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

    def get_sprite_frame(animation_ID, frame):      #a static pose that is held for exactly one frame
        raise AssertionError("function get_sprite_frame() called on root ZSPR class directly")

    def get_sprite_animation(animation_ID):   #get set of sprite frames that comprise a full animation sequence
        raise AssertionError("function get_sprite_animation() called on root ZSPR class directly")

    
