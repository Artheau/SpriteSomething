#Written by Artheau
#over several days in Feb. 2019
#while looking out the window and dreaming of being outside in the sunshine

import struct
import csv
from pprint import pprint

TILESIZE = 0x20

STUDIED_ANIMATIONS = list(range(0xFD))

# STUDIED_ANIMATIONS.remove(0x89)     #Animation 0x89 is just animation 0x01's first frame (i.e. standing in place)
# STUDIED_ANIMATIONS.remove(0x8A)     #Animation 0x8A is just animation 0x02's first frame (i.e. standing in place)
# STUDIED_ANIMATIONS.remove(0xCD)     #Animation 0xCD and 0xC9 are identical
# STUDIED_ANIMATIONS.remove(0xCE)     #Animation 0xCE and 0xCA are identical
# STUDIED_ANIMATIONS.remove(0x4B)     #Animation 0x4B is just animation 0xA6's first frame (i.e. transitioning from air to ground or vice versa)
# STUDIED_ANIMATIONS.remove(0xA4)     #Animation 0xA4 is just animation 0xA6's first two frames (i.e. transitioning from air to ground or vice versa)
# STUDIED_ANIMATIONS.remove(0x4C)     #Animation 0x4C is just animation 0xA7's first frame (i.e. transitioning from air to ground or vice versa)
# STUDIED_ANIMATIONS.remove(0xA5)     #Animation 0xA5 is just animation 0xA7's first two frames (i.e. transitioning from air to ground or vice versa)
# STUDIED_ANIMATIONS.remove(0x53)     #Animation 0x53 is just animation 0xD7's first two frames (i.e. crystal ends in bonk pose)
# STUDIED_ANIMATIONS.remove(0x54)     #Animation 0x54 is just animation 0xD8's first two frames (i.e. crystal ends in bonk pose)

#I allow myself a few indulgences here by declaring global variables (please do not inform the Python Police)
rom = None
animation_data = None

def main():
    load_rom_contents()
    load_animation_data()

    usage_dict = {}
    big_usage_dict = {}
    appears_with = {}
    big_tiles = {}

    for animation in animation_data:
        if animation['used'] == True and animation['ID'] in STUDIED_ANIMATIONS:         #for debugging purposes, focus on one animation
            upper_tilemaps, lower_tilemaps = get_tilemaps(animation['ID'])

            VRAM_temporal_data = get_VRAM_data(animation['ID'])

            for i in range(animation['num_poses']):
                for tile in upper_tilemaps[i] + lower_tilemaps[i]:
                    for tile2 in upper_tilemaps[i] + lower_tilemaps[i]:
                        increment_value_in_dict(appears_with,hex(VRAM_temporal_data[i][tile['index']]),hex(VRAM_temporal_data[i][tile2['index']]))

                    if tile['large_size'] == True:
                        big_tiles[VRAM_temporal_data[i][tile['index']]] = [VRAM_temporal_data[i][tile['index']+offset] for offset in [0x00,0x01,0x10,0x11]]
                        for offset in [0x00,0x01,0x10,0x11]:
                            increment_value_in_dict(big_usage_dict,VRAM_temporal_data[i][tile['index']+offset],animation['ID'])
                    else:
                        increment_value_in_dict(usage_dict,VRAM_temporal_data[i][tile['index']],animation['ID'])

    
    #a quick audit on our assumptions
    if set(usage_dict.keys()).intersection(set(big_usage_dict.keys())):
        raise AssertionError(f"Something is wrong about the assumption that 16x16 tiles are never broken up")


    small_tile_number = len(usage_dict.keys())
    large_tile_number = len(appears_with.keys()) - small_tile_number
    print(f"Number of unique tiles used: \n{small_tile_number} of size 8x8 \n{large_tile_number} of size 16x16")


    #NOTABLY this does not deep check for relative arrangement to be the same in each instance of the chunk
    truly_unique_tile_chunks = set()
    ignore_set = set()
    for tile in appears_with:
        for tile2 in appears_with[tile]:
            if tile2 not in ignore_set and tile != tile2 and appears_with[tile][tile] == appears_with[tile][tile2]:
                ignore_set.add(tile)
                break
        if tile not in ignore_set:
            truly_unique_tile_chunks.add(tile)

    print(f"{len(truly_unique_tile_chunks)} truly unique chunks")

    joined_chunks = []
    for tile in sorted(truly_unique_tile_chunks):
        joined_chunk = set()
        for tile2 in sorted(appears_with):
            if tile in appears_with[tile2] and appears_with[tile2][tile2] == appears_with[tile2][tile]:
                joined_chunk.add(tile2)
        joined_chunks.append(joined_chunk)

    #TODO: export chunks natively (graphically with correct offsets)

    #this next identification doesn't have to be made, but it makes sense because Samus is the same in these ways
    raw_chunks = []
    pixel_perfect_chunks = []
    for chunk in joined_chunks:
        raw_chunk = set()
        for tile in chunk:
            if int(tile,0) in big_usage_dict.keys():
                for tile_part in big_tiles[int(tile,0)]:
                    raw_chunk.add(get_tile(tile_part))
            else:
                raw_chunk.add(get_tile(int(tile,0)))
        for existing_chunk in raw_chunks:
            if existing_chunk == raw_chunk:
                break
        else:
            raw_chunks.append(raw_chunk)
            pixel_perfect_chunks.append(chunk)

    print(f"Number of pixel-perfect unique chunks: {len(raw_chunks)}")

    for chunk in sorted(pixel_perfect_chunks):
        print("BEGIN CHUNK")
        for tile in sorted(chunk):
            if int(tile,0) in big_usage_dict.keys():
                print(f"big tile {[hex(tile_part) for tile_part in big_tiles[int(tile,0)]]}")
            elif int(tile,0) in usage_dict.keys():
                print(f"small tile {tile}")
            else:
                raise AssertionError()







