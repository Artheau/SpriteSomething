#Written by Artheau
#in March, 2019
#while sipping flavorful coffee loudly

#applies bugfixes to the rom
#blanks out all Samus tiles!  (Pac Man mode)
#rebuilt the tilemaps to create a "canvas" to paint on.

#TODO: factor out the mutual hex processing code from this file and util.py
#TODO: Re-factor as much as possible to avoid doubling up on "upper" and "lower" halves of the code

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


#TODO: Remove the right chest tile at ROM D5620 (used to break symmetry in elevator poses; no longer necessary)



def erase_all_samus_info():
    blank_tile = bytes(8*[0x00,0xFF]+16*[0x00]) #technically this is Samus's yellow color right now (Pac Man mode)
    for addr in range(convert_to_rom_address(SAMUS_TILES_START),convert_to_rom_address(SAMUS_TILES_END),TILESIZE):
        rom[addr:addr+TILESIZE] = blank_tile
    blank_DMA_entry = bytes(7*[0x00])
    for addr in range(convert_to_rom_address(DMA_ENTRIES_START),convert_to_rom_address(DMA_ENTRIES_END)-0x07,0x07):
        rom[addr:addr+0x07] = blank_DMA_entry


def write_new_tilemaps():
    current_addr = SAMUS_TILEMAPS_START

    upper_map_addresses = {}
    tilemaps_to_create = get_raw_upper_tilemaps()
    for key in tilemaps_to_create:
        tilemap = tilemaps_to_create[key]
        tilemap_size = len(tilemap)
        rom_addr = convert_to_rom_address(current_addr)
        rom[rom_addr:rom_addr+tilemap_size] = bytes(tilemap)
        upper_map_addresses[key] = current_addr - 0x920000
        current_addr += tilemap_size
        if current_addr > SAMUS_TILEMAPS_END:
            raise AssertionError("Made too many tilemaps -- exceeded ROM tilemap allocation")

    lower_map_addresses = {}
    tilemaps_to_create = get_raw_lower_tilemaps()
    for key in tilemaps_to_create:
        tilemap = tilemaps_to_create[key]
        tilemap_size = len(tilemap)
        rom_addr = convert_to_rom_address(current_addr)
        rom[rom_addr:rom_addr+tilemap_size] = bytes(tilemap)
        lower_map_addresses[key] = current_addr - 0x920000
        current_addr += tilemap_size
        if current_addr > SAMUS_TILEMAPS_END:
            raise AssertionError("Made too many tilemaps -- exceeded ROM tilemap allocation")

    return upper_map_addresses, lower_map_addresses


def get_raw_upper_tilemaps():
    return tilemaps.upper_tilemaps

def get_raw_lower_tilemaps():
    return tilemaps.lower_tilemaps



def assign_new_tilemaps(upper_map_addresses, lower_map_addresses, DMA_dict, DMA_info_address_dict):
    #every pose/timeline has one four byte line in the AFP table ($00000000 for null pose), in an array indexed by the animation number
    # bytes are: upper_dma_table, upper_dma_entry, lower_dma_table, lower_dma_entry
    # these can be modified in place if needed
    #
    #from $92D94E, index by animation number
    # to get ptr AFP_T??, tells me where the animation's timeline data is
    #When I get there, there is four bytes for each timeline entry, call them a,b (upper).  There are two more for lower
    #Take these numbers to $92D91E (upper) or $92D938 (lower)
    #use a to index and get UT_DMAa ptr
    #go there and get entry #b (7 byte array entries).



    animation_number_list = set([animation_number for (animation_number,timeline_number) in filemap.keys()])
    for animation_number in animation_number_list:
        max_timeline = max([timeline_number for (this_animation_number,timeline_number) in filemap.keys() if this_animation_number == animation_number])


        
        upper_tilemap_list = []
        lower_tilemap_list = []
        afp_list = []
        for t in range(max_timeline+1):
            if (animation_number,t) not in filemap:   #as will be the case for control codes
                upper_tilemap_list.extend([0x00,0x00])
                lower_tilemap_list.extend([0x00,0x00])
                afp_list.extend([0x00,0x00,0x00,0x00])
            else:
                upper_address_to_insert = upper_map_addresses[filemap[(animation_number,t)]['upper_map']]
                upper_tilemap_list.extend(little_endian(upper_address_to_insert,2))

                afp_list.extend(DMA_info_address_dict[filemap[(animation_number,t)]['upper_file']])
                
                lower_address_to_insert = lower_map_addresses[filemap[(animation_number,t)]['lower_map']]
                lower_tilemap_list.extend(little_endian(lower_address_to_insert,2))
                afp_list.extend(DMA_info_address_dict[filemap[(animation_number,t)]['lower_file']])

        [upper_offset] = get_indexed_values(UPPER_TILEMAP_TABLE_POINTER,animation_number,0x02,'2')
        [lower_offset] = get_indexed_values(LOWER_TILEMAP_TABLE_POINTER,animation_number,0x02,'2')

        rom_upper_tilemap_array = convert_to_rom_address(TILEMAP_TABLE + 2 * upper_offset)
        rom[rom_upper_tilemap_array:rom_upper_tilemap_array+len(upper_tilemap_list)] = bytes(upper_tilemap_list)

        rom_lower_tilemap_array = convert_to_rom_address(TILEMAP_TABLE + 2 * lower_offset)
        rom[rom_lower_tilemap_array:rom_lower_tilemap_array+len(lower_tilemap_list)] = bytes(lower_tilemap_list)

        [afp_table_location] = get_indexed_values(AFP_TABLE_ARRAY,animation_number,0x02,'2')
        afp_table_location += 0x920000

        afp_table_in_rom = convert_to_rom_address(afp_table_location)
        rom[afp_table_in_rom:afp_table_in_rom+len(afp_list)] = bytes(afp_list)



