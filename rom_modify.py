#Written by Artheau
#in March, 2019
#while sipping flavorful coffee loudly

#applies bugfixes to the rom
#blanks out all Samus tiles!  (Pac Man mode)
#rebuilt the tilemaps to create a "canvas" to paint on.

#TODO: factor out the mutual hex processing code from this file and util.py

import argparse
import os
import struct
import csv
from PIL import Image

import romload
import tilemaps
from constants import *

rom = None
filemap = None






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
    return tilemaps.upper_tilemaps

def get_raw_lower_tilemaps():
    return tilemaps.lower_tilemaps


def assign_new_tilemaps(upper_map_addresses, lower_map_addresses):
    #TODO: Re-factor this to avoid doubled-up code
    animation_number_list = set([animation_number for (animation_number,timeline_number) in filemap.keys()])
    for animation_number in animation_number_list:
        max_timeline = max([timeline_number for (this_animation_number,timeline_number) in filemap.keys() if this_animation_number == animation_number])
        
        upper_tilemap_list = []
        lower_tilemap_list = []
        for t in range(max_timeline+1):
            if (animation_number,t) not in filemap:   #as will be the case for control codes
                upper_tilemap_list.extend([0x00,0x00])
                lower_tilemap_list.extend([0x00,0x00])
            else:
                upper_address_to_insert = upper_map_addresses[filemap[(animation_number,t)]['upper_map']]
                msb = upper_address_to_insert // 0x100
                lsb = upper_address_to_insert % 0x100
                upper_tilemap_list.extend([lsb,msb])
                
                lower_address_to_insert = lower_map_addresses[filemap[(animation_number,t)]['lower_map']]
                msb = lower_address_to_insert // 0x100
                lsb = lower_address_to_insert % 0x100
                lower_tilemap_list.extend([lsb,msb])

        [upper_offset] = get_indexed_values(UPPER_TILEMAP_TABLE_POINTER,animation_number,0x02,'2')
        [lower_offset] = get_indexed_values(LOWER_TILEMAP_TABLE_POINTER,animation_number,0x02,'2')

        rom_upper_tilemap_array = convert_to_rom_address(TILEMAP_TABLE + 2 * upper_offset)
        rom[rom_upper_tilemap_array:rom_upper_tilemap_array+len(upper_tilemap_list)] = bytes(upper_tilemap_list)

        rom_lower_tilemap_array = convert_to_rom_address(TILEMAP_TABLE + 2 * lower_offset)
        rom[rom_lower_tilemap_array:rom_lower_tilemap_array+len(lower_tilemap_list)] = bytes(lower_tilemap_list)






def convert_file_to_VRAM_data(filename):
    image = Image.open(filename)
    pixels = image.load()
    palette = load_palette_from_file()             #this line placed here so that the palette can be switched per file
    #TODO: Use the palette and the image file to reverse engineer the indices

    row1,row2 = None,None
    return row1,row2


def load_palette_from_file(filename = "resources/samus_palette.tpl"):
    palette = []
    with open(filename, 'rb') as file:
        _ = file.read(4)       #skip "TPL" + null (4 bytes total)
        raw_file = file.read()
    for i in range(0,len(raw_file),3):
        red = int(raw_file[i])
        green = int(raw_file[i+1])
        blue = int(raw_file[i+2])
        palette.append((red,green,blue))
    print(palette)
    return palette




def load_filemap(filename='resources/filemap.csv'):
    filemap = {}
    with open(filename, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        next(spamreader)             #skip header
        for row in spamreader:
            animation_number = int(row[0])
            pose_number = int(row[2])
            timeline_number = int(row[3])
            upper_map = row[4]
            upper_file = row[5]
            lower_map = row[6]
            lower_file = row[7]

            filemap[(animation_number,timeline_number)] = { 'pose_number': pose_number,
                                                        'upper_map': upper_map,
                                                        'upper_file': upper_file,
                                                        'lower_map': lower_map,
                                                        'lower_file': lower_file}
    return filemap

def process_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom",
                        dest=ROM_FILENAME_ARG_KEY,
                        help="Location of the rom file; e.g. /my_dir/sm_orig.sfc",
                        metavar="<rom_filename>",
                        default='sm_orig.sfc')
    
    command_line_args = vars(parser.parse_args())

    return command_line_args

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
    global filemap

    command_line_args = process_command_line_args()
    rom = romload.load_rom_contents(command_line_args[ROM_FILENAME_ARG_KEY])
    filemap = load_filemap()

    blank_all_samus_tiles()

    upper_map_addresses, lower_map_addresses = write_new_tilemaps()

    assign_new_tilemaps(upper_map_addresses, lower_map_addresses)

    #the file saves automatically because it is an mmap (see romload.py)

    #TODO: remove
    load_palette_from_file()
    

if __name__ == "__main__":
    main()

