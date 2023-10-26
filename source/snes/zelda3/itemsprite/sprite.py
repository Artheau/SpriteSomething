import itertools
import json
import os
import io
import re
from string import ascii_uppercase, digits
from PIL import Image
from source.meta.common import common
from source.meta.classes.spritelib import SpriteParent

# This module assumes we are replacing the triforce piece sprite by default.
# The "standing" 4bpp data location used is unclaimed space immediately after
# the power star gfx in ROM. But in theory we can configure arbitrary
# graphics replacements for any item.
# 
# See the documentation at:
# https://github.com/KatDevsGames/z3randomizer/blob/master/itemdatatables.asm
# https://github.com/KatDevsGames/z3randomizer/blob/master/data/customitems.png

CHEST_SPRITE_POINTERS = 0xA2C600
STANDING_SPRITE_POINTERS = 0xA2C800
CHEST_SPRITE_POINTER = 0x0060
STANDING_SPRITE_POINTER = 0x1220
SPRITE_PAL_1 = [0x7FFF, 0x08D9, None, None, 0x14A5, None, None, 0x0000, 0x7FFF, 0x1979, 0x14B6, 0x39DC, 0x14A5, 0x66F7, 0x45EF] # Red
SPRITE_PAL_2 = [0x7FFF, None, None, None, 0x14A5, None, None, 0x0000, 0x7FFF, 0x5A1F, 0x55AA, 0x76B2, 0x14A5, 0x2ADF, 0x1597] # Blue
SPRITE_PAL_4 = [0x7FFF, 0x319B, 0x1596, 0x369E, 0x14A5, 0x7E56, 0x65CA, 0x0000, 0x7FFF, 0x0CD9, 0x1A49, 0x3B53, 0x14A5, 0x1F5F, 0x1237] # Green
PALETTE_TABLE = [None, SPRITE_PAL_1, SPRITE_PAL_2, None, SPRITE_PAL_4, None, None, None]
CUSTOM_PALETTE_ADDRESS = 0x9BB260
PALETTE_CONTROL_CHEST = [None, 0, 17, 51, 34] # Map palette index to control pixel index
PALETTE_CONTROL_STANDING = [None, 1, 18, 52, 35]
# ROW_INDEX_MAP [1, 2, 4, 3]
PALETTE_ADDRESSES = [None, 0xD218, 0xD272, CUSTOM_PALETTE_ADDRESS & 0xFFFF, 0xD236]

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.load_plugins()

        # Icons are sideview, so only left/right direction buttons should show
        self.overhead = False

        self.item_sprite_globals = {}
        self.images = {}
        self.chest_wide = True
        self.standing_wide = True
        self.chest_palette_index = 4
        self.standing_palette_index = 4
        self.palette_address = 0x9BD272
        self.item_index = 0x6C # Triforce Piece
        self.item_sprite_globals["palettes"] = {
          "1": [
            (255, 255, 255),
            (206, 49, 16),
            (None, None, None),
            (None, None, None),
            (41, 41, 41),
            (255, 206, 33),
            (255, 115, 49),
            (0, 0, 0),
            (255, 255, 255),
            (206, 90, 49),
            (181, 41, 41),
            (231, 115, 115),
            (41, 41, 41),
            (189, 189, 206),
            (123, 123, 140)
          ],
          "2": [
            (255, 255, 255),
            (None, None, None),
            (None, None, None),
            (None, None, None),
            (41, 41, 41),
            (None, None, None),
            (None, None, None),
            (0, 0, 0),
            (255, 255, 255),
            (255, 132, 181),
            (82, 107, 173),
            (148, 173, 239),
            (41, 41, 41),
            (255, 181, 82),
            (184, 96, 40)
          ],
          "4": [
            (255, 255, 255),
            (222, 99, 99),
            (181, 99, 41),
            (247, 165, 107),
            (41, 41, 41),
            (181, 148, 255),
            (82, 115, 206),
            (0, 0, 0),
            (255, 255, 255),
            (206, 49, 24),
            (74, 148, 49),
            (156, 214, 115),
            (41, 41, 41),
            (255, 214, 57),
            (189, 140, 33)
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
        self.palette_address = rom.read_from_snes_address(0xA2BE00+(self.item_index*2), "2")[0]
        self.standing_wide = bool(rom.read_from_snes_address(0xA2BA00+self.item_index, 1))
        self.chest_wide = bool(rom.read_from_snes_address(0xA2BA00+self.item_index, 1))

        pixel_data = rom.bulk_read_from_snes_address(0xA28060,0x40)
        pixel_data.extend(rom.bulk_read_from_snes_address(0xA28260,0x40))
        standing_pixel_data = rom.bulk_read_from_snes_address(0xA29220,0x40)
        standing_pixel_data.extend(rom.bulk_read_from_snes_address(0xA29420,0x40))
        # Duplicate the chest sprite data if no standing sprite
        if any(standing_pixel_data):
            pixel_data.extend(standing_pixel_data)
        else:
            pixel_data.extend(pixel_data[:])

        chest_palette_index = rom.read_from_snes_address(0xA2BC00+self.item_index, 1)
        if not (chest_palette_index & 0x80):
            self.chest_palette_index = chest_palette_index
            chest_palette_data = None
            # chest_palette_data = PALETTE_TABLE[chest_palette_index]
            self.item_sprite_globals["palettes"]["3"] = [(0, 0, 0, 0)] * 15
        else:
            self.chest_palette_index = 3
            chest_palette_data = [None] * 7
            chest_palette_data.extend(rom.read_from_snes_address((self.palette_address | 0x9B0000), "22222222"))
            # chest_palette_data_converted = [int.from_bytes(chest_palette_data[i:i+2], byteorder='little') \
            #                                                 for i in range(0,len(chest_palette_data),2)]
            self.item_sprite_globals["palettes"]["3"] = common.convert_555_to_rgb(chest_palette_data_converted)

        standing_palette_index = rom.read_from_snes_address(0xA2BD00+self.item_index, 1)
        if not (standing_palette_index & 0x80):
            self.standing_palette_index = standing_palette_index
            standing_palette_data = None
            # standing_palette_data = PALETTE_TABLE[standing_palette_index]
            self.item_sprite_globals["palettes"]["3"] = [(0, 0, 0, 0)] * 15
        else:
            self.standing_palette_index = 3
            standing_palette_data = [None] * 7
            standing_palette_data.extend(rom.read_from_snes_address((self.palette_address | 0x9B0000), "22222222"))
            # standing_palette_data_converted = [int.from_bytes(standing_palette_data[i:i+2], byteorder='little') \
            #                                                 for i in range(0,len(standing_palette_data),2)]
            self.item_sprite_globals["palettes"]["3"] = common.convert_555_to_rgb(standing_palette_data_converted)

        palette_data = chest_palette_data if chest_palette_data else standing_palette_data
        self.import_from_binary_data(pixel_data, palette_data)

    def import_from_binary_data(self,pixel_data,palette_data):
        base_master_palette = construct_base_palette_block()
        if palette_data:
            converted_palette = [int.from_bytes(_palette_data[i:i+2], byteorder='little') \
                                                    for i in range(0,len(standing_palette_data),2)]
            base_master_palette.extend(converted_palette)
        else:
            base_master_palette.extend([(0, 0, 0, 0)] * 15)
        # Set palette control pixels
        base_master_palette[PALETTE_CONTROL_CHEST[self.chest_palette_index]] = (0, 0, 0)
        base_master_palette[PALETTE_CONTROL_STANDING[self.standing_palette_index]] = (0, 0, 0)
        self.master_palette = base_master_palette

        palette_block = Image.new('RGBA',(17,4),0)
        palette_block.putdata(self.master_palette)
        self.images["palette_block"] = palette_block

        tile_chunks = [pixel_data[i * 0x20:(i + 1) * 0x20] for i in range((len(pixel_data) + 0x20 - 1) // 0x20 )]
        chest_image = Image.new("P",(16,16),0)
        for i, position in [
            (0, (0,0)),
            (1, (8,0)),
            (2, (0,8)),
            (3, (8,8))
        ]:
            raw_tile = tile_chunks[i]
            pastable_tile = common.image_from_bitplanes(raw_tile)
            chest_image.paste(pastable_tile,position)
        this.images["item_sprite_receipt"] = chest_image
        standing_image = Image.new("P",(16,16),0)
        for i, position in [
            (4, (0,0)),
            (5, (8,0)),
            (6, (0,8)),
            (7, (8,8))
        ]:
            raw_tile = tile_chunks[i]
            pastable_tile = common.image_from_bitplanes(raw_tile)
            standing_image.paste(pastable_tile,position)
        this.images["item_sprite_standing"] = standing_image

    def inject_into_ROM(self, spiffy_dict, rom):
        # TODO check rom version?

        #this'll check VT rando Tournament Flag
        tournament_flag = (float(rom.get_size_in_MB()) > 1.5) and (rom.read(0x180213, 2) == 1)
        if not tournament_flag:
            chest = this.images["item_sprite_receipt"]
            standing = this.images["item_sprite_standing"]
            palette_block = this.images["palette_block"]
            chest_4bpp = common.convert_to_4bpp(chest, (0,0), (0,0,16,16), None)
            standing_4bpp = common.convert_to_4bpp(standing, (0,0), (0,0,16,16), None)

            same_sprite = chest == standing
            self.chest_wide = is_wide(chest)
            self.standing_wide = is_wide(standing)
            self.chest_palette_index, self.standing_palette_index = get_palette_indexes(palette_block)
            self.palette_address = PALETTE_ADDRESSES[self.chest_palette_index]

            write_table_data(palette_block, same_sprite, rom)
            rom.bulk_write_to_snes_address(0xA28060, chest_4bpp[:0x40], 0x40)
            rom.bulk_write_to_snes_address(0xA28260, chest_4bpp[0x40:], 0x40)
            if not same_sprite:
                rom.bulk_write_to_snes_address(0xA29220, standing_4bpp[:0x40], 0x40)
                rom.bulk_write_to_snes_address(0xA29420, standing_4bpp[0x40:], 0x40)
        else:
            # FIXME: English
            raise AssertionError(f"Cannot inject into a Race/Tournament ROM!")

        return rom

    def construct_base_palette_block():
        '''
        Constructs the "base" palette block including two columns of white pixels on the
        left side. The final, 15-color "custom" palette must be appended to the end.
        '''
        palette_block = []

        palette_block.extend([(255, 255, 255), (255, 255, 255)])
        for c in SPRITE_PALETTE_1:
            palette_block.append(common.convert_555_to_rgb(c))
        palette_block.extend([(255, 255, 255), (255, 255, 255)])
        for c in SPRITE_PALETTE_2:
            palette_block.append(common.convert_555_to_rgb(c))
        palette_block.extend([(255, 255, 255), (255, 255, 255)])
        for c in SPRITE_PALETTE_4:
            palette_block.append(common.convert_555_to_rgb(c))
        palette_block.extend([(255, 255, 255), (255, 255, 255)])

        return palette_block

    def is_wide(sprite_image):
        blank = True
        right_side = sprite_image.crop(8, 0, 0, 0)
        right_side_pixels = list(right_side.getdata())
        for p in right_side_pixels:
            if p != right_side_pixels[0]:
                blank = False

        return not blank

    def get_palette_indexes(palette_block):
        palette_block_pixels = list(palette_block.getdata())
        chest_idx = 4
        standing_idx = 4

        while chest_idx > 0:
            if palette_block_pixels[PALETTE_CONTROL_CHEST[i]] == (0, 0, 0):
                break
            else:
                 chest_idx -= 1
        while standing_idx > 0:
            if palette_block_pixels[PALETTE_CONTROL_STANDING[i]] == (0, 0, 0):
                break
            else:
                 chest_idx -= 1

        return (chest_idx, standing_idx)

    def write_table_data(palette_block, same_sprite, rom):
        if same_sprite:
            # Width
            width = 2 if self.chest_wide else 0
            rom.write_to_snes_address(0xA2BA00+self.item_index, width, 1)
            rom.write_to_snes_address(0xA2BB00+self.item_index, width, 1)
            # Palette index
            palette_index = self.chest_palette_index if self.chest_palette_index != 3 else 0x80
            rom.write_to_snes_address(0xA2BC00+self.item_index, palette_index, 1)
            rom.write_to_snes_address(0xA2BD00+self.item_index, palette_index, 1)
            # Decompressed sprite pointer
            rom.write_to_snes_address(0xA2C600+(self.item_index*2), 0x0060, 2)
            rom.write_to_snes_address(0xA2C800+(self.item_index*2), 0x0060, 2)
        else:
            chest_width = 2 if self.chest_wide else 0
            standing_width = 2 if self.standing_wide else 0
            rom.write_to_snes_address(0xA2BA00+self.item_index, chest_width, 1)
            rom.write_to_snes_address(0xA2BB00+self.item_index, standing_width, 1)
            chest_palette_index = self.chest_palette_index if self.chest_palette_index != 3 else 0x80
            standing_palette_index = self.standing_palette_index if self.standing_palette_index != 3 else 0x80
            rom.write_to_snes_address(0xA2BC00+self.item_index, chest_palette_index, 1)
            rom.write_to_snes_address(0xA2BD00+self.item_index, standing_palette_index, 1)
            rom.write_to_snes_address(0xA2C600+(self.item_index*2), 0x0060, 2)
            rom.write_to_snes_address(0xA2C800+(self.item_index*2), 0x1220, 2)

        # Palette address
        rom.write_to_snes_address(0xA2BE00+(self.item_index*2), self.palette_address, 2)
        if self.palette_address == CUSTOM_PALETTE_ADDRESS & 0xFFFF:
            custom_palette = list(palette_block.getdata())[-8:]
            custom_palette_converted = common.convert_to_555(custom_palette)
            rom.write_to_snes_address(CUSTOM_PALETTE_ADDRESS, custom_palette_converted, 8*"2")

