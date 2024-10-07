import itertools
import json                        #for reading JSON
import os                            #for filesystem manipulation
import io                            #for filesystem manipution
import re
from string import ascii_uppercase, digits
from PIL import Image
from source.meta.common import common
from source.meta.classes.spritelib import SpriteParent

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=None, verbose=True):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name, verbose)
        self.load_plugins()

        # Icons are sideview, so only left/right direction buttons should show
        self.overhead = False

        self.tfp_globals = {}
        self.tfp_globals["palettes"] = {
          "1": [
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (248, 200, 32),
            (248, 112, 48),
            (0, 0, 0),
            (248, 248, 248),
            (200, 88, 48),
            (176, 40, 40),
            (224, 112, 112),
            (40, 40, 40),
            (184, 184, 200),
            (120, 120, 136)
          ],
          "2": [
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (0, 0, 0),
            (248, 248, 248),
            (248, 128, 176),
            (80, 104, 168),
            (144, 168, 232),
            (40, 40, 40),
            (248, 176, 80),
            (184, 96, 40)
          ],
          "4": [
            (False, False, False),
            (248, 248, 248),
            (216, 96, 96),
            (176, 96, 40),
            (240, 160, 104),
            (40, 40, 40),
            (176, 144, 248),
            (80, 112, 200),
            (0, 0, 0),
            (248, 248, 248),
            (200, 48, 24),
            (72, 144, 48),
            (152, 208, 112),
            (40, 40, 40),
            (248, 208, 56),
            (184, 136, 32)
          ],
          "7": [
            (False, False, False),
            (248, 248, 248),
            (240, 216, 64),
            (184, 104, 32),
            (240, 160, 104),
            (40, 40, 40),
            (248, 120, 0),
            (192, 24, 32),
            (232, 96, 176),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False),
            (False, False, False)
          ]
        }

    def import_cleanup(self):
        '''
        Post-import cleanup
        '''
        self.load_plugins()
        self.equipment = self.plugins.equipment_test(False)
        if hasattr(self, "images"):
            self.images["transparent"] = Image.new("RGBA",(0,0),0)
            self.images = dict(self.images,**self.equipment)

    def import_from_ROM(self, rom):
        author_data = self.translate_author(rom)
        self.metadata["author.name"] = author_data
        self.metadata["author.name-short"] = author_data
        # pixel_data = rom.bulk_read_from_snes_address(0x108000,0x7000)        #the big Link sheet
        # palette_data = rom.bulk_read_from_snes_address(0x1BD308,120)         #the palettes
        # self.import_from_binary_data(pixel_data,palette_data)

    # def import_from_binary_data(self,pixel_data,palette_data):
    #     # get imagery
    #     # get palette bit
    #     pass

    def inject_into_ROM(self, spiffy_dict, rom):
        #should work for the combo rom, VT rando
        #should work for the (J) & (U) ROMs but won't automatically include the extra code needed to manage gloves, etc

        #this'll check VT rando Tournament Flag
        tournament_flag = (float(rom.get_size_in_MB()) > 1.5) and (rom.read(0x180213, 2) == 1)
        #this'll check combo Tournament Flag
        if rom.type() == "EXHIROM" and not tournament_flag:
            config = rom.read_from_snes_address(0x80FF52, 2)
            fieldvals = {}
            fieldvals["gamemode"] = [ "singleworld", "multiworld" ]
            fieldvals["z3logic"] = [ "normal", "hard" ]
            fieldvals["m3logic"] = [ "normal", "hard" ]
            field = {}
            field["race"] = ((config & (1 << 15)) >> 15) > 0 # 1 bit
            field["keysanity"] = ((config & (0b11 << 13)) >> 13) > 0 # 2 bits
            field["gamemode"] = ((config & (1 << 12)) >> 12) # 1 bit
            field["z3logic"] = ((config & (0b11 << 10)) >> 10) # 2 bits
            field["m3logic"] = ((config & (0b11 << 8)) >> 8) # 2 bits
            field["version"] = {}
            field["version"]["major"] = ((config & (0b1111 << 4)) >> 4) # 4 bits
            field["version"]["minor"] = ((config & (0b1111 << 0)) >> 0) # 4 bits

            field["gamemode"] = fieldvals["gamemode"][field["gamemode"]]
            field["z3logic"] = fieldvals["z3logic"][field["z3logic"]]
            field["m3logic"] = fieldvals["m3logic"][field["m3logic"]]

            tournament_flag = field["race"]

        if not tournament_flag or iddqd:
            linelen = 0
            if hex(rom.read_from_snes_address(0x238000, 2)) == "0x3702":
                print("CHECK ONE")
                if hex(rom.read_from_snes_address(0x23801E, 2)) == "0x3702":
                    print("CHECK TWO")
                    linelen = 28
                elif hex(rom.read_from_snes_address(0x238022, 2)) == "0x3702":
                    print("CHECK THREE")
                    linelen = 32
            if linelen > 0:
                # print("v32-compatible credits")
                # print(f"Length: {linelen}")
                [bigText, addrs, charClass] = self.get_alphabet(rom)

                msg = {"hi":{"ascii":"","rom":{"hex":[],"dec":[]}},"lo":{"ascii":"","rom":{"hex":[],"dec":[]}}}
                author = ""
                author_short = ""
                if "author.name" in self.metadata:
                    author = self.metadata["author.name"]
                if "author.name-short" in self.metadata:
                    author_short = self.metadata["author.name-short"]
                char_class = "a-zA-Z0-9\' " if charClass == "" else charClass
                pattern = r'^([' + char_class + ']+)$'
                antipattern = r'([^' + char_class + '])'
                if len(author) <= linelen:
                    matches = re.match(pattern,author)
                    if matches:
                        author = matches.groups(0)[0]
                    else:
                        author = re.sub(antipattern, "", author)
                if len(author_short) <= linelen:
                    matches = re.match(pattern,author_short)
                    if matches:
                        author_short = matches.groups(0)[0]
                    else:
                        author_short = re.sub(antipattern, "", author_short)
                if len(author_short) > len(author):
                    author = author_short
                author = author.upper()
                lpad = int((linelen - len(author)) / 2)
                author = author.rjust(lpad + len(author)).ljust(linelen)
                for i,ltr in enumerate(itertools.chain(author)):
                    msg["hi"]["ascii"] += ltr
                    msg["lo"]["ascii"] += ltr
                    msg["hi"]["rom"]["hex"].append(bigText[ltr][0])
                    msg["lo"]["rom"]["hex"].append(bigText[ltr][1])
                    msg["hi"]["rom"]["dec"].append(int(bigText[ltr][0],16))
                    msg["lo"]["rom"]["dec"].append(int(bigText[ltr][1],16))
                print(msg)

                # rom.bulk_write_to_snes_address(0x238002,msg["hi"]["rom"]["dec"],linelen)
                # rom.bulk_write_to_snes_address(0x238004+linelen,msg["lo"]["rom"]["dec"],linelen)

        else:
            # FIXME: English
            raise AssertionError(f"Cannot inject into a Race/Tournament ROM!")

        return rom
