#Written by Artheau
#in March, 2019
#while sipping flavorful coffee loudly

#applies bugfixes to the rom
#blanks out all Samus tiles!  (Pac Man mode)
#spreads out the tilemaps to create a "canvas" to paint on.

#TODO: factor out the mutual hex processing code from this file and util.py

import argparse
import os
import struct

import romload
from constants import *

rom = None

def process_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom",
                        dest=ROM_FILENAME_ARG_KEY,
                        help="Location of the rom file; e.g. /my_dir/sm_orig.sfc",
                        metavar="<rom_filename>",
                        default='sm_orig.sfc')
    
    command_line_args = vars(parser.parse_args())

    return command_line_args


def blank_all_samus_tiles():
    blank_tile = bytes(8*[0x00,0xFF]+16*[0x00]) #technically this is Samus's yellow color right now (Pac Man mode)
    for addr in range(SAMUS_TILES_START,SAMUS_TILES_END,TILESIZE):
        rom[addr:addr+TILESIZE] = blank_tile


def write_new_tilemaps():
    current_addr = SAMUS_TILEMAPS_START

    upper_map_addresses = {}
    tilemaps_to_create = get_raw_upper_tilemaps()
    for key in tilemaps_to_create:
        tilemap = tilemaps_to_create[key]
        tilemap_size = len(tilemap)
        rom[current_addr:current_addr+tilemap_size] = bytes(tilemap)
        upper_map_addresses[key] = convert_to_ram_address(current_addr) - 0x920000
        current_addr += tilemap_size
        if current_addr > SAMUS_TILEMAPS_END:
            raise AssertionError("Made too many tilemaps -- exceeded ROM tilemap allocation")

    lower_map_addresses = {}
    tilemaps_to_create = get_raw_lower_tilemaps()
    for key in tilemaps_to_create:
        tilemap = tilemaps_to_create[key]
        tilemap_size = len(tilemap)
        rom[current_addr:current_addr+tilemap_size] = bytes(tilemap)
        lower_map_addresses[key] = convert_to_ram_address(current_addr) - 0x920000
        current_addr += tilemap_size
        if current_addr > SAMUS_TILEMAPS_END:
            raise AssertionError("Made too many tilemaps -- exceeded ROM tilemap allocation")

    return upper_map_addresses, lower_map_addresses


def get_raw_upper_tilemaps():
    #TODO: More tilemaps
    tilemaps = {}

    this_map = [0x01,0x00]  #one tile in map
    this_map.extend([0xF3,0x01,0xF0,0x00,0x28])

    tilemaps['test_1x1'] = this_map.copy()

    this_map = [0x01,0x00]  #one tile in map
    this_map.extend([0xF3,0xC3,0xF0,0x00,0x28])

    tilemaps['test_2x2'] = this_map.copy()

    this_map = [0x03,0x00]  #three tiles in map
    this_map.extend([0xF3,0xC3,0xF0,0x00,0x28])
    this_map.extend([0x03,0x00,0xF0,0x02,0x28])
    this_map.extend([0x03,0x00,0xF8,0x03,0x28])

    tilemaps['test_2x3'] = this_map.copy()

    this_map = [0x06,0x00]  #six tiles in map
    this_map.extend([0xF3,0xC3,0xF0,0x00,0x28])
    this_map.extend([0x03,0x00,0xF0,0x02,0x28])
    this_map.extend([0x03,0x00,0xF8,0x03,0x28])
    this_map.extend([0xF3,0x01,0x00,0x04,0x28])
    this_map.extend([0xFB,0x01,0x00,0x05,0x28])
    this_map.extend([0x03,0x00,0x00,0x06,0x28])

    tilemaps['test_3x3'] = this_map.copy()
    
    return tilemaps

def get_raw_lower_tilemaps():
    #TODO: More tilemaps
    tilemaps = {}

    this_map = [0x01,0x00]  #one tile in map
    this_map.extend([0xF3,0x01,0x00,0x08,0x28])

    tilemaps['test_1x1'] = this_map.copy()

    this_map = [0x01,0x00]  #one tile in map
    this_map.extend([0xF3,0xC3,0x00,0x08,0x28])

    tilemaps['test_2x2'] = this_map.copy()

    this_map = [0x06,0x00]  #six tiles in map
    this_map.extend([0xF3,0xC3,0x00,0x08,0x28])
    this_map.extend([0x03,0x00,0x00,0x0A,0x28])
    this_map.extend([0x03,0x00,0x08,0x0B,0x28])
    this_map.extend([0xF3,0x01,0x10,0x0C,0x28])
    this_map.extend([0xFB,0x01,0x10,0x0D,0x28])
    this_map.extend([0x03,0x00,0x10,0x0E,0x28])

    tilemaps['test_3x3'] = this_map.copy()

    this_map = [0x06,0x00]  #six tiles in map
    this_map.extend([0xF3,0xC3,0x00,0x08,0x28])
    this_map.extend([0x03,0x00,0x00,0x0A,0x28])
    this_map.extend([0x03,0x00,0x08,0x0B,0x28])
    this_map.extend([0xF3,0xC3,0x10,0x0C,0x28])
    this_map.extend([0x03,0x00,0x10,0x0E,0x28])
    this_map.extend([0x03,0x00,0x18,0x0F,0x28])

    tilemaps['test_4x3'] = this_map.copy()
    

    return tilemaps

