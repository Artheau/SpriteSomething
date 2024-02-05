import importlib
import itertools
import json
import os
import random
from base64 import b64encode
from binascii import crc32
from PIL import Image
from source.meta.classes.spritelib import SpriteParent
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
        for item in ["WEAPON","MAGNET","SLING","HALO"]:
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
                megadata["sprites"][sprite]["patch"] = {}
                megadata["sprites"][sprite]["modified"] = False

        game_name = rom.get_name()

        if "NAYRU" in game_name:
            gameID = "ages"
        elif "DIN" in game_name:
            gameID = "seasons"
        elif "ZELDA" in game_name:
            gameID = "la"
            size_MB = rom.get_size_in_MB()
            if size_MB == 1.0:
                gameID = "ladx"
            print(size_MB, gameID)
            exit(1)

        # get input image
        imgfile = None
        if "sheet" in sprites[sprite] and gameID in sprites[sprite]["sheet"]:
            imgfile = self.get_image(
                sprites[sprite]["sheet"][gameID]
            )
        else:
            imgfile = self.get_master_PNG_image()
        imgfile = imgfile.convert("RGBA")

        megadata["sprites"] = self.get_2bpp(
            megadata["sprites"],
            sprite,
            patch["note"],
            patch["sheet"][1],
            imgfile
        )

        # for sprite in megadata["sprites"]:
        #     if gameID in megadata["sprites"][sprite]["ips"]["header"]:
        #         spriteHeader = megadata["sprites"][sprite]["ips"]["header"][gameID]
        #     elif "global" in megadata["sprites"][sprite]["ips"]["header"]:
        #         spriteHeader = megadata["sprites"][sprite]["ips"]["header"]["global"]
        #     sprite_addr = int("0x" + (spriteHeader[0] + spriteHeader[1] + spriteHeader[2]).replace("0x", ""), 16)
        #     sprite_len = int("0x" + (spriteHeader[3] + spriteHeader[4]).replace("0x", ""), 16)
        #     rom.bulk_write(
        #         sprite_addr,
        #         megadata["sprites"][sprite]["patch"],
        #         sprite_len
        #     )
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
                megadata["sprites"][sprite]["patch"] = {}
                megadata["sprites"][sprite]["modified"] = False
        megadata["games"] = {}
        for gameID in [
            "ages",
            "seasons",
            "ladx"
        ]:
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

        # check to see if it's modded data
        for sprite in spriteIDs:
            print(f"Examining {myString(sprite).ucfirst()} Data")
            for patch in megadata["sprites"][sprite]["ips"]:
                # get input image
                imgfile = None
                if "address" in patch:
                    if "sheet" in patch and patch["sheet"][0][0] != "master":
                        animation = patch["sheet"][0][0]
                        direction = patch["sheet"][0][1] if len(patch["sheet"][0]) > 1 else ""
                        print(f" Loading: '{animation}/{direction}' for '{patch['note']}'")
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

                # output binary data if verbose for good measure
                if patch["note"] in megadata["sprites"][sprite]["patch"]:
                    with open(
                        os.path.join(
                            outputDir,
                            common.filename_scrub(f"{basename}_{sprite}_{patch['note']}.bin")
                        ),
                        "wb+"
                    ) as spriteBin:
                        spriteBin.write(bytes(megadata["sprites"][sprite]["patch"][patch['note']]))

            vanillaCRCs[sprite] = int(megadata["sprites"][sprite]["bin"]["vanilla_crc"], 16)
            importedCRCs[sprite] = crc32(bytes(megadata["sprites"][sprite]["patch"][patch['note']])) if patch["note"] in megadata["sprites"][sprite]["patch"] else -1
            megadata["sprites"][sprite]["modified"] = importedCRCs[sprite] != vanillaCRCs[sprite]
            # if it's been modded, print a message
            if megadata["sprites"][sprite]["modified"]:
                print(f" Modded {myString(sprite).ucfirst()}")
                megadata["modified"] = True
            else:
                print(f" Vanilla {myString(sprite).ucfirst()}")

        # if we got this far, let's build some stuff
        if megadata["modified"]:
            print({"vanilla":vanillaCRCs,"imported":importedCRCs})

        for sprite in spriteIDs:
            if megadata["sprites"][sprite]["modified"]:
                print(f"Building {myString(sprite).ucfirst()} {patch_fmt.upper()}")
                for gameID in gameIDs:
                    header_added = False
                    for patch in megadata["sprites"][sprite]["ips"]:
                        patch_note = patch["note"]
                        if "address" in patch:
                            for address in patch["address"]:
                                if gameID in address["games"]:
                                    if not header_added:
                                        megadata["games"][gameID]["patch"] = [
                                            *patch_parts[patch_fmt]["header"]
                                        ]
                                        header_added = True
                                    print(
                                        f" Adding '{patch_note}' " +
                                        f"[{sprite}] " +
                                        f"for '{gameID}' " +
                                        f"{address['locations']}"
                                    )
                                    for locationData in address["locations"]:
                                        patch_length = len(bytes(megadata["sprites"][sprite]["patch"][patch["note"]]))
                                        patch_length = hex(patch_length)
                                        patch_length = patch_length.replace("0x","")
                                        patch_length = patch_length.zfill(4)
                                        patch_length = [
                                            int(patch_length[:2],16),
                                            int(patch_length[2:],16)
                                        ]

                                        location = []
                                        locationData = locationData.replace("0x","")
                                        for idx in range(0,len(locationData),2):
                                            location.append(int(locationData[idx:idx+2], 16))
                                        megadata["games"][gameID]["patch"] = [
                                            *megadata["games"][gameID]["patch"],
                                            *location,
                                            *patch_length
                                        ]
                                        megadata["games"][gameID]["patch"] = [
                                            *megadata["games"][gameID]["patch"],
                                            *megadata["sprites"][sprite]["patch"][patch["note"]]
                                        ]
                    if header_added:
                        megadata["games"][gameID]["patch"] = [
                            *megadata["games"][gameID]["patch"],
                            *patch_parts[patch_fmt]["footer"]
                        ]

        # if modified, write patches
        for gameID in gameIDs:
            if megadata["sprites"][sprite]["modified"]:
                print(f"Writing {myString(gameID).ucfirst()} IPS")
                patch_length = len(megadata["games"][gameID]["patch"])
                if patch_length <= 8:
                    patch_mismatch = "long" if patch_length > 256 else "short"
                    print(f" {myString(gameID).ucfirst()} had a {patch_mismatch} sheet for IPS writing")
                    with open(
                        os.path.join(
                            outputDir,
                            f"{basename}_{gameID}.json"
                        ),
                        "w"
                    ) as jsonFile:
                        jsonFile.write(json.dumps(megadata["games"][gameID]["patch"], indent=2))
                else:
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
                        print(f" Adding {myString(sprite).ucfirst()}")
                        spriteHandle = sprite
                        if spriteHandle == "baby":
                            spriteHandle = "link_baby"
                        yamlFile.write(f"  spr_{spriteHandle}:" + "\n")
                        patchData = []
                        for [note, patch] in megadata["sprites"][sprite]["patch"].items():
                            patchData += patch
                        yamlFile.write("    0x0: " + encode(patchData) + "\n")
        print()