def load_rom_contents():
    global rom
    with open('metroid.smc', mode='rb') as file:
        rom = file.read()

def load_animation_data():
    #generated this csv data from community disassembly data (thank you to all contributors)
    #format: [ANIMATION_ID, NUM_POSES, USED, DESCRIPTION]
    global animation_data
    animation_data = []
    with open('animations.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for row in spamreader:
            index = int(row[0],0)    #the second argument specifies to determine if it is hex or not automatically
            num_poses = int(row[1])
            used = row[2].lower() in ['true','t','y']
            description = row[3]
            animation_data.append({'ID': index, 'num_poses': num_poses,'used': used,'description':description})


def get_tilemaps(animation):
    #returns a list
    #one entry for each pose in the animation
    #each entry is a list of tile dicts
    num_poses = animation_data[animation]['num_poses']
    [upper_offset] = get_indexed_values(0x929263,animation,0x02,'2')
    [lower_offset] = get_indexed_values(0x92945D,animation,0x02,'2')

    upper_tilemap_offset = get_indexed_values(0x92808D,upper_offset,0x02,'2'*num_poses)
    lower_tilemap_offset = get_indexed_values(0x92808D,lower_offset,0x02,'2'*num_poses)

    upper_tilemaps_all = []
    lower_tilemaps_all = []

    for pose_number in range(num_poses):
        upper_tilemaps_all.append(process_tilemap(upper_tilemap_offset[pose_number]))
        lower_tilemaps_all.append(process_tilemap(lower_tilemap_offset[pose_number]))

    return upper_tilemaps_all,lower_tilemaps_all

def process_tilemap(offset):
    tilemap = []

    if offset != 0x00:             #offset can be zero for empty tilemaps (no tiles in this half of Samus body)
        tilemap_location = 0x920000+offset

        [tilemap_size] = get_indexed_values(tilemap_location,0,0x01,'2')

        for tile_number in range(tilemap_size):
            raw_tile = get_indexed_values(tilemap_location+(0x02+tile_number*0x05),0,0x01,'11111')
            tilemap.append(interpret_tile(raw_tile))

    return tilemap


def interpret_tile(raw_tile):
    tile = {}
    tile['x_offset'] = raw_tile[0]
    tile['auto_flag'] = raw_tile[1] & 0x01 != 0x00
    tile['large_size'] = raw_tile[1] & 0xc2 != 0x00
    tile['y_offset'] = raw_tile[2]
    tile['index'] = raw_tile[3]
    tile['v_flip'] = raw_tile[4] & 0x80 != 0x00
    tile['h_flip'] = raw_tile[4] & 0x40 != 0x00
    tile['priority'] = raw_tile[4] & 0x20 != 0x00
    tile['palette'] = (raw_tile[4] >> 2) & 0b111

    return tile


def get_VRAM_data(animation):
    [DMA_table_info_location] = get_indexed_values(0x92D94E,animation,0x02,'2')
    DMA_table_info_location += 0x920000

    VRAM_temporal_data = []

    for pose_number in range(animation_data[animation]['num_poses']):
        DMA_table_info_location
        [upper_table_location,upper_index,lower_table_location,lower_index] = get_indexed_values(DMA_table_info_location,pose_number,0x04,'1111')

        [upper_DMA_table] = get_indexed_values(0x92D91E,upper_table_location,0x02,'2')
        [lower_DMA_table] = get_indexed_values(0x92D938,lower_table_location,0x02,'2')
        upper_DMA_table += 0x920000
        lower_DMA_table += 0x920000


        upper_graphics_data = get_indexed_values(upper_DMA_table,upper_index,0x07,'322')  
        lower_graphics_data = get_indexed_values(lower_DMA_table,lower_index,0x07,'322')  

        VRAM = load_virtual_VRAM(upper_graphics_data,lower_graphics_data)

        VRAM_temporal_data.append(VRAM)

    return VRAM_temporal_data


def load_virtual_VRAM(upper_graphics_data,lower_graphics_data):
    [upper_graphics_ptr,upper_top_row_amt,upper_bottom_row_amt] = upper_graphics_data
    [lower_graphics_ptr,lower_top_row_amt,lower_bottom_row_amt] = lower_graphics_data

    VRAM = [None] * 0x20    #initialize

    for i in range(upper_top_row_amt//TILESIZE):
        VRAM[i] = convert_address(upper_graphics_ptr + i * TILESIZE)

    for i in range(lower_top_row_amt//TILESIZE):
        VRAM[0x08 + i] = convert_address(lower_graphics_ptr + i * TILESIZE)

    for i in range(upper_bottom_row_amt//TILESIZE):
        VRAM[0x10 + i] = convert_address(upper_graphics_ptr + upper_top_row_amt + i * TILESIZE)

    for i in range(lower_bottom_row_amt//TILESIZE):
        VRAM[0x18 + i] = convert_address(lower_graphics_ptr + lower_top_row_amt + i * TILESIZE)

    return VRAM


def get_indexed_values(base,index,entry_size,encoding):
    #returns an unpacked list of the values specified by the enconding at base[index], assuming array entries are entry_size long
    beginning_of_entry = convert_address(base+index*entry_size)
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


def convert_address(snes_addr):
    #convert from memory address to ROM address (lorom 0x80)
    bank = snes_addr // 0x10000 - 0x80
    offset = (snes_addr % 0x10000) - 0x8000

    if offset < 0x0000 or bank < 0x00:
        raise AssertionError(f"Function convert_address() called on {hex(snes_addr)}, but this is not a valid SNES address.")
    
    new_address = bank*0x8000 + offset

    return new_address

def increment_value_in_dict(*args):
    dest_dict = args[0]
    for arg in args[1:-1]:
        if arg not in dest_dict:
            dest_dict[arg] = {}
        dest_dict = dest_dict[arg]
    
    if args[-1] in dest_dict:
        dest_dict[args[-1]] += 1
    else:
        dest_dict[args[-1]] = 1

def get_tile(address):
    return rom[address:address+TILESIZE]

def horizontal_flip_byte(byte):
    return int('{:08b}'.format(byte)[::-1], 2)
    
if __name__ == "__main__":
    main()