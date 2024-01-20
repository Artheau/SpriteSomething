import importlib
import itertools
import json
import os
from base64 import b64encode
from binascii import crc32
from PIL import Image
from source.meta.classes.spritelib import SpriteParent
from source.meta.common import common

from . import plugins

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.load_plugins()

        self.link_globals = {
            "green_palette": [
                (0xFF, 0xFF, 0xFF),
                (0x00, 0x00, 0x00),
                (0x10, 0xAD, 0x42),   # changes
                (0xFF, 0xD6, 0x8C)
            ],
            "blue_palette": [
                (0xFF, 0xFF, 0xFF),
                (0x00, 0x00, 0x00),
                (0x18, 0x84, 0xFF),   # changes
                (0xFF, 0xD6, 0x8C)
            ],
            "red_palette": [
                (0xFF, 0xFF, 0xFF),
                (0x00, 0x00, 0x00),
                (0xFF, 0x08, 0x29),   # changes
                (0xFF, 0xD6, 0x8C)
            ],
            "gold_palette": [
                (0xFF, 0xFF, 0xFF),
                (0x00, 0x00, 0x00),
                (0xFF, 0x7B, 0x08),   # changes
                (0xFF, 0xD6, 0x8C)
            ]
        }
        self.master_palette = self.link_globals["green_palette"]

    def get_palette(self, palettes, default_range=[], frame_number=0):
        this_palette = []
        palette = "green"
        for color in ["blue","red","gold"]:
            if f"{color}_palette" in palettes:
                palette = color
        this_palette = self.link_globals[f"{palette}_palette"]

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
        for item in ["WEAPON","MAGNET","SLING"]:
            if image_name.startswith(item):
                if item.lower() in slugs:
                    found_alt = True
                    image_name = image_name.replace(
                        item,
                        slugs[item.lower()] + '_' + item.lower()
                    ) if not "none_" + item.lower() in palettes else \
                    "transparent"
        if "accessories" in slugs:
            for item, default in [
                    ("ITEM","pendant"),
                    ("CRYSTAL","crystal"),
                    ("BUSH_SHADOW","main_shadow")
                ]:
                if image_name.startswith(item):
                    found_alt = True
                    image_name = default.lower() if \
                        not "none_accessories" in palettes else \
                        "transparent"
            for item in ["BUSH","BOOK"]:
                if image_name.startswith(item):
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
        # get megadata
        patch_manifest_path = os.path.join(
            "resources",
            "app",
            self.resource_subpath,
            "manifests",
            "patch.json"
        )
        megadata = {}
        if os.path.isfile(patch_manifest_path):
            with open(patch_manifest_path) as patch_manifest:
                megadata = json.load(patch_manifest)
        megadata["modified"] = False
        if "sprites" in megadata:
            for sprite in megadata["sprites"]:
                megadata["sprites"][sprite]["patch"] = []
                megadata["sprites"][sprite]["modified"] = False

        megadata["sprites"] = self.get_2bpp(megadata["sprites"])

        game_name = rom.get_name()

        if "NAYRU" in game_name:
            gameID = "ages"
        elif "DIN" in game_name:
            gameID = "seasons"

        for sprite in megadata["sprites"]:
            if "global" in megadata["sprites"][sprite]["ips"]["header"]:
                spriteHeader = megadata["sprites"][sprite]["ips"]["header"]["global"]
            elif gameID in megadata["sprites"][sprite]["ips"]["header"]:
                spriteHeader = megadata["sprites"][sprite]["ips"]["header"][gameID]
            sprite_addr = int("0x" + (spriteHeader[0] + spriteHeader[1] + spriteHeader[2]).replace("0x", ""), 16)
            sprite_len = int("0x" + (spriteHeader[3] + spriteHeader[4]).replace("0x", ""), 16)
            rom.bulk_write(
                sprite_addr,
                megadata["sprites"][sprite]["patch"],
                sprite_len
            )
        return rom

    def get_2bpp(self, sprites):
        # vanilla palette for Link sprites
        vanillaPalette = self.link_globals["green_palette"]

        # port of appendBlock function
        def appendBlock(img, byteArr, x, y):
            for j in range(0, 8):
                row = []
                for i in range(0, 8):
                    pixel = img.getpixel((x + i, y + j))
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
        # get input image
        imgfile = self.get_master_PNG_image()
        imgfile = imgfile.convert("RGBA")

        # get pixel data
        # build patch files
        spriteIDs = sprites.keys()
        for sprite in spriteIDs:
            print(f"Examining {sprite.capitalize()} Data")
            for y in range(*sprites[sprite]["sheet_range"]["y"]):
                for x in range(*sprites[sprite]["sheet_range"]["x"]):
                    for y2 in range(*sprites[sprite]["sheet_range"]["y2"]):
                        if sprite == "link":
                            if y == 272 and x >= 56:
                                continue
                        sprites[sprite]["patch"] = appendBlock(
                            imgfile,
                            sprites[sprite]["patch"],
                            x,
                            y + y2
                        )

        return sprites

    def export_patch(self):
        verbose = False
        vanillaCRCs = {}    # hold vanilla CRCs for sprite data
        importedCRCs = {}   # calculate imported CRCs for comparison

        patch_fmt = "ips"

        patch_parts = {
            "ips": {
                "header": bytes(ord(x) for x in "PATCH"),
                "footer": bytes(ord(x) for x in "EOF")
            }
        }

        # port of encode function
        def encode(byteArr):
            ret = byteArr
            ret = bytes(ret)
            ret = b64encode(ret)
            ret = ret.decode()
            return ret

        # do the thing
        # gather all the things!

        # get megadata
        patch_manifest_path = os.path.join(
            "resources",
            "app",
            self.resource_subpath,
            "manifests",
            "patch.json"
        )
        megadata = {}
        if os.path.isfile(patch_manifest_path):
            with open(patch_manifest_path) as patch_manifest:
                megadata = json.load(patch_manifest)
        megadata["modified"] = False
        if "sprites" in megadata:
            for sprite in megadata["sprites"]:
                megadata["sprites"][sprite]["patch"] = []
                megadata["sprites"][sprite]["modified"] = False
        megadata["games"] = {}
        for gameID in ["ages","seasons"]:
            megadata["games"][gameID] = { "patch": [] }

        # print(megadata)
        spriteIDs = list(megadata["sprites"].keys())    # get sprite names
        gameIDs = list(megadata["games"].keys())        # get game names

        # make output dir
        #FIXME: Get output dir from user
        outputDir = os.path.join(
            "resources",
            "user",
            "gbc",
            "zelda4o",
            "link",
            "sheets"
        )
        if not os.path.isdir(outputDir):
            os.makedirs(outputDir)

        # get a slug for naming stuff
        basename = os.path.splitext(os.path.basename(self.filename))[0]

        # get input image
        imgfile = self.get_master_PNG_image()
        imgfile = imgfile.convert("RGBA")

        # get pixel data
        # build patch files
        megadata["sprites"] = self.get_2bpp(megadata["sprites"])

        # check to see if it's modded data
        for sprite in spriteIDs:
            vanillaCRCs[sprite] = int(megadata["sprites"][sprite]["bin"]["vanilla_crc"], 16)
            importedCRCs[sprite] = crc32(bytes(megadata["sprites"][sprite]["patch"]))
            megadata["sprites"][sprite]["modified"] = importedCRCs[sprite] != vanillaCRCs[sprite]
            # if it's been modded, print a message
            if megadata["sprites"][sprite]["modified"]:
                print(f"Modded {sprite.capitalize()}")
                megadata["modified"] = True
            else:
                print(f"Vanilla {sprite.capitalize()}")
            # output binary data if verbose for good measure
            if megadata["sprites"][sprite]["modified"] or verbose:
                with open(
                    os.path.join(
                        outputDir,
                        f"{basename}_{sprite}.bin"
                    ),
                    "wb"
                ) as spriteBin:
                    spriteBin.write(bytes(megadata["sprites"][sprite]["patch"]))

        # if we got this far, let's build some stuff
        if megadata["modified"]:
            print({"vanilla":vanillaCRCs,"imported":importedCRCs})

        for sprite in spriteIDs:
            if megadata["sprites"][sprite]["modified"]:
                print(f"Building {sprite.capitalize()} {patch_fmt.upper()}")
                for gameID in gameIDs:
                    spriteHeader = []
                    if "global" in megadata["sprites"][sprite]["ips"]["header"]:
                        spriteHeader = megadata["sprites"][sprite]["ips"]["header"]["global"]
                    elif gameID in megadata["sprites"][sprite]["ips"]["header"]:
                        spriteHeader = megadata["sprites"][sprite]["ips"]["header"][gameID]
                    spriteHeader = [int(x, 16) for x in spriteHeader]
                    megadata["games"][gameID]["patch"] = [
                        *patch_parts[patch_fmt]["header"]
                    ]
                    megadata["games"][gameID]["patch"] = [
                        *megadata["games"][gameID]["patch"],
                        *spriteHeader
                    ]
                    megadata["games"][gameID]["patch"] = [
                        *megadata["games"][gameID]["patch"],
                        *megadata["sprites"][sprite]["patch"]
                    ]
                    megadata["games"][gameID]["patch"] = [
                        *megadata["games"][gameID]["patch"],
                        *patch_parts[patch_fmt]["footer"]
                    ]

        # put footer on patches
        # if modified, write patches
        for gameID in gameIDs:
            if megadata["sprites"][sprite]["modified"]:
                with open(
                    os.path.join(
                        outputDir,
                        f"{basename}_{gameID}.{patch_fmt}"
                    ),
                    "wb"
                ) as ipsFile:
                    ipsFile.write(bytes(megadata["games"][gameID]["patch"]))

        # if it's been modded, build YAML patch file
        if megadata["modified"]:
            with open(
                os.path.join(
                    outputDir,
                    f"{basename}.yaml"
                ),
                "w"
            ) as yamlFile:
                print("Building YAML Patch File")
                yamlFile.write("common:" + "\n")
                for sprite in spriteIDs:
                    if megadata["sprites"][sprite]["modified"]:
                        print(f" Adding {sprite.capitalize()}")
                        spriteHandle = sprite
                        if spriteHandle == "baby":
                            spriteHandle = "link_baby"
                        yamlFile.write(f"  spr_{spriteHandle}:" + "\n")
                        yamlFile.write("    0x0: " + encode(megadata["sprites"][sprite]["patch"]) + "\n")
        print()
