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
import numpy as np
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






def convert_file_to_VRAM_data(filename,lower=False):
    #TODO: Don't trust that the image is correctly sized
    #TODO: Non-rectangular templates
    image = Image.open(filename)
    pixels = image.load()
    palette = load_palette_from_file()             #this line placed here so that the palette can be switched per file
    
    reverse_palette = {(r,g,b,0xFF):index for (index,(r,g,b)) in enumerate(palette)}
    image_colors = [color for (count,color) in image.getcolors()]

    for (r,g,b,a) in image_colors:
        if a == 0:
            reverse_palette[(r,g,b,a)] = 0      #force all the transparent colors to index 0

    #audit the colors in the image to make sure we CAN translate them all using the palette
    for color in image_colors:
        if color not in reverse_palette:
            raise AssertionError(f"color {color} is present in image {filename}, but it is not in the corresponding palette")

    image_raw_pixels = list(image.getdata())
    rows, cols = image.size

    #sadly this next data structure will need to be indexed by index_pixels[row][col],
    # which is opposite the math intution (i.e. must use index_pixels[y_coord][x_coord])
    index_pixels = np.reshape(list(map(lambda x: reverse_palette[x], image_raw_pixels)), (cols,rows))
    
    #####now flatten the image out in the 4bpp tile format

    row1,row2 = [],[]

    #big tiles first
    for y in range(0,rows-8,16):
        for x in range(0,cols-8,16):
            row1.append(extract_vram_tile(index_pixels[y  :y+8 ,x  :x+8 ]))  #top left
            row1.append(extract_vram_tile(index_pixels[y  :y+8 ,x+8:x+16]))  #top right
            row2.append(extract_vram_tile(index_pixels[y+8:y+16,x  :x+8 ]))  #bottom left
            row2.append(extract_vram_tile(index_pixels[y+8:y+16,x+8:x+16]))  #bottom right
    #rightmost column if necessary
    if cols % 16 != 0:
        x = cols - (cols % 16)
        for y in range(0,rows-8,16):
            row1.append(extract_vram_tile(index_pixels[y  :y+8 ,x  :x+8 ]))  #top
            row2.append(extract_vram_tile(index_pixels[y+8:y+16,x  :x+8 ]))  #bottom
    #bottom row if necessary
    if rows % 16 != 0:
        y = rows - (rows % 16)
        for x in range(0,cols-8,16):
            row1.append(extract_vram_tile(index_pixels[y  :y+8 ,x  :x+8 ]))  #left
            row2.append(extract_vram_tile(index_pixels[y  :y+8 ,x+8:x+16]))  #right
    #bottom right corner, if necessary
    if rows % 16 != 0 and cols % 16 != 0:
        x = cols - (cols % 16)
        y = rows - (rows % 16)
        row1.append(extract_vram_tile(index_pixels[y  :y+8 ,x  :x+8 ]))
    
    #so there's this thing with row2 in the lower body section where they used the rightmost two tiles
    # for other stuff like cannon ports, so we need to stay out of there
    if lower and len(row2)//TILESIZE > 0x06:
        #move last tile from row2 up to row1
        row1.extend(row2[0x06*TILESIZE:])
        row2 = row2[:0x06*TILESIZE]


    if len(row1)//TILESIZE > 0x08 or len(row2)//TILESIZE > 0x08:
        raise AssertionError(f"Too many tiles created for {filename}")
    

    return row1,row2

def extract_vram_tile(tile):
    #pasting this again because my head explodes every time I try to do something with 4bpp
    # (this condition is not congenital)
    #from https://mrclick.zophar.net/TilEd/download/consolegfx.txt
    # [r0, bp1], [r0, bp2], [r1, bp1], [r1, bp2], [r2, bp1], [r2, bp2], [r3, bp1], [r3, bp2]
    # [r4, bp1], [r4, bp2], [r5, bp1], [r5, bp2], [r6, bp1], [r6, bp2], [r7, bp1], [r7, bp2]
    # [r0, bp3], [r0, bp4], [r1, bp3], [r1, bp4], [r2, bp3], [r2, bp4], [r3, bp3], [r3, bp4]
    # [r4, bp3], [r4, bp4], [r5, bp3], [r5, bp4], [r6, bp3], [r6, bp4], [r7, bp3], [r7, bp4]

    vram_dict = {}
    for bitplane in range(4):
        bitmask = 0x01 << bitplane
        for i,row in enumerate(tile.tolist()):
            vram_dict[(i,bitplane)] = 0
            for j,pixel in enumerate(row):
                vram_dict[(i,bitplane)] = (vram_dict[(i,bitplane)] << 1) + (1 if (pixel & bitmask != 0) else 0)
    return  [vram_dict[coord] for coord in [ \
                (0,0),(0,1),(1,0),(1,1),(2,0),(2,1),(3,0),(3,1),
                (4,0),(4,1),(5,0),(5,1),(6,0),(6,1),(7,0),(7,1),
                (0,2),(0,3),(1,2),(1,3),(2,2),(2,3),(3,2),(3,3),
                (4,2),(4,3),(5,2),(5,3),(6,2),(6,3),(7,2),(7,3)]
            ]            


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

    #TODO: need to do this for every file, then actually store it in the tile data section of the ROM
    convert_file_to_VRAM_data('new_sprite/lower/l_elevator_streak0.png')
    #TODO: Then need to tell the poses the correct amount of data to load into VRAM each time
    

if __name__ == "__main__":
    main()