def write_tiles():
    DMA_dict = {}
    tile_ptr = SAMUS_TILES_START
    upper_files = set(single_pose_dict['upper_file'] for single_pose_dict in filemap.values())
    lower_files = set(single_pose_dict['lower_file'] for single_pose_dict in filemap.values())

    for file in upper_files:
        filename = f"new_sprite/upper/{file}.png"
        row1, row2 = convert_file_to_VRAM_data(filename,lower=False)
        DMA_dict[file] = (tile_ptr,len(row1),len(row2))
        tile_ptr = write_single_row_of_tiles(row1, tile_ptr)
        tile_ptr = write_single_row_of_tiles(row2, tile_ptr)
    for file in lower_files:
        filename = f"new_sprite/lower/{file}.png"
        row1, row2 = convert_file_to_VRAM_data(filename,lower=True)
        DMA_dict[file] = (tile_ptr,len(row1),len(row2))
        tile_ptr = write_single_row_of_tiles(row1, tile_ptr)
        tile_ptr = write_single_row_of_tiles(row2, tile_ptr)

    return DMA_dict

def write_single_row_of_tiles(row,tile_ptr):
    length = len(row)
    rom_ptr = convert_to_rom_address(tile_ptr)
    rom[rom_ptr:rom_ptr+length] = bytes(row)

    tile_ptr += length
    if tile_ptr > SAMUS_TILES_END:
        raise AssertionError("Too many tiles have been written into the ROM -- no more space available")

    return tile_ptr



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
    cols, rows = image.size

    #sadly this next data structure will need to be indexed by index_pixels[row][col],
    # which is opposite the math intution (i.e. must use index_pixels[y_coord][x_coord])
    index_pixels = np.reshape(list(map(lambda x: reverse_palette[x], image_raw_pixels)), (rows,cols))
    
    #####now flatten the image out in the 4bpp tile format

    row1,row2 = [],[]

    #big tiles first
    for y in range(0,rows-8,16):
        for x in range(0,cols-8,16):
            row1.extend(extract_vram_tile(index_pixels[y  :y+8 ,x  :x+8 ]))  #top left
            row1.extend(extract_vram_tile(index_pixels[y  :y+8 ,x+8:x+16]))  #top right
            row2.extend(extract_vram_tile(index_pixels[y+8:y+16,x  :x+8 ]))  #bottom left
            row2.extend(extract_vram_tile(index_pixels[y+8:y+16,x+8:x+16]))  #bottom right
    #rightmost column if necessary
    if cols % 16 != 0:
        x = cols - (cols % 16)
        for y in range(0,rows-8,16):
            row1.extend(extract_vram_tile(index_pixels[y  :y+8 ,x  :x+8 ]))  #top
            row2.extend(extract_vram_tile(index_pixels[y+8:y+16,x  :x+8 ]))  #bottom
    #bottom row if necessary
    if rows % 16 != 0:
        y = rows - (rows % 16)
        for x in range(0,cols-8,16):
            row1.extend(extract_vram_tile(index_pixels[y  :y+8 ,x  :x+8 ]))  #left
            row2.extend(extract_vram_tile(index_pixels[y  :y+8 ,x+8:x+16]))  #right
    #bottom right corner, if necessary
    if rows % 16 != 0 and cols % 16 != 0:
        x = cols - (cols % 16)
        y = rows - (rows % 16)
        row1.extend(extract_vram_tile(index_pixels[y  :y+8 ,x  :x+8 ]))
    
    #so there's this thing with row2 in the lower body section where they used the rightmost two tiles
    # for other stuff like cannon ports, so we need to stay out of there, unless we are rendering something that
    # we know will never use those tiles (e.g. space jump does not render cannon port, and so can use those tiles)
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