def assign_new_tilemaps(upper_map_addresses, lower_map_addresses):
    animation_number = 0x00
    [upper_offset] = get_indexed_values(UPPER_TILEMAP_TABLE_POINTER,animation_number,0x02,'2')
    [lower_offset] = get_indexed_values(LOWER_TILEMAP_TABLE_POINTER,animation_number,0x02,'2')

    animation_upper_tilemap_list = TILEMAP_TABLE + 2 * upper_offset
    rom_upper_tilemap_pointer_location = convert_to_rom_address(animation_upper_tilemap_list)

    map_to_insert = upper_map_addresses['test_2x3']
    msb = map_to_insert // 0x100
    lsb = map_to_insert % 0x100

    rom[rom_upper_tilemap_pointer_location:rom_upper_tilemap_pointer_location+2] = bytes([lsb,msb])

    animation_lower_tilemap_list = TILEMAP_TABLE + 2 * lower_offset
    rom_lower_tilemap_pointer_location = convert_to_rom_address(animation_lower_tilemap_list)

    map_to_insert = lower_map_addresses['test_4x3']
    msb = map_to_insert // 0x100
    lsb = map_to_insert % 0x100

    rom[rom_lower_tilemap_pointer_location:rom_lower_tilemap_pointer_location+2] = bytes([lsb,msb])


def convert_to_rom_address(snes_addr):
    #convert from memory address to ROM address (lorom 0x80)
    bank = snes_addr // 0x10000 - 0x80
    offset = (snes_addr % 0x10000) - 0x8000

    if offset < 0x0000 or bank < 0x00:
        raise AssertionError(f"Function convert_to_rom_address() called on {pretty_hex(snes_addr)}, but this is not a valid SNES address.")
    
    new_address = bank*0x8000 + offset

    return new_address

def convert_to_ram_address(rom_addr):
    #convert from ROM address to memory address (lorom 0x80)
    bank = rom_addr // 0x8000
    offset = rom_addr % 0x8000

    if bank < 0x00:
        raise AssertionError(f"Function convert_to_ram_address() called on {pretty_hex(rom_addr)}, but this is not a valid SNES address.")
    
    new_address = (bank+0x80)*0x10000 + (offset+0x8000)

    return new_address


def get_indexed_values(base,index,entry_size,encoding):
    #returns an unpacked list of the values specified by the enconding at base[index], assuming array entries are entry_size long
    beginning_of_entry = convert_to_rom_address(base+index*entry_size)
    returnvalue = []
    for code in encoding:
        bytes_to_get = int(code)

        extracted_bytes = rom[beginning_of_entry:beginning_of_entry+bytes_to_get]


        if bytes_to_get == 1:
            unpack_code = 'B'
        elif bytes_to_get == 2:
            unpack_code = 'H'
        elif bytes_to_get == 3:
            unpack_code = 'L'
            extracted_bytes += b'\x00'    #no native 3-byte unpacking format in Python; this is a workaround to pad the 4th byte
        else:
            raise AssertionError(f"get_indexed_values() called with encoding {encoding}, contains invalid code {code}.")

        extracted_value = struct.unpack('<'+unpack_code,extracted_bytes)[0]           #the '<' forces it to read as little-endian
        returnvalue.append(extracted_value)
        beginning_of_entry += bytes_to_get
    return returnvalue


def main():
    global rom

    command_line_args = process_command_line_args()
    rom = romload.load_rom_contents(command_line_args[ROM_FILENAME_ARG_KEY])

    blank_all_samus_tiles()

    upper_map_addresses, lower_map_addresses = write_new_tilemaps()

    assign_new_tilemaps(upper_map_addresses, lower_map_addresses)

    #the file saves automatically because it is an mmap (see romload.py)
    

if __name__ == "__main__":
    main()

