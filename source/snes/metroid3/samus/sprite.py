import importlib
import itertools
import json
import os
from PIL import Image
from PIL import ImageOps
from source.meta.classes.spritelib import SpriteParent
from source.meta.common import common
from string import ascii_uppercase, digits
from . import rom_extract, rom_inject, rdc_export


class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.load_plugins()

        # Samus is sideview, so only left/right direction buttons should show
        self.overhead = False

        # TODO: Make file select and ship be animations in the big list, or tie to the ship background
        # self.plugins += [
        #     ("File Select Preview",None,None),
        #     ("Ship Preview",None,None)
        # ]

    def import_cleanup(self):
        self.load_plugins()
        self.images["transparent"] = Image.new("RGBA", (0, 0), 0)
        self.equipment = self.plugins.equipment_test(False)
        # print(self.equipment)
        self.images = dict(self.images,**self.equipment)

    def import_from_ROM(self, rom):
        # The history of the Samus import code is a story I will tell to my children
        self.images = rom_extract.rom_extract(self, rom)
        self.master_palette = list(self.images["palette_block"].getdata())

    def inject_into_ROM(self, spiffy_dict, rom):
        # The history of the Samus export code is a story I will tell to my grandchildren
        return rom_inject.rom_inject(self, spiffy_dict, rom)

    def get_stamp(self):
        dims = {
            "bg": {
                "width": 332,
                "height": 142
            },
            "cb": {
                "width": 0,
                "height": 0,
                "x": 148,
                "y": 110
            },
            "name": {
                "width": 8,
                "height": 12,
                "x": 0,
                "y": 0
            },
            "author": {
                "width": 7,
                "height": 7,
                "x": 0,
                "y": 0
            }
        }
        stamp = Image.open(common.get_resource([self.resource_subpath,"sheets","stamp"],"stamp.png")).convert("RGBA")
        rowIMG = {
            "name": Image.open(common.get_resource([self.resource_subpath,"sheets","stamp"],"uppercase.png")),
            "author": Image.open(common.get_resource([self.resource_subpath,"sheets","stamp"],"lowercase.png")),
        }
        charmap = {
            "name": [
                ascii_uppercase,
                ".,?!_#%()+-/;:<=>[] "
            ],
            "author": [
                ascii_uppercase,
                digits + " "
            ]
        }

        spritedata = {
            "name": self.metadata["sprite.name"] if "sprite.name" in self.metadata and self.metadata["sprite.name"] != "" else "Unknown Samus Sprite",
            "author": self.metadata["author.name"] if "author.name" in self.metadata and self.metadata["author.name"] != "" else "Unknown Author"
        }
        dims["fullName"] = {
            "width": len(spritedata["name"]) * (dims["name"]["width"])
        }
        dims["fullAuthor"] = {
            "width": len(spritedata["author"]) * (dims["author"]["width"] + 1)
        }
        ltrsIMG = Image.new(
            "RGBA",
            (
                max(
                    dims["fullName"]["width"],
                    dims["fullAuthor"]["width"]
                ),
                38
            ),
            (255,255,255,0)
        )

        if spritedata["name"] != "" and spritedata["author"] != "":
            createdby = Image.open(common.get_resource([self.resource_subpath,"sheets","stamp"],"createdby.png"))
            x = dims["cb"]["x"]
            y = dims["cb"]["y"]
            stamp.paste(createdby, (x,y), createdby)
            createdby.close()

        coords = {
            "dest": {
                "x": (int(ltrsIMG.size[0] / 2) - int(dims["fullName"]["width"] / 2)),
                "y": dims["name"]["y"]
            },
            "src": {
                "x": 0,
                "y": 0
            }
        }
        for row in ["name","author"]:
            for i,ltr in enumerate(spritedata[row][:(26+15)]):
                found = False
                ltr = ltr.upper()
                for ltrs in [row,"name","author"]:
                    for j,line in enumerate(charmap[ltrs]):
                        if not found and ltr in line:
                            found = True
                            # print(ltr,line.find(ltr),j)
                            coords["src"]["x"] = (line.find(ltr) * (dims[ltrs]["width"] + 1))
                            coords["src"]["y"] = j * dims[ltrs]["height"]
                            ltrIMG = rowIMG[ltrs].crop(
                                (
                                    coords["src"]["x"],
                                    coords["src"]["y"],
                                    coords["src"]["x"] + dims[ltrs]["width"],
                                    coords["src"]["y"] + dims[ltrs]["height"] + 1
                                )
                            )
                            (x,y) = (
                                coords["dest"]["x"],
                                coords["dest"]["y"]
                            )
                            if row == "name" and ltrs == "author":
                                y += 4
                            ltrIMG = Image.alpha_composite(Image.new("RGBA", ltrIMG.size, (255,255,255,0)), ltrIMG.convert("RGBA"))
                            ltrsIMG.paste(ltrIMG, (x,y))
                            ltrIMG.close()
                            coords["dest"]["x"] += dims[ltrs]["width"]
                            if ltrs == "author":
                                coords["dest"]["x"] += 1
            coords["dest"]["x"] = (int(ltrsIMG.size[0] / 2) - int(dims["fullAuthor"]["width"] / 2))
            coords["dest"]["y"] += dims[row]["height"] + 17

        find = [0,0,0]
        replace = (255,255,255)
        data = common.np.array(ltrsIMG)
        r,g,b,a = data.T
        black_areas = (r == find[0]) & (g == find[1]) & (b == find[2])
        data[..., :-1][black_areas.T] = replace
        ltrsIMG = Image.fromarray(data)
        # ltrsIMG.save(os.path.join(".","ltrs.png"))
        stamp.paste(ltrsIMG, (int(stamp.size[0] / 2) - int(ltrsIMG.size[0] / 2),91), ltrsIMG)
        rowIMG = {}
        return stamp

    def save_as_PNG(self, filename):
        master_image = self.get_master_PNG_image()
        stamp = self.get_stamp()
        master_image.paste(stamp, (0,0))
        master_image.save(filename, "PNG")
        return True

    def get_rdc_export_blocks(self):
        SAMUS_EXPORT_BLOCK_TYPE = 4
        return [(SAMUS_EXPORT_BLOCK_TYPE,rdc_export.get_raw_rdc_samus_block(self))]

    def get_colors_from_master(self, color_set):
        # for internal class use.    For general use, call get_timed_palette()
        color_set_switcher = {
            "power": [0,15],
            "base": [0,15],
            "varia": [15,30],
            "gravity": [30,45],
            "death": [45,60],
            "flash": [60,75],
            "fileselect": [75,90],
            "door": [3],
            "xray": [91,94],
            "ship": [101,104]
        }
        colors = None
        master_palette_indexes = color_set_switcher.get(
            color_set.lower()
            .replace(' ',"")
            .replace('-',"")
            .replace('_',"")
        )
        if master_palette_indexes:
            if len(master_palette_indexes) == 1:
                colors = self.master_palette[master_palette_indexes[0]]
            if len(master_palette_indexes) == 2:
                colors = self.master_palette[master_palette_indexes[0]:master_palette_indexes[1]]
            # print("FOUND INDEXES:",color_set,len(master_palette_indexes),colors)
        elif color_set == "gty":
            colors = [
                ( 64, 64,  0),
                (188,188,188),
                ( 40,  0, 40),
                (  0,248,112),
                ( 64,104, 64),
                (248,224,168),
                (144,176,144),
                (112,144,112),
                (216, 40,  0),
                ( 88,128,177),
                ( 36, 82, 82),
                (144,144,  0),
                ( 32, 64, 32),
                (160, 24,  0),
                (104,  0,  0)
            ]
        if colors:
            return colors
        # FIXME: English
        print(color_set, "X")
        raise AssertionError(f"Unrecognized color set request: {color_set}")

    def get_timed_palette(self, overall_type="power", variant_type="standard"):
        timed_palette = []
        base_palette = self.get_colors_from_master(overall_type)

        if overall_type.lower() == "ship" or variant_type.lower() == "ship":
            ship_color_body, ship_color_window, ship_glow_color = self.get_colors_from_master("ship")

            if variant_type.lower() == "outro" or variant_type.lower() == "intro":
                # 11 customizable colors
                ship_palette = []
                ship_palette.append(tuple(channel+72 for channel in ship_color_body))
                ship_palette.append(tuple(25/21*channel for channel in ship_color_body))
                ship_palette.append(tuple(10/21*channel for channel in ship_color_body))
                ship_palette.append(tuple( 0/21*channel for channel in ship_color_body))
                ship_palette.append(tuple(channel+5 for channel in ship_color_body))
                ship_palette.append(tuple(22/21*channel for channel in ship_color_body))
                ship_palette.append(tuple(18/21*channel for channel in ship_color_body))
                ship_palette.append(tuple(13/21*channel for channel in ship_color_body))
                ship_palette.append(ship_color_window)
                ship_palette.append(tuple(0.7*channel for channel in ship_color_window))
                ship_palette.append(tuple(0.4*channel for channel in ship_color_window))
                # and then 4 colors that are part of the underrigging which aren't coded to customize
                ship_palette.extend([(48,48,72),(16,16,40),(0,0,0),(0,0,0)])
                if variant_type.lower() == "intro":
                    timed_palette = [(0, ship_palette)]
                else:     #outro
                    timed_palette = [(0x18, common.palette_pull_towards_color(ship_palette,(0xFF,0xFF,0xFF),(float(15-i)/15.0))) for i in range(15)]
                    timed_palette.append((0, ship_palette))

            else:         #standard ship colors with underglow
                # 11 customizable colors
                ship_palette = []
                ship_palette.append(ship_color_body)
                ship_palette.append(tuple(16/21*channel for channel in ship_color_body))
                ship_palette.append(tuple( 3/21*channel for channel in ship_color_body))
                ship_palette.append(tuple( 1/21*channel for channel in ship_color_body))
                ship_palette.append(tuple(17/21*channel for channel in ship_color_body))
                ship_palette.append(tuple(13/21*channel for channel in ship_color_body))
                ship_palette.append(tuple( 9/21*channel for channel in ship_color_body))
                ship_palette.append(tuple( 4/21*channel for channel in ship_color_body))
                ship_palette.append(ship_color_window)
                ship_palette.append(tuple(0.7*channel for channel in ship_color_window))
                ship_palette.append(tuple(0.4*channel for channel in ship_color_window))
                # and then 3 colors that are part of the underrigging which aren't coded to customize
                ship_palette.extend([(48,48,72),(16,16,40),(0,0,0)])
                # then 1 more color for the underglow
                timed_palette = [(5, ship_palette + common.palette_pull_towards_color([ship_glow_color], (0,0,0), abs(float(7-i)/7.0))) for i in range(14)]

        elif variant_type.lower() == "standard":
            timed_palette = [(0, self.get_colors_from_master(overall_type))]

        elif variant_type.lower() == "loader":
            for _ in range(0x27):     #in the ROM, this is encoded as 0x24 + 0x03
                timed_palette.append((3,base_palette))
                timed_palette.append((3,common.palette_shift(base_palette,(0,80,120))))
            for _ in range(3):
                timed_palette.append((3,base_palette))
                timed_palette.append((3,common.palette_shift(base_palette,(0,40,120))))
            for _ in range(2):
                timed_palette.append((3,base_palette))
                timed_palette.append((3,common.palette_shift(base_palette,(0,0,80))))
            timed_palette.append((0,base_palette))

        elif variant_type.lower() == "heat":
            palette_shifts = [
                { "index": 16, "color": (0,0,0) },
                { "index": 4, "color": (8,0,0) },
                { "index": 4, "color": (8,0,0) },
                { "index": 5, "color": (16,0,0) },
                { "index": 6, "color": (16,0,0) },
                { "index": 7, "color": (24,0,0) },
                { "index": 8, "color": (24,0,0) },
                { "index": 8, "color": (40,0,0) },
                { "index": 8, "color": (40,0,0) },
                { "index": 8, "color": (24,0,0) },
                { "index": 7, "color": (24,0,0) },
                { "index": 6, "color": (16,0,0) },
                { "index": 5, "color": (16,0,0) },
                { "index": 4, "color": (8,0,0) },
                { "index": 4, "color": (8,0,0) },
                { "index": 3, "color": (8,0,0) }
            ]

            for shift in palette_shifts:
                timed_palette.append((shift["index"],common.palette_shift(base_palette,shift["color"])))

        elif variant_type.lower() == "charge":
            timed_palette = [(1, common.palette_pull_towards_color(base_palette,(0xFF,0xFF,0xFF),float(i)/8.0)) for i in range(8)]

        elif variant_type.lower().replace("_"," ") == "speed boost":

            palette_shifts = [
                { "index": 4, "color": (0,0,0) },
                { "index": 4, "color": (0,0,80) },
                { "index": 4, "color": (0,40,160) },
                { "index": 0, "color": (20,100,240) } #(0,120,160)
            ]

            for shift in palette_shifts:
                timed_palette.append((shift["index"],common.palette_shift(base_palette,shift["color"])))

        elif variant_type.lower().replace("_"," ") == "speed squat":
            # i = 0 1 2 3 2 1 0 2 3 2 1 0 1 2...
            timed_palette.extend([(1,common.palette_pull_towards_color(base_palette,(0xFF,0xFF,0xFF),float(i)/4.0)) for i in range(4)])
            timed_palette.extend([(1,common.palette_pull_towards_color(base_palette,(0xFF,0xFF,0xFF),float(i)/4.0)) for i in [2,1]])

        elif variant_type.lower().replace("_","").replace(" ","") == "shinespark":
            palette_shifts = [
                { "index": 1, "color": (0,0,0) },
                { "index": 1, "color": (64,64,32) },
                { "index": 1, "color": (104,104,0) },
                { "index": 1, "color": (176,176,64) }
            ]

            for shift in palette_shifts:
                timed_palette.append((shift["index"],common.palette_shift(base_palette,shift["color"])))

        elif variant_type.lower().replace("_"," ") == "screw attack":
            palette_shifts = [
                { "index": 1, "color": (0,0,0) },
                { "index": 1, "color": (0,64,0) },
                { "index": 1, "color": (0,128,0) },
                { "index": 1, "color": (0,192,40) },
                { "index": 1, "color": (0,128,0) },
                { "index": 1, "color": (0,64,0) }
            ]

            for shift in palette_shifts:
                timed_palette.append((shift["index"],common.palette_shift(base_palette,shift["color"])))

        elif variant_type.lower().replace("_"," ") == "hyper":
            palette_shifts = [
                { "index": 2, "color": (0xE0,0x20,0x20) },
                { "index": 2, "color": (0xE0,0x68,0x10) },
                { "index": 2, "color": (0xE0,0xE0,0x00) },
                { "index": 2, "color": (0x58,0xE0,0x00) },
                { "index": 2, "color": (0x00,0xE0,0x00) },
                { "index": 2, "color": (0x08,0x85,0x40) },
                { "index": 2, "color": (0x08,0x60,0x80) },
                { "index": 2, "color": (0x50,0x30,0x90) },
                { "index": 2, "color": (0x90,0x00,0x90) },
                { "index": 2, "color": (0xA8,0x10,0x58) }
            ]

            grayscale_palette = common.grayscale(self.get_colors_from_master("gravity"))
            faded_palette = common.palette_pull_towards_color(grayscale_palette,(0,0,0),2.0/3.0)

            for shift in palette_shifts:
                timed_palette.append((shift["index"],common.palette_shift(faded_palette,shift["color"])))

        elif variant_type.lower().replace("_"," ") == "death suit":
            palette_indexes = [21,6,3,4,5,5,6,6,80]
            for i,_ in enumerate(palette_indexes):
                timed_palette.append((palette_indexes[i], common.palette_pull_towards_color(base_palette,(0xFF,0xFF,0xFF),float(i)/8.0)))

        elif variant_type.lower() == "death":
            death_palette = self.get_colors_from_master("death")
            palette_indexes = [21,6,3,4,5,5,6,6,80]
            for i,_ in enumerate(palette_indexes):
                timed_palette.append((palette_indexes[i], common.palette_pull_towards_color(death_palette,(0xFF,0xFF,0xFF),float(i)/8.0)))

        elif variant_type.lower() == "flash":
            # in the ROM, the flash timing is technically coded as "2", but that looks abnormally fast if rendered outside the ROM,
            # so maybe there is some hidden code in the ROM that doubles that before it is used
            FLASH_TIMING = 4
            flash_master_palette = self.get_colors_from_master("flash")
            flash_bright_portion = flash_master_palette[:9]
            flash_rotating_portion = flash_master_palette[9:]
            palette_shifts = [
                ( 0, 0, 0),
                (24,24,24),
                (56,56,56),
                (88,88,88),
                (56,56,56),
                (24,24,24)
            ]
            for i,_ in enumerate(palette_shifts):
                color = palette_shifts[i]
                str_index = len(palette_shifts) - i
                timed_palette.append((FLASH_TIMING,common.palette_shift(flash_bright_portion,color) + flash_rotating_portion[str_index:] + flash_rotating_portion[:str_index]))

        elif variant_type.lower() == "sepia":
            timed_palette = [(0, common.sepia(self.get_colors_from_master("power")))]

        elif variant_type.lower().replace("_"," ") == "sepia hurt":
            sepia_palette = common.sepia(self.get_colors_from_master("power"))
            timed_palette = [(0, common.palette_pull_towards_color(sepia_palette,(0xFF,0xFF,0xFF),0.6))]

        elif variant_type.lower() == "door":
            TRANSITION_TIME = 30
            visor_color = self.get_colors_from_master("power")[3]
            for i in range(13):
                [new_visor_color] = common.palette_pull_towards_color([visor_color],base_palette[3],float(i)/13.0)
                dimmed_base_palette = common.palette_pull_towards_color(base_palette,(0,0,0),float(13-i)/13.0)
                dimmed_base_palette[3] = new_visor_color
                timed_palette.append((3,dimmed_base_palette))
            timed_palette.append((TRANSITION_TIME,base_palette))
            for i in range(13):
                [new_visor_color] = common.palette_pull_towards_color([visor_color],base_palette[3],float(12-i)/13.0)
                dimmed_base_palette = common.palette_pull_towards_color(base_palette,(0,0,0),float(1+i)/13.0)
                dimmed_base_palette[3] = new_visor_color
                timed_palette.append((3,dimmed_base_palette))
            timed_palette.append((TRANSITION_TIME,[(0,0,0) for _ in range(15)]))

        elif variant_type.lower().replace("-", "").replace("_","") == "xray":
            visor_colors = self.get_colors_from_master("xray")
            timed_palette = [(6, base_palette[:3]+[color]+base_palette[4:]) for color in visor_colors]

        elif variant_type.lower().replace("_", " ") == "file select":
            timed_palette = [(0, self.get_colors_from_master("file select"))]

        else:
            # FIXME: English
            raise AssertionError(f"unrecognized palette request: {overall_type}, {variant_type}")

        # now scrub the palette to get rid of floats and numbers that are too large/small
        return [(time,[(max(0,min(255,int(color_plane))) for color_plane in color) for color in palette]) for (time,palette) in timed_palette]

    def get_projectile_priority(self, projectiles=["power_beam"]):
        for beam in ["power","spazer","wave","plasma","ice"]:
            if beam in projectiles or (beam + "_beam") in projectiles:
                projectile = beam
        return projectile

    def get_projectile(self, projectile="lemon"):
        '''
        BEHAVIOR
        ========
        lemon:                16 frames, alternate on/off starting with on; then starting a new shot
        iced lemon:        randomly choose ice0 or ice1/ice2, drop a particle shower ice_particle[0-3]
            ice0:                16 frames, alternate on/off starting with on, h-flip each time; then starting a new shot
            ice1/ice2:    16 frames, alternate on/off starting with on, cycle 1/2 each time; then starting a new shot
        wave:                    16 frames, run trail in bell curve, each spot deteriorates
        spazer:                16 frames, shoot single, alternate on/shift/off starting with on, split to 3 with space of 6, space of 14; then starting a new shot
        plasma:                16 frames, shoot single, alternate on/shift/off starting with on, continue to grow to 32 long

        CHARGING BEHAVIOR
        =================
        frames: 0 1 0 1 0 1 0 1 2 1 2 1 2 1 2 1 2 3 [2 3]

        CHARGED SHOT BEHAVIOR
        =====================
        lemon:    [4 5], orange ice particles
        ice:        [4 5], blue ice particles
        wave:        [4 5], wave particles
        spazer:    special charge shot, no particles, alternate standard spazer/special
        plasma:    special charge shot, no particles, alternate standard plasma/special

        COMBO BEHAVIOR
        ==============
                        COLOR        NUMBER    BEHAVIOR
                        =====        ======    ========
        ice:        BLUE        single    ice particles
        plasma:    green        single    plasma texture
        wave:        purple    trail        wave motion
        spazer:    yellow    TRIPLE    spazer texture
        lemon:    no change

        <-- higher priority
        COLOR:        ice, plasma, wave, spazer, lemon
        NUMBER:     spazer, plasma+wave (double), plasma, wave, ice, lemon
        BEHAVIOR:    ice, wave, plasma, spazer, lemon

        SIZE
        ====
        lemon:            no change
        iced lemon:    no change
        wave:                no change
        spazer:            starts 9 long, then 16 long
        plasma:            starts 5 long, then 32 long
        '''

    def get_projectile_palette(self, projectile="power_beam"):
        # Ice:        Blue        ice_beam
        # Plasma:    Green        plasma_beam
        # Wave:        Purple    wave_beam
        # Spazer:    Yellow    spazer_beam
        # Power:    Lemon        power_beam
        # Charged Shots use all 6 colors
        # Charged Shots Ice-like particles use [0,1,2,5]
        palette_switcher = {
            "power_beam": [
                (107, 40, 33),
                (173, 81, 57),
                (255,121, 49),
                (247,231,    0),
                (255,255,165),
                (255,255,255)
            ],
            "ice_beam": [
                (    0, 56,173),
                (    0,121,222),
                (    0,182,255),
                ( 82,199,231),
                (115,223,255),
                (255,255,255)
            ],
            "wave_beam": [
                ( 99,    0, 99),
                (181,    0,181),
                (255,    0,255),
                (255,113,255),
                (255,182,255),
                (255,255,255)
            ],
            "spazer_beam": [
                (115, 56,    0),
                (181,134,    0),
                (255,255,    0),
                (255,255,148),
                (255,255,214),
                (255,255,255)
            ],
            "plasma_beam": [
                (    0, 97, 41),
                (    0,166, 74),
                (    0,255,115),
                (148,255,148),
                (214,255,214),
                (255,255,255)
            ]
        }

        palette = palette_switcher.get(projectile) if projectile in palette_switcher else palette_switcher.get("power_beam")

        return palette

    def get_supplemental_tiles(self,animation,direction,pose_number,palettes,frame_number):
        return_tiles = []

        tiles = { #tiles
            "Stand": { #Stand
                "right": [ #right
                    {
                        "pose": [0],
                        "frame": list(range(16)),
                        "image": "lemon_right",
                        "pos": [11,-8],
                        "pos_offset": [8,0],
                        "palette": "power_beam_projectile"
                    }
                ]
            }
        }
        tiles = {} #don't do this stuff yet

        if animation in tiles:
            if direction in tiles[animation]:
                for direction_tile in tiles[animation][direction]:
                    if pose_number in direction_tile["pose"]:
                        for frame_check in direction_tile["frame"]:
                            if frame_number == frame_check or frame_check > 0 and frame_number % frame_check == 0:
                                print(str(frame_check) + " in pose")
                                direction_tile["pos"][0] += direction_tile["pos_offset"][0] * frame_check
                                direction_tile["pos"][1] += direction_tile["pos_offset"][1] * frame_check
                                return_tiles.append(direction_tile)

        return return_tiles

    def get_alternative_direction(self, animation, direction):
        # suggest an alternative direction, which can be referenced if the original direction doesn't have an animation
        direction_dict = self.animations[animation]
        split_string = direction.split("_aim_")
        facing = split_string[0]
        aiming = split_string[1] if len(split_string) > 1 else ""

        # now start searching for this facing and aiming in the JSON dict
        # start going down the list of alternative aiming if a pose does not have the original
        ALTERNATIVES = {
            "up": "diag_up",
            "diag_up": "shoot",
            "down": "diag_down",
            "diag_down": "shoot"
        }
        while(self.concatenate_facing_and_aiming(facing,aiming) not in direction_dict):
            if aiming in ALTERNATIVES:
                aiming = ALTERNATIVES[aiming]
            elif facing in direction_dict:     #no aim was available, try the pure facing
                return facing
            else:        #now we are really screwed, so just do anything
                return next(
                    iter(
                        [
                            x for x in list(
                                direction_dict.keys()
                            ) if "#" not in x
                        ]
                    )
                )

        # if things went well, we are here
        return "_aim_".join([facing,aiming])

    def concatenate_facing_and_aiming(self, facing, aiming):
        return "_aim_".join([facing,aiming])

    def get_palette(self, palettes, default_range=[], frame_number=0):
        # get the actual list of associated palettes
        palette_timing_list = self.get_timed_palette_converter(palettes)
        # figure out the timing
        palette_timing_progression = list(itertools.accumulate([duration for (duration,_) in palette_timing_list]))

        # if the last palette has "zero" duration, indicating to freeze on that palette, and we are past that point
        if palette_timing_list[-1][0] == 0 and frame_number >= palette_timing_progression[-1]:
            palette_number = -1        #use the last palette
        elif palette_timing_progression[-1] == 0 and frame_number < 0:     #can happen if someone switches from a dynamic palette to a static palette, and then backsteps a lot
            palette_number = 0         #use the first palette
        else:
            mod_frames = frame_number % palette_timing_progression[-1]
            palette_number = palette_timing_progression.index(min([x for x in palette_timing_progression if x >= mod_frames]))

        # now actually get that specific palette
        _,palette = palette_timing_list[palette_number]

        return palette

    def get_palette_duration(self, palettes):
        palette_timing_list = self.get_timed_palette_converter(palettes)
        palette_duration = sum([duration for (duration,_) in palette_timing_list])
        return palette_duration

    def get_timed_palette_converter(self, palette_list):
        # used to interface the new palette string format with the older get_timed_palette function.
        # could be refactored into the main code later, if coding time was not a valuable resource

        overall_type, variant_type = "power", "standard"     #defaults unless we are told otherwise
        for palette_string in palette_list:
            if palette_string.endswith("_suit"):
                # if we've got a suit base
                # [power|varia|gravity]
                overall_type = palette_string.replace("_suit","")
            if palette_string.endswith("_variant"):
                # if we've got a variant
                this_variant = palette_string.replace("_variant","")
                # if it's not currently set to base
                if variant_type not in ["standard"]:
                    # if we're not trying to set it to these low-priority ones
                    if this_variant not in ["xray"]:
                        # set it
                        variant_type = this_variant
                # else, move it away from standard
                else:
                    variant_type = this_variant

        return self.get_timed_palette(overall_type=overall_type, variant_type=variant_type)

    def get_alternate_tile(self, image_name, palettes):
        slugs = {}
        for palette in palettes:
            if '_' in palette:
                slugs[palette[palette.rfind('_')+1:]] = palette[:palette.rfind('_')]
        OPTIONAL_PORT_STRING = "optional_"
        if image_name.startswith(OPTIONAL_PORT_STRING):        #as would be for the cannon ports, which are optionally present
            if "yes_cannon-port" in palettes:
                image_name = image_name.replace(OPTIONAL_PORT_STRING,"")
                return self.images[image_name]
            return Image.new("RGBA",(0,0),0)
        # FIXME: English
        raise AssertionError(f"Could not locate tile with name {image_name}")