def create_DMA_tables(DMA_dict):
    #DMA tables:
    # a bunch of 7 byte instructions: long ptr to tiles, bytes in top row, bytes in bottom row
    # in theory these could be modified in place, but the original pose crosstalk might change the way these need to work
    #
    # can probably write DMA info from $92CBEE up to $92D91D, but after that you have to find somewhere else
    #
    #There will need to be exactly one DMA table for every image file (i.e. for every entry in DMA_dict)
    # Probably just better to strong-arm this instead of being ginger with the pointer overwrites

    upper_files = set(single_pose_dict['upper_file'] for single_pose_dict in filemap.values())
    lower_files = set(single_pose_dict['lower_file'] for single_pose_dict in filemap.values())

    DMA_info_address_dict = {}

    DMA_PAGESIZE = 0x20
    DMA_ptr = DMA_ENTRIES_START
    index = 0
    for file in upper_files:
        if index % DMA_PAGESIZE == 0x00:    #start a new DMA 'page' every DMA_PAGESIZE entries
            page_number = index // DMA_PAGESIZE
            if page_number > 0x0C:
                raise AssertionError("Exceeded Upper DMA Pointer Table limit")
            target_addr = convert_to_rom_address(UPPER_DMA_POINTER_TABLE + 2 * page_number)
            rom[target_addr:target_addr+2] = little_endian(DMA_ptr-0x920000,2)
        DMA_info_address_dict[file] = [index // DMA_PAGESIZE,index % DMA_PAGESIZE]
        DMA_ptr = write_single_DMA_entry(DMA_dict[file], DMA_ptr)
        index += 1
    index = 0
    for file in lower_files:
        if index % DMA_PAGESIZE == 0x00:    #start a new DMA 'page' every DMA_PAGESIZE entries
            page_number = index // DMA_PAGESIZE
            if page_number > 0x0A:
                raise AssertionError("Exceeded Lower DMA Pointer Table limit")
            target_addr = convert_to_rom_address(LOWER_DMA_POINTER_TABLE + 2 * page_number)
            rom[target_addr:target_addr+2] = little_endian(DMA_ptr-0x920000,2)
        DMA_info_address_dict[file] = [index // DMA_PAGESIZE,index % DMA_PAGESIZE]
        DMA_ptr = write_single_DMA_entry(DMA_dict[file], DMA_ptr)
        index += 1

    return DMA_info_address_dict



def write_single_DMA_entry(entry,DMA_ptr):
    rom_ptr = convert_to_rom_address(DMA_ptr)

    ptr = entry[0]
    size1 = entry[1]
    size2 = entry[2]
    rom[rom_ptr:rom_ptr+0x03] = little_endian(ptr,3)
    rom[rom_ptr+0x03:rom_ptr+0x05] = little_endian(size1,2)
    rom[rom_ptr+0x05:rom_ptr+0x07] = little_endian(size2,2)

    DMA_ptr += 0x07
    if DMA_ptr > DMA_ENTRIES_END:
        raise AssertionError("Too many DMA entries have been made -- there is no more room for DMA info")

    return DMA_ptr

def little_endian(x,num_bytes):
    result = []
    for i in range(num_bytes):
        result.append(x % 0x100)
        x = x // 0x100
    return bytes(result)


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

    erase_all_samus_info()   #technically this is not needed, but it provides a stronger argument that there are no bugs/oversights

    upper_map_addresses, lower_map_addresses = write_new_tilemaps()

    DMA_dict = write_tiles()
    DMA_info_address_dict = create_DMA_tables(DMA_dict)

    assign_new_tilemaps(upper_map_addresses, lower_map_addresses, DMA_dict, DMA_info_address_dict)

    #the file saves automatically because it is an mmap (see romload.py)
    

if __name__ == "__main__":
    main()

