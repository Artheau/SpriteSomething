import importlib
import itertools
import json
import pathlib
import os
import random
from base64 import b64encode
from binascii import crc32
from PIL import Image
from source.meta.classes.spritelib import SpriteParent
from source.meta.classes.patch.ipslib import IPSFile, Record
from source.meta.common import common

from . import plugins

class myString(str):
    def __init__(self, value):
        self.value = value
    def ucfirst(self):
        return self.value[:1].upper() + self.value[1:]

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.load_plugins()

        self.link_globals = {
            "green_palette": [
                (0xFF, 0xFF, 0xFF),   # white
                (0x00, 0x00, 0x00),   # border
                (0x10, 0xAD, 0x42),   # mail
                (0xFF, 0xD6, 0x8C)    # skin
            ],
            "blue_palette": [
                (0xFF, 0xFF, 0xFF),   # white
                (0x00, 0x00, 0x00),   # border
                (0x18, 0x84, 0xFF),   # mail
                (0xFF, 0xD6, 0x8C)    # skin
            ],
            "red_palette": [
                (0xFF, 0xFF, 0xFF),   # white
                (0x00, 0x00, 0x00),   # border
                (0xFF, 0x08, 0x29),   # mail
                (0xFF, 0xD6, 0x8C)    # skin
            ],
            "gold_palette": [
                (0xFF, 0xFF, 0xFF),   # white
                (0x00, 0x00, 0x00),   # border
                (0xFF, 0x7B, 0x08),   # mail
                (0xFF, 0xD6, 0x8C)    # skin
            ],
            # "invertgreen_palette": [
            #     (0xFF, 0xFF, 0xFF),   # white
            #     (0x10, 0xFF, 0x42),   # border
            #     (0x10, 0xAD, 0x42),   # mail
            #     (0x00, 0x00, 0x00)    # skin
            # ],
            "invertblue_palette": [
                (0xFF, 0xFF, 0xFF),   # white
                (0x73, 0xAD, 0xFF),   # border
                (0x00, 0x00, 0xFF),   # mail
                (0x00, 0x00, 0x00)    # skin
            ],
            "invertred_palette": [
                (0xFF, 0xFF, 0xFF),   # white
                (0xFF, 0xB5, 0x31),   # border
                (0xDE, 0x00, 0x00),   # mail
                (0x00, 0x00, 0x00)    # skin
            ],
            # "invertgold_palette": [
            #     (0xFF, 0xFF, 0xFF),   # white
            #     (0xFF, 0xCD, 0x08),   # border
            #     (0xFF, 0x7B, 0x08),   # mail
            #     (0x00, 0x00, 0x00)    # skin
            # ]
        }
        self.master_palette = self.link_globals["green_palette"]

    def get_representative_images(self, style):
        '''
        Generate preview image set
        '''
        return_images = []
        return_images += super().get_representative_images(style)

        if style.lower() in ["snow"]:
            return_images += self.get_defined_images(style.lower(), return_images)

        return return_images

    def get_defined_images(self, style, return_images):
        bgfilename = f"{style}.png"
        bgimg = Image.new("RGBA",(16*4,16*6),(0,0,0,0))
        if "sprite.name" in self.metadata and self.metadata["sprite.name"]:
            sprite_save_name = self.metadata["sprite.name"].lower()
        else:
            # FIXME: English
            sprite_save_name = "unknown"

        for i,_ in enumerate(return_images):
            img = return_images[i][1]
            pose_coords = (0, 0)
            if len(return_images[i]) > 2:
                pose_coords = tuple(return_images[i][2])
            bgimg.paste(img,pose_coords,img)
        bgimg = bgimg.resize((bgimg.size[0] * 2, bgimg.size[1] * 2), Image.NEAREST)
        return_images.append(("-".join([sprite_save_name,bgfilename]),bgimg))
        return_images = return_images[-1:]
        return return_images

    def get_palette(self, palettes, default_range=[], frame_number=0):
        this_palette = []
        palette = "green_palette"
        for sent_palette in palettes:
            if "_palette" in sent_palette and sent_palette in self.link_globals:
                palette = sent_palette
        this_palette = self.link_globals[palette]

        return this_palette

    def get_alternate_tile(self, image_name, palettes):
        '''
        Get alternate tile to replace requested tile
        '''
        slugs = {}
        found_alt = ""
        for palette in palettes:
            if '_' in palette:
                slugs[
                    palette[
                        palette.rfind('_')+1:
                    ]
                ] = palette[
                    :palette.rfind('_')
                ]
        for item in ["WEAPON","SHIELD","BOOMERANG","MAGNET","SLING","HALO"]:
            if image_name.startswith(item):
                if item.lower() in slugs and not found_alt:
                    found_alt = True
                    image_name = image_name.replace(
                        item,
                        slugs[item.lower()] + '_' + item.lower()
                    ) if not "none_" + item.lower() in palettes else \
                    "transparent"
        if "accessories" in slugs:
            for item, default in [
                    ("ITEM","sword_weapon0"),
                    ("INSTRUMENT","essence0"),
                    ("ESSENCE_BG","essence_bgblue"),
                    ("ESSENCE","essence0"),
                    ("BUSH_SHADOW","main_shadow")
                ]:
                if image_name.startswith(item) and not found_alt:
                    found_alt = True
                    if not "none_accessories" in palettes:
                        image_name = default.lower()
                        if item == "ESSENCE" and False:
                            essenceIDs = [x for x in range(18)]
                            essenceIDs.remove(8)
                            essenceIDs.remove(17)
                            image_name = "essence" + str(random.choice(essenceIDs))
                    else:
                        image_name = "transparent"
            for item in ["BUSH","BOOK"]:
                if image_name.startswith(item) and not found_alt:
                    found_alt = True
                    image_name = image_name.lower() if \
                        not "none_accessories" in palettes else \
                        "transparent"
        if found_alt:
            return self.images[image_name]
        if True:
            #TODO: Track down why this function is being called without
            # spiffy button info during sprite load
            return Image.new("RGBA",(0,0),0)
        # FIXME: English
        raise AssertionError(f"Could not locate tile with name {image_name}")

    def import_cleanup(self):
        '''
        Post-import cleanup
        '''
        self.load_plugins()
        self.equipment = self.plugins.equipment_test(False)
        if hasattr(self, "images"):
            self.images = dict(self.images,**self.equipment)

    def inject_into_ROM(self, spiffy_dict, rom):
        #return the injected ROM

        game_name = rom.get_name()
        size_MB = rom.get_size_in_MB()

        if "NAYRU" in game_name:
            gameIDs = ["ages"]
            spriteIDs = ["link","baby"]
        elif "DIN" in game_name:
            gameIDs = ["seasons"]
            spriteIDs = ["link","baby"]
        elif "ZELDA" in game_name:
            gameIDs = ["ladx"]
            spriteIDs = ["LADX"]
            # gameIDs = ["la"]
            # if size_MB == 1.0:
            #     gameIDs = ["ladx"]
        # print(size_MB, gameIDs, spriteIDs)

        patch_fmt = "ips"
        patch_file = None

        if patch_fmt == "ips":
            patch_file = self.export_IPS(gameIDs, spriteIDs)

        if patch_file:
            # get a slug for naming stuff
            basename = os.path.splitext(os.path.basename(self.filename))[0]

            # write IPS
            patch_file.save(f"./{basename}_{gameIDs[0]}.{patch_fmt}")
            # write BIN
            patch_file.save_bin(f"./{basename}_{gameIDs[0]}.bin")

            # patch ROM
            rom.write_raw(
                patch_file.apply_patch(
                    rom.read_raw()
                )
            )

        return rom

    # self:     self
    # sprites:  object to return to
    # sprite:   spriteID to print in debug statements
    # note:     sprite note to differentiate this patch
    # ranges:   sheet ranges to collect from input image
    # imgfile:  input image
    def get_2bpp(self, sprites, sprite, note, ranges, imgfile=None):
        # vanilla palette for Link sprites
        vanillaPalette = self.link_globals["green_palette"]

        width = 0
        height = 0
        if imgfile:
            width, height = imgfile.size

        # port of appendBlock function
        def appendBlock(img, byteArr, x, y):
            for j in range(0, 8):
                row = []
                for i in range(0, 8):
                    pixel = 0
                    try:
                        pixel = img.getpixel((x + i, y + j))
                    except Exception as e:
                        print(e, ((x+i),(y+j)))
                        exit(1)
                    if len(pixel) >= 4 and pixel[3] == 0:
                        # print("Adding Index: 0*")
                        row.append(0)
                    elif pixel[:3] in vanillaPalette:
                        # print(f"Adding Index: {vanillaPalette.index(pixel[:3])}")
                        row.append(vanillaPalette.index(pixel[:3]))
                    else:
                        print(f"Adding Pixel: {pixel}")
                        row.append(pixel)
                        exit()
                rowLow = 0
                rowHigh = 0
                # print(type(row[i]))
                for i in range(0, 8):
                    rowLow |= (row[i] & 1) << (7 - i)
                    rowHigh |= ((row[i] & 2) >> 1) << (7 - i)
                byteArr = [*byteArr, rowLow, rowHigh]
            return byteArr

        # get pixel data
        # build patch file
        yRange, xRange, y2Range, _ = ranges.values()
        if yRange[1] > height:
            yRange[1] = height
        if xRange[1] > width:
            xRange[1] = width
        for y in range(*yRange):
            for x in range(*xRange):
                for y2 in range(*y2Range):
                    if sprite == "link":
                        if y == 272 and x >= 56:
                            continue
                    sprites[sprite]["patch"][note] = appendBlock(
                        imgfile,
                        sprites[sprite]["patch"][note],
                        x,
                        y + y2
                    )

        return sprites

    def export_IPS(self, gameIDs=[], spriteIDs=[]):
        # port of encode function
        def yaml_encode(byteArr):
            ret = byteArr
            ret = bytes(ret)
            ret = b64encode(ret)
            ret = ret.decode()
            return ret

        patch_file = IPSFile()

        # get megadata
        patch_manifest_path = os.path.join(
            "resources",
            "app",
            self.resource_subpath,
            "manifests",
            "patch.json"
        )
        megadata = {}
        vanillaCRCs = {}
        importedCRCs = {}
        if os.path.isfile(patch_manifest_path):
            with open(patch_manifest_path) as patch_manifest:
                megadata = json.load(patch_manifest)
        megadata["modified"] = False
        if "sprites" in megadata:
            for sprite in megadata["sprites"]:
                megadata["sprites"][sprite]["patch"] = {}
                megadata["sprites"][sprite]["modified"] = False
        megadata["games"] = {}
        for gameID in gameIDs:
            megadata["games"][gameID] = { "patch": [] }

        # check to see if it's modded data
        first_patch = True
        for sprite in spriteIDs:
            print(f"Examining {myString(sprite).ucfirst()} Data")
            for patch in megadata["sprites"][sprite]["ips"]:
                # get input image
                if not first_patch:
                    continue
                # first_patch = False
                imgfile = None
                if "address" in patch:
                    if "sheet" in patch and patch["sheet"][0][0] != "master":
                        animation = patch["sheet"][0][0]
                        direction = patch["sheet"][0][1] if len(patch["sheet"][0]) > 1 else ""
                        animation_title = animation
                        if direction != "":
                            animation_title += f"/{direction}"
                        print(f" Loading: '{animation_title}' for '{patch['note']}'")
                        imgfile = self.get_image(
                            animation,
                            direction,
                            0,
                            [],
                            0
                        )[0]
                    else:
                        print(f" Loading 'Master PNG' for '{patch['note']}'")
                        imgfile = self.get_master_PNG_image()
                    imgfile = imgfile.convert("RGBA")

                if imgfile:
                    # get pixel data
                    # build patch files
                    if patch["note"] not in megadata["sprites"][sprite]["patch"]:
                        megadata["sprites"][sprite]["patch"][patch["note"]] = []
                    megadata["sprites"].update(
                        {
                            patch['note']: self.get_2bpp(
                                megadata["sprites"],
                                sprite,
                                patch["note"],
                                patch["sheet"][1],
                                imgfile
                            )
                        }
                    )

            vanillaCRCs[sprite] = int(megadata["sprites"][sprite]["bin"]["vanilla_crc"], 16)
            importedCRCs[sprite] = crc32(bytes(megadata["sprites"][sprite]["patch"][patch['note']])) if patch["note"] in megadata["sprites"][sprite]["patch"] else -1
            if importedCRCs[sprite] != vanillaCRCs[sprite]:
                megadata["sprites"][sprite]["modified"] = True
                megadata["modified"] = True

        for sprite in spriteIDs:
            patch_fmt = "ips"
            print(f"Building {myString(sprite).ucfirst()} {patch_fmt.upper()}")
            for gameID in gameIDs:
                patches = 0
                header_added = False
                for patch in megadata["sprites"][sprite]["ips"]:
                    patches = patches + 1
                    # if patches not in [1,3]:
                    #     continue
                    patch_note = patch["note"]
                    if "address" in patch:
                        for address in patch["address"]:
                            if gameID in address["games"]:
                                print(
                                    f" Adding '{patch_note}' " +
                                    f"[{sprite}] " +
                                    f"for '{gameID}' " +
                                    f"{address['locations']}"
                                )
                                for locationData in address["locations"]:
                                    patch_file.add_record(
                                        locationData,
                                        megadata["sprites"][sprite]["patch"][patch["note"]]
                                    )

        # get a slug for naming stuff
        basename = os.path.splitext(os.path.basename(self.filename))[0]

        # if it's been modded, build YAML patch file
        if megadata["modified"]:
            with open(
                os.path.join(
                    f"./{basename}_{gameID}.yaml"
                ),
                "w"
            ) as yamlFile:
                print("Building YAML Patch File")
                yamlFile.write("common:" + "\n")
                for sprite in spriteIDs:
                    if megadata["sprites"][sprite]["modified"]:
                        print(f" Adding {myString(sprite).ucfirst()}")
                        spriteHandle = sprite
                        if spriteHandle == "baby":
                            spriteHandle = "link_baby"
                        yamlFile.write(f"  spr_{spriteHandle}:" + "\n")
                        patchData = []
                        for [note, patch] in megadata["sprites"][sprite]["patch"].items():
                            patchData += patch
                        yamlFile.write("    0x0: " + yaml_encode(patchData) + "\n")

        return patch_file
