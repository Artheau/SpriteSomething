# common functions for all entities (i.e. "Sprites")
# sprites are responsible for maintaining their widgets
# they have to contain PIL images of all of their data, and the offset info,
#  and how to assemble it
# and they have to interpret the global frame timer, and communicate back
#  when to next check in

try:
  import yaml
  from PIL import Image
except ModuleNotFoundError as e:
  print(e)

import itertools
import importlib
import io
import json
import os
import random
import tempfile
from functools import partial
from json.decoder import JSONDecodeError
from shutil import make_archive, move
from source.meta.classes import layoutlib
from source.meta.common import common

# TODO: make this an actual abstract class by importing 'abc'
#  and doing the things


class SpriteParent():
    # parent class for sprites to inherit
    def __init__(self, filename, manifest_dict, my_subpath, _):
        self.classic_name = manifest_dict["name"]  # e.g. "Samus" or "Link"
        # the path to this sprite's subfolder in resources
        self.resource_subpath = my_subpath
        self.internal_name = manifest_dict["folder name"]
        self.metadata = {
                            "sprite.name": "",
                            "author.name": "",
                            "author.name-short": ""
                        }
        self.filename = filename
        self.overview_scale_factor = 2
        self.overhead = True
        if "input" in manifest_dict and \
            "png" in manifest_dict["input"] and \
                "overview-scale-factor" in manifest_dict["input"]["png"]:
            osf = manifest_dict["input"]
            osf = osf["png"]
            osf = osf["overview-scale-factor"]
            self.overview_scale_factor = osf
        self.plugins = None
        self.has_plugins = False
        self.load_layout("")
        self.load_animations("")
        self.import_from_filename()
        self.view_only = False

    # to make a new sprite class, you must write code for all
    #  of the functions in this section below.
    # ======================== BEGIN ABSTRACT CODE ========================= #

    def load_plugins(self):
        normalized_path = os.path.normpath(self.resource_subpath)
        module_subname = normalized_path.replace(os.path.sep, '.')
        plugins_module = self.import_module(f"source.{module_subname}.plugins")
        self.plugins = plugins_module.Plugins()
        self.has_plugins = True

    # FIXME: English
    def import_from_ROM(self, rom):
        # self.images, self.master_palette = ?, ?
        raise AssertionError("called import_from_ROM() on Sprite base class")

    def import_from_binary_data(self, pixel_data, palette_data):
        # self.images, self.master_palette = ?, ?
        raise AssertionError(
            "called import_from_binary_data() on Sprite base class")

    def inject_into_ROM(self, spiffy_dict, rom):
        # return the injected ROM
        raise AssertionError("called export_to_ROM() on Sprite base class")

    def get_rdc_export_blocks(self):
        # return the binary blocks that are used to pack the RDC format
        raise AssertionError(
            "called get_sprite_export_blocks() on Sprite base class")

    def get_palette(self, palette_type, default_range, frame_number):
        # in most cases the child class will override this in order to
        #  provide functionality to things like spiffy buttons
        # and to implement dynamic palettes by leveraging the frame number

        # if the child class didn't tell us what to do, just go back to
        #  whatever palette it was on when it was imported
        return self.master_palette[default_range[0]:default_range[1]]

    def get_palette_duration(self, palettes):
        # in most cases will be overriden by the child class to
        #  report duration of a palette
        return 1

    # ========================= END ABSTRACT CODE ========================= #

    # the functions below here are special to the parent class and do not need
    # to be overwritten, unless you see a reason

    def load_layout(self, _):
        self.layout = layoutlib.Layout(common.get_resource(
            [self.resource_subpath, "manifests"], "layout.json"))

    def load_animations(self, _):
        with open(common.get_resource(
            [
                self.resource_subpath,
                "manifests"
            ],
            "animations.json"
        )) as file:
            self.animations = {}
            try:
                self.animations = json.load(file)
            except JSONDecodeError as e:
                raise ValueError(
                    "Animations manifest malformed: " +
                    os.sep.join([
                        self.resource_subpath,
                        "manifests",
                        "animations.json"
                    ])
                )

    def import_from_filename(self):
        _, file_extension = os.path.splitext(self.filename)
        if file_extension.lower() == '.png':
            self.import_from_PNG()
        elif file_extension.lower() == '.rdc':
            self.import_from_RDC()
        elif file_extension.lower() == '.zspr':
            self.import_from_ZSPR()
        elif file_extension.lower() in [
            '.sfc', '.smc',  # SNES RomHandler
            #        '.nes' # NES RomHandler
        ]:
            # dynamic import
            rom_path, _ = os.path.split(self.resource_subpath)
            rom_path = rom_path.replace(os.sep, '.')
            rom_module = self.import_module(f"source.{rom_path}.rom")
            self.import_from_ROM(rom_module.RomHandler(self.filename))
        # elif file_extension.lower() == ".4bpp":
        #     self.import_from_binary()
        self.import_cleanup()

    def import_from_PNG(self):
        with Image.open(self.filename) as master:
            self.images, self.master_palette = self.layout.extract_all_images_from_master(
                master)

    def import_from_RDC(self):
        with open(self.filename, "rb") as file:
            data = bytearray(file.read())

        pointer = 0
        HEADER_STRING = "RETRODATACONTAINER"
        readLen = len(HEADER_STRING)
        print(f"Read: {pointer} + {readLen} = {pointer + readLen}")
        print(f"Header:    {data[0:readLen].decode('utf-8')}")
        print()

        if data[pointer:(pointer + readLen)] != bytes(ord(x) for x in HEADER_STRING):
            # FIXME: English
            raise AssertionError("This file does not have a valid RDC header")

        pointer += readLen
        readLen = 1
        print(f"Read: {pointer} + {readLen} = {pointer + readLen}")
        version = common.from_u8(data[pointer:(pointer + readLen)])
        print(f"Version:   {version}")
        print()
        if int.from_bytes(data[pointer:(pointer + readLen)], byteorder='little', signed=False) == 1:
            pointer += readLen

            readLen = 4
            print(f"Read: {pointer} + {readLen} = {pointer + readLen}")
            number_of_blocks = common.from_u32(data[pointer:(pointer + readLen)])
            print(f"NumBlocks: {number_of_blocks}")
            print()

            block_types = { "0": "JSON Metadata", "4": "Type 2" }

            blocks = []
            for i in range(0, number_of_blocks):
                pointer += readLen
                readLen = 4
                # print(f"Read: {pointer} + {readLen} = {pointer + readLen}")
                block_type = common.from_u32(data[pointer:(pointer + readLen)])
                # print(f"Block Type: {block_type}/{block_types[str(block_type)]}")

                pointer += readLen
                readLen = 4
                # print(f"Read: {pointer} + {readLen} = {pointer + readLen}")
                block_offset = common.from_u32(data[pointer:(pointer + readLen)])
                # print(f"Block Offset: {block_offset}")
                blocks.append(
                    {
                        "typeID": block_type,
                        "type": block_types[str(block_type)],
                        "offset": block_offset
                    }
                )
                if i > 0:
                    blocks[i - 1]["length"] = block_offset - blocks[i - 1]["offset"]
                # print()

        print(blocks)

        pointer += readLen
        print(f"Read: {pointer} + {readLen} = {pointer + readLen}")
        readLen = data[pointer:200].decode("utf-8").find("O")
        authorName = data[pointer:(pointer + readLen - 1)].decode("utf-8")
        self.metadata["author.name"] = authorName
        self.metadata["author.name-short"] = authorName
        print(authorName)
        pointer += 1

        for block in blocks:
            pointer = block["offset"] + 1
            block_data = None
            if "length" in block:
                readLen = block["length"]
                block_data = (data[pointer:(pointer + readLen - 1)])
            else:
                block_data = (data[pointer:200])
            if block_data:
                if block["typeID"] == 0:
                    block_data = block_data.decode("utf-8")
                    block_data = block_data[block_data.find("{"):]
                    try:
                        block_data = json.loads(block_data)
                    except ValueError as e:
                        raise ValueError("Block Data malformed! Within Sprite Type: " + self.resource_subpath)
                    self.metadata["sprite.name"] = block_data["title"]
            print(f"Read: {pointer} + {readLen} = {pointer + readLen}")
            print(f"Block Data: {block_data}")

        print(self.metadata)

        # pointer += readLen
        # print(f"Read: {pointer} + {readLen} = {pointer + readLen}")
        # print(data[pointer:200])

    def import_from_ZSPR(self):
        with open(self.filename, "rb") as file:
            data = bytearray(file.read())

        HEADER_STRING = "ZSPR"

        if data[0:len(HEADER_STRING)] != bytes(ord(x) for x in HEADER_STRING):
            # FIXME: English
            raise AssertionError("This file does not have a valid ZSPR header")
        if data[len(HEADER_STRING)] == 1:
            print("ZSPRv1")
            pixel_data_offset = int.from_bytes(
                data[9:13], byteorder='little', signed=False)
            pixel_data_length = int.from_bytes(
                data[13:15], byteorder='little', signed=False)
            palette_data_offset = int.from_bytes(
                data[15:19], byteorder='little', signed=False)
            palette_data_length = int.from_bytes(
                data[19:21], byteorder='little', signed=False)
            offset = 29

            '''
 4 (header) +
 1 (version) +
 4 (checksum) +
 4 (sprite data offset) +
 2 (sprite data size) +
 4 (pal data offset) +
 2 (pal data size) +
 2 (sprite type) +
 6 (reserved)
==
29 (start of metadata)
            '''

            # I hate little endian so much.  So much.
            for key, byte_size in [
                ("sprite.name", 2),
                ("author.name", 2),
                ("author.name-short", 1)
            ]:
                i = 0
                null_terminator = b"\x00" * byte_size
                while data[offset + i:offset + i + byte_size] != null_terminator:
                    i += byte_size

                raw_string_slice = data[offset:offset + i]
                if byte_size == 1:
                    self.metadata[key] = str(
                        raw_string_slice, encoding="ascii")
                else:
                    self.metadata[key] = str(
                        raw_string_slice, encoding="utf-16-le")
                # have to add another byte_size to go over the null terminator
                offset += i + byte_size

            pixel_data = data[pixel_data_offset:pixel_data_offset +
                              pixel_data_length]
            palette_data = data[palette_data_offset:palette_data_offset +
                                palette_data_length]
            self.import_from_binary_data(pixel_data, palette_data)
        else:
            # FIXME: English
            raise AssertionError(f"No support is implemented for ZSPR version {int(data[4])}")

    def get_alphabet(self, rom):
        rom_name = rom.get_name()
        is_zsm = "ZSM" in rom_name
        bigText = { "": [0x00, 0x00 ] }
        addrs = { rom.type().lower(): [ "SNES0x00" ] }
        charClass = ""

        alphabetsPath = common.get_resource([self.resource_subpath, "..", "manifests"], "alphabets.json")
        with open(alphabetsPath, "r", encoding="utf-8") as alphabetsFile:
            key = "zsm" if is_zsm else self.resource_subpath.split(os.sep)[1]
            alphabetsJSON = {}
            try:
                alphabetsJSON = json.load(alphabetsFile)
            except ValueError as e:
                raise ValueError("Alphabets file malformed: " + alphabetsPath)
            alphaVersion = "base"
            romVersion = rom.read(0x7FE2, 1) if not is_zsm else "vanilla-like"
            if romVersion in [3, 4]:
                alphaVersion = "0003"
            if is_zsm or key == "zelda3":
                print(romVersion, alphaVersion)
            if key in alphabetsJSON:
                if alphaVersion in alphabetsJSON[key]:
                    bigText = alphabetsJSON[key][alphaVersion]["alphabet"]
                    addrs = alphabetsJSON[key][alphaVersion]["addrs"][self.internal_name]
                    charClass = alphabetsJSON[key][alphaVersion]["charClass"] if "charClass" in alphabetsJSON[key][alphaVersion] else ""

        if isinstance(addrs, dict):
            addrs = addrs[rom.type().lower()]
        return [bigText, addrs, charClass]

    def translate_author(self, rom):
        name = ""
        [bigText, addrs, _] = self.get_alphabet(rom)

        names = {}
        for addr in addrs:
            readType = "SNES" if "SNES" in addr else "PC"
            addr = addr[len(readType):]
            if int(str(addr), 16) > 0:
                names[addr] = ""
                data = []
                if readType == "SNES":
                    data = rom.bulk_read_from_snes_address(int(str(addr), 16), (28 * 2)).hex()
                elif readType == "PC":
                    data = rom.bulk_read(int(str(addr), 16), (28 * 2)).hex()
                n = 2
                data = [data[i:i+n] for i in range(0, len(data), n)]
                for hexCode in data:
                    for [bigLetter, bigLCodes] in bigText.items():
                        for bigLCode in bigLCodes:
                            if isinstance(bigLCode, str):
                                bigLCode = int(bigLCode, 16)
                            if int(f"0x{hexCode}", 16) == bigLCode:
                                # if bigLetter not in [ " ", "0", "Q" ]:
                                names[addr] += bigLetter
                if names[addr] != "":
                    names[addr] = " ".join(map(str.capitalize, names[addr].split())).strip()
                    names[addr] = names[addr].split("0 ")[0].strip()
                    names[addr] = " ".join(list(set(names[addr].split(" "))))
                    if names[addr] != "":
                        for [srch, repl] in [
                          [ "DA", "D" ],
                          [ "EQ", "E" ],
                          [ "G0", "G" ],
                          [ "I3", "I" ],
                          [ "Mt", "M" ],
                          [ "N_", "N" ],
                          [ "UQ", "U" ],
                          [ "Y6", "Y" ]
                        ]:
                            names[addr] = names[addr].replace(srch, repl).strip()
                            names[addr] = names[addr].replace(srch.lower(), repl.lower()).strip()
                    if names[addr] != "":
                        name = names[addr]
                        print("Found Sprite Author:", name, names)
                        return name
        return name

    # filename, gameName, paletteID, fmt
    def export_palette(self, filename="", gameName="", paletteID="", fmt="gimp"):
        if self.classic_name != "Link":
          return

        if filename == "":
          filename = self.classic_name.lower() + ".palette"
          if fmt != "binary":
            filename += '-' + fmt

        if fmt == "binary":
          write_buffer = bytearray()
          write_buffer.extend(self.get_binary_palettes())
          with open(filename, "wb") as palettes_file:
              palettes_file.write(write_buffer)
          return True

        palette_doc = []
        header = []
        footer = [""]
        clrfmt = lambda x:(
          "%d %d %d"
          %
          (
            x[0],
            x[1],
            x[2]
          )
        )

        # ASPR
        if fmt == "aspr":
          header = [
            "---"
          ]
          clrfmt = lambda x:(
            "%s"
            %
            str(x)
          )

        # GIMP
        # CinePaint
        # Inkscape
        # Krita
        elif fmt == "gimp":
          header = [
            "GIMP Palette",
            "Base Sprite Name: ".ljust(len("Custom Sprite Name: "))   + self.classic_name,
            "Base Palette Name: ".ljust(len("Custom Sprite Name: "))  + paletteID,
            "Base Game Name: ".ljust(len("Custom Sprite Name: "))     + gameName,
            "Custom Sprite Name: ".ljust(len("Custom Sprite Name: ")) + self.metadata["sprite.name"],
            "Author: ".ljust(len("Custom Sprite Name: "))             + self.metadata["author.name"],
            "Columns: ".ljust(len("Custom Sprite Name: "))            + str(0),
            "#"
          ]
          clrfmt = lambda x:(
            "%s %s %s\t%s"
            %
            (
              str(x[0]).rjust(3),
              str(x[1]).rjust(3),
              str(x[2]).rjust(3),
              " " or "Color Name"
            )
          )

        # Corel
        # Graphics Gale
        # Paint Shop Pro
        elif fmt == "jasc":
          header = [
            "JASC-PAL",
            "0100",
            "16"
          ]

        # Paint.NET
        elif fmt == "pdn":
          header = [
            "; paint.net Palette File",
            "; Lines that start with a semicolon are comments",
            "; Colors are written as 8-digit hexadecimal numbers: aarrggbb",
            "; For example, this would specify green: FF00FF00",
            "; The alpha ('aa') value specifies how transparent a color is. FF is fully opaque, 00 is fully transparent.",
            "; A palette must consist of ninety six (96) colors. If there are less than this, the remaining color",
            "; slots will be set to white (FFFFFFFF). If there are more, then the remaining colors will be ignored.",
            ";",
            "; Base Sprite Name: ".ljust(len("; Custom Sprite Name: "))   + self.classic_name,
            "; Base Palette Name: ".ljust(len("; Custom Sprite Name: "))  + paletteID,
            "; Base Game Name: ".ljust(len("; Custom Sprite Name: "))     + gameName,
            "; Custom Sprite Name: ".ljust(len("; Custom Sprite Name: ")) + self.metadata["sprite.name"],
            "; Author: ".ljust(len("; Custom Sprite Name: "))             + self.metadata["author.name"],
          ]
          clrfmt = lambda x:(
            "%s%s%s%s"
            %
            (
              "FF",
              (hex(x[0])[2:]).ljust(2,'0').upper(),
              (hex(x[1])[2:]).ljust(2,'0').upper(),
              (hex(x[2])[2:]).ljust(2,'0').upper()
            )
          )

        # TileShop
        elif fmt == "tileshop":
          header = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<!--',
            '<sprite>',
            "\t" + f"<base name=\"{self.classic_name}\" game=\"{gameName}\" />",
            "\t" + f"<palette name=\"{paletteID}\" />",
            "\t" + f"<custom name=\"{self.metadata['sprite.name']}\" author=\"{self.metadata['author.name']}\" />",
            '</sprite>',
            '-->',
            '<palette datafile="" color="Bgr15" zeroindextransparent="true">'
          ]
          clrfmt = lambda x:(
            "\t<nativecolor value=\"#%s%s%s%s\" />"
            %
            (
              (hex(x[0])[2:]).ljust(2,'0').upper(),
              (hex(x[1])[2:]).ljust(2,'0').upper(),
              (hex(x[2])[2:]).ljust(2,'0').upper(),
              "FF"
            )
          )
          footer = [
            '</palette>',
            ""
          ]
          pass

        palette_doc += header

        if fmt == "aspr":
          for paletteID in ["green","blue","red","bunny","gloves"]:
            palette_doc.append(f"{paletteID}:")
            if paletteID != "gloves":
              palette_doc.append(f"    col0: " + str((0,0,0)))
            for [colID, color] in enumerate(self.get_palette([paletteID])):
              colNum = colID
              if paletteID == "gloves":
                colNum = ["power","titan"][colNum]
              else:
                colNum += 1
                colNum = f"col{hex(colNum)[2:].upper()}"
              color = f"    {colNum}: " + str(color)
              palette_doc.append(color)
        else:
          palette_doc.append(clrfmt((0,0,0)))
          for color in self.get_palette([paletteID]):
            color = clrfmt(color)
            palette_doc.append(color)

        if fmt == "pdn":
          padding = 96 - len(palette_doc) + len(header)
          for i in range(padding):
            palette_doc.append("FFFFFFFF")

        palette_doc += footer

        with(open(filename, "w")) as palettes_file:
          palettes_file.write("\n".join(palette_doc))

        # print("\n".join(palette_doc))

    def get_supplemental_tiles(self, animation, direction, pose_number,
                               palettes, frame_number):
        return []

    def import_cleanup(self):
        pass

    def get_alternate_tile(self, image_name, _):
        # FIXME: English
        raise AssertionError(f"Image called {image_name} not found!")

    def get_tiles_for_pose(self, animation, direction, pose_number,
                           palettes, frame_number):
        pose_list = self.get_pose_list(animation, direction)
        if pose_number > len(pose_list):
            print(animation,direction,pose_number,palettes)
        tile_list = pose_list[pose_number]["tiles"][::-1]
        tile_list += self.get_supplemental_tiles(
            animation, direction, pose_number, palettes, frame_number)
        if "displacement" in pose_list[pose_number]:
            global_displacement = pose_list[pose_number]["displacement"]
        else:
            global_displacement = [0, 0]
        full_tile_list = []
        for tile_info in tile_list:
            # some poses have extra palette information, e.g. use "bunny" or
            #  "crystal_flash" palettes
            # which can (whole or in part) override certain parts of the
            #  palette specified in the argument
            new_palette = None
            for possible_palette_info_location in [
                    pose_list[pose_number],
                    tile_info]:
                if "palette" in possible_palette_info_location:
                    palette_info_location = possible_palette_info_location
                    new_palette = palette_info_location["palette"]

            if new_palette:
                palettes.append(new_palette)

            base_image = self.images[tile_info["image"]] if \
                tile_info["image"] in self.images else self.get_alternate_tile(
                tile_info["image"],
                palettes
            )
            if base_image is None:
                pass
                # print("Base image not found!")
            if "crop" in tile_info:
                base_image = base_image.crop(tuple(tile_info["crop"]))
                if base_image is None:
                    pass
                    # print("Cropped image broken!")
            if "flip" in tile_info:
                hflip = "h" in tile_info["flip"].lower()
                vflip = "v" in tile_info["flip"].lower()
                if (hflip and vflip) or "both" in tile_info["flip"].lower():
                    base_image = base_image.transpose(Image.ROTATE_180)
                    if base_image is None:
                        pass
                        # print("180ed image broken!")
                elif hflip:
                    base_image = base_image.transpose(Image.FLIP_LEFT_RIGHT)
                    if base_image is None:
                        pass
                        # print("H-flipped image broken!")
                elif vflip:
                    base_image = base_image.transpose(Image.FLIP_TOP_BOTTOM)
                    if base_image is None:
                        pass
                        # print("V-flipped image broken!")

            default_range = self.layout.get_property(
                "import palette interval", tile_info["image"])
            this_palette = self.get_palette(
                palettes, default_range, frame_number)

            base_image = common.apply_palette(base_image, this_palette)

            position = [tile_info["pos"][i] + global_displacement[i]
                        for i in range(2)]  # add the x and y coords

            full_tile_list.append((base_image, position))

        return full_tile_list

    def get_palette_loop_timer(self, animation, direction, palettes):
        pose_list = self.get_pose_list(animation, direction)
        returnvalue = 1  # default
        for pose_number,_ in enumerate(pose_list):
            tile_list = pose_list[pose_number]["tiles"][::-1]
            tile_list += self.get_supplemental_tiles(
                animation, direction, pose_number, palettes, 0)
            for tile_info in tile_list:
                new_palette = None
                for possible_palette_info_location in [
                    pose_list[pose_number],
                    tile_info
                ]:
                    if "palette" in possible_palette_info_location:
                        palette_info_location = possible_palette_info_location
                        new_palette = palette_info_location["palette"]
                if new_palette:
                    palettes.append(new_palette)

                this_palette_duration = max(
                    1, self.get_palette_duration(palettes))
                returnvalue = common.lcm(returnvalue, this_palette_duration)
        return returnvalue

    def get_pose_list(self, animation, direction):
        direction_dict = self.animations[animation]
        if direction in direction_dict:
            return direction_dict[direction]
        return []

    def get_alternative_direction(self, animation, direction):
        direction_dict = self.animations[animation]
        return next(iter(direction_dict.keys()))

    def assemble_tiles_to_completed_image(self, tile_list):
        # have to check this because some animations include "empty" poses
        if tile_list:
            min_x = min([x for im, (x, y) in tile_list])
            min_y = min([y for im, (x, y) in tile_list])
            max_x = max([im.size[0] + x for im, (x, y) in tile_list])
            max_y = max([im.size[1] + y for im, (x, y) in tile_list])

            # start out with a transparent image that is correctly sized
            working_image = Image.new(
                'RGBA',
                (max_x - min_x, max_y - min_y),
                0
            )
            for new_image, (x, y) in tile_list:
                # the third argument is the transparency mask, so it is not
                #  redundant to use the same variable name twice
                working_image.paste(
                    new_image,
                    (x - min_x, y - min_y),
                    new_image
                )
            return working_image, (min_x, min_y)
        # blank image and dummy offset
        return Image.new('RGBA', (1, 1), 0), (0, 0)

    def get_image(self, animation, direction, pose, palettes, frame_number):
        # What I hope for this to do is to just retrieve a single PIL Image
        #  that corresponds to a particular pose in a particular animation
        #  using the specified list of palettes
        # e.g. get_image("Walk", "right", 2, ["red_mail", "master_sword"])
        # and it will return (Image, position_offset)
        # the frame number here is passed as an argument to allow for the
        #  implementation of dynamic palettes
        tile_list = self.get_tiles_for_pose(
            animation, direction, pose, palettes, frame_number)
        assembled_image, offset = self.assemble_tiles_to_completed_image(
            tile_list)
        return assembled_image, offset

    def get_representative_images(self, style="default"):
        if "sprite.name" in self.metadata and self.metadata["sprite.name"]:
            sprite_save_name = self.metadata["sprite.name"].lower()
        else:
            # FIXME: English
            sprite_save_name = "unknown"

        manifest_file = common.get_resource(
            [self.resource_subpath, "manifests"], "representative-images.json")
        if manifest_file:
            with open(manifest_file) as manifest:
                manifest_image = {}
                try:
                    manifest_images = json.load(manifest)
                except JSONDecodeError as e:
                    raise ValueError("Manifest images malformed: " + manifest_file)
        else:
            manifest_images = {}

        if "default" not in manifest_images:
            # try to have sane defaults
            animationkeys = list(self.animations.keys())
            if "$schema" in animationkeys:
                animationkeys.remove("$schema")
            animation = animationkeys[0]  # default to first image here
            direction = list(self.animations[animation].keys())[
                0]  # first direction
            pose = 0  # first pose
            # by default, will use default palettes, without having any info
            #  supplied probably won't matter, but just in case, use the
            #  first frame of palette
            frame = 0

        if style in manifest_images:
            images = manifest_images[style]
        elif style == "default":
            images = [[]]  # use defaults
        else:
            # FIXME: English
            raise AssertionError(
                f"received call to get_representative_image()" + ' ' +
                "with unknown style {style}"
            )

        return_images = []
        i = 0
        for image in images:
            animationkeys = list(self.animations.keys())
            if "$schema" in animationkeys:
                animationkeys.remove("$schema")
            animation = animationkeys[0]  # default to first image here
            if len(image) > 0 and image[0] != "":
                animation = image[0]

            direction = list(self.animations[animation].keys())[
                0]  # default: first direction
            if len(image) > 1 and image[1] != "":
                direction = image[1]

            pose = image[2] if len(image) > 2 else 0  # default: #first pose
            # defaults to the defaults determined by get_image
            palette = image[3] if len(image) > 3 else []
            # default to the first frame of timed palette
            frame = image[4] if len(image) > 4 else 0
            # default to the sprite name and style
            filename = image[5] if len(image) > 5 else \
                common.filename_scrub(
                    "-".join([sprite_save_name, style, str(i)]) + ".png")
            i = i + 1
            return_images.append((filename, self.get_image(
                animation, direction, pose, palette, frame)[0]))

        # should return a list of tuples of the form (filename, PIL Image)
        return return_images

    def save_as(self, filename="", gameName=""):
        _, file_extension = os.path.splitext(filename)
        if file_extension.lower() == ".4bpp":
            return self.save_as_binary(filename)
        if file_extension.lower() == ".png":
            return self.save_as_PNG(filename)
        if file_extension.lower() == ".rdc":
            return self.save_as_RDC(filename)
        if file_extension.lower() == ".zhx":
            return self.save_as_ZHX(filename, gameName)
        if file_extension.lower() == ".zspr":
            return self.save_as_ZSPR(filename)
        # tk.messagebox.showerror(
        #     "ERROR",
        #     f"Did not recognize file type \"{file_extension}\""
        # )
        return False

    def save_as_binary(self, filename):
        write_buffer = bytearray()
        write_buffer.extend(self.get_binary_sprite_sheet())
        with open(filename, "wb") as FOURbpp_file:
            FOURbpp_file.write(write_buffer)
        return True

    def save_as_PNG(self, filename):
        master_image = self.get_master_PNG_image()
        master_image.save(filename, "PNG")
        return True

    def save_as_ZHX(self, filename="", gameName="", paletteID=""):
        filename = os.path.splitext(filename)[0]
        slug = self.metadata["sprite.name"].replace(' ', '-').lower()
        if filename == "":
            filename = os.path.join(".", f"{slug}.zhx")
        temporary_zhx_directory = tempfile.mkdtemp()
        zhxLines = []
        zhxLines.append("---")
        zhxLines.append("# ZHX manifest file")
        zhxLines.append("# https://github.com/spannerisms/ZippedHacks")
        zhxLines.append("")
        zhxObj = {}
        zhxObj["meta"] = {
          "game": gameName,
          "package": {
            "name": self.metadata["sprite.name"],
            "author": self.metadata["author.name"]
          }
        }
        zhxObj["included"] = [[]]
        zhxObj["meta"]["package"]["name_rom"] = zhxObj["meta"]["package"]["name"].upper()
        zhxObj["meta"]["package"]["author_rom"] = self.metadata["author.name-short"]
        # print(
        #   "\n".join(zhxLines) +
        #   yaml.dump(zhxObj, sort_keys=False, indent=2)
        # )

        print(f"Saving '{slug}.4bpp'")
        self.save_as(os.path.join(temporary_zhx_directory, f"{slug}.4bpp"))
        zhxObj["included"][0].append(
          {
            "file": f"{slug}.4bpp",
            "read": "raw",
            "type": "PlayerGraphics"
          }
        )

        print(f"Exporting binary palette to: '{slug}.pal'")
        # filename, gameName, paletteID, fmt
        self.export_palette(
          os.path.join(temporary_zhx_directory, f"{slug}.pal"),
          gameName,
          paletteID,
          "binary"
        )
        self.export_palette(
          os.path.join(temporary_zhx_directory, f"{slug}.palette-aspr"),
          gameName,
          paletteID,
          "aspr"
        )
        self.export_palette(
          os.path.join(temporary_zhx_directory, f"{slug}.palette-gimp"),
          gameName,
          paletteID,
          "gimp"
        )
        zhxObj["included"][0].append(
          {
            "file": f"{slug}.pal",
            "read": "raw",
            "type": "PlayerPalette"
          }
        )

        print(f"Saving '{slug}.png'")
        self.save_as(os.path.join(temporary_zhx_directory, f"{slug}.png"))
        zhxObj["included"][0].append(
          {
            "file": f"{slug}.png",
            "type": "PlayerPreview"
          }
        )

        with(open(os.path.join(temporary_zhx_directory, f"{slug}.yml"), "w+")) as manifestFile:
          manifestFile.write("\n".join(zhxLines))
          manifestFile.write(yaml.dump(zhxObj, sort_keys=False, indent=2))
        print(f"Writing '{slug}.yml'")

        make_archive(f"{slug}", "zip", temporary_zhx_directory)
        print(f"Made archive '{slug}.zip'; ren to '{filename}.zhx'")
        move(f"{slug}.zip", f"{filename}.zhx")

        return True

    def save_as_ZSPR(self, filename):
        # check to see if the functions exist (e.g. crashes hard if used
        #  on Samus)
        if hasattr(self, "get_binary_sprite_sheet") and \
                hasattr(self, "get_binary_palettes"):
            sprite_sheet = self.get_binary_sprite_sheet()
            palettes = self.get_binary_palettes()
            HEADER_STRING = b"ZSPR"
            VERSION = 0x01
            SPRITE_TYPE = 0x01  # this format has "1" for the player sprite
            RESERVED_BYTES = b'\x00\x00\x00\x00\x00\x00'
            QUAD_BYTE_NULL_CHAR = b'\x00\x00\x00\x00'
            DOUBLE_BYTE_NULL_CHAR = b'\x00\x00'
            SINGLE_BYTE_NULL_CHAR = b'\x00'

            write_buffer = bytearray()

            write_buffer.extend(HEADER_STRING)
            write_buffer.extend(common.as_u8(VERSION))
            checksum_start = len(write_buffer)
            write_buffer.extend(QUAD_BYTE_NULL_CHAR)
            sprite_sheet_pointer = len(write_buffer)
            write_buffer.extend(QUAD_BYTE_NULL_CHAR)
            write_buffer.extend(common.as_u16(len(sprite_sheet)))
            palettes_pointer = len(write_buffer)
            write_buffer.extend(QUAD_BYTE_NULL_CHAR)
            write_buffer.extend(common.as_u16(len(palettes)))
            write_buffer.extend(common.as_u16(SPRITE_TYPE))
            write_buffer.extend(RESERVED_BYTES)
            write_buffer.extend(
                self.metadata["sprite.name"].encode('utf-16-le'))
            write_buffer.extend(DOUBLE_BYTE_NULL_CHAR)
            write_buffer.extend(
                self.metadata["author.name"].encode('utf-16-le'))
            write_buffer.extend(DOUBLE_BYTE_NULL_CHAR)
            write_buffer.extend(
                self.metadata["author.name-short"].encode('ascii'))
            write_buffer.extend(SINGLE_BYTE_NULL_CHAR)
            write_buffer[sprite_sheet_pointer:sprite_sheet_pointer +
                         4] = common.as_u32(len(write_buffer))
            write_buffer.extend(sprite_sheet)
            write_buffer[palettes_pointer:palettes_pointer +
                         4] = common.as_u32(len(write_buffer))
            write_buffer.extend(palettes)

            checksum = (sum(write_buffer) + 0xFF + 0xFF) % 0x10000
            checksum_complement = 0xFFFF - checksum

            write_buffer[checksum_start:checksum_start +
                         2] = common.as_u16(checksum)
            write_buffer[checksum_start + 2:checksum_start +
                         4] = common.as_u16(checksum_complement)

            with open(filename, "wb") as zspr_file:
                zspr_file.write(write_buffer)

            return True  # report success to caller
        return False  # report failure to caller

    def save_as_RDC(self, filename):
        raw_author_name = self.metadata["author.name-short"]
        author = raw_author_name.encode(
            'utf-8') if raw_author_name else bytes()
        HEADER_STRING = b"RETRODATACONTAINER"
        VERSION = 0x01

        blocks_with_type = self.get_rdc_meta_data_block() + self.get_rdc_export_blocks()
        number_of_blocks = len(blocks_with_type)

        preample_length = len(HEADER_STRING) + 1
        block_list_length = 4 + number_of_blocks * 8
        author_field_length = len(author) + 1
        block_offset = preample_length + block_list_length + author_field_length

        with open(filename, "wb") as rdc_file:
            rdc_file.write(HEADER_STRING)
            rdc_file.write(common.as_u8(VERSION))
            rdc_file.write(common.as_u32(number_of_blocks))
            for block_type, block in blocks_with_type:
                rdc_file.write(common.as_u32(block_type))
                rdc_file.write(common.as_u32(block_offset))
                block_offset += len(block)
            rdc_file.write(author)
            rdc_file.write(common.as_u8(0))

            for _, block in blocks_with_type:
                rdc_file.write(block)

        return True  # indicate success to caller

    def get_rdc_meta_data_block(self):
        title_name = self.metadata["sprite.name"]
        author_name = self.metadata["author.name"]
        data = json.dumps(
            {
                "title": title_name,
                "author": author_name,
                "game": "snes/metroid3",
                "spriteType": 1
            },
            separators=(',', ':')
        ).encode('utf-8')

        META_DATA_BLOCK_TYPE = 0
        return [
            (
                META_DATA_BLOCK_TYPE,
                bytearray(common.as_u32(len(data))) + data
            )
        ]

    def get_master_PNG_image(self):
        return self.layout.export_all_images_to_PNG(
            self.images,
            self.master_palette,
            self.filename
        )

    def import_module(self, module_name):
        # TODO: factor this out to a common source file
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError as err:
            raise AssertionError(f"ModuleNotFoundError in spritelib.py: {err}")


def main():
    print(f"Called main() on utility library {__file__}")

if __name__ == "__main__":
    main()
