#Written by Artheau
#in March, 2019
#while sipping flavorful coffee loudly

#Takes a new sprite sheet and inserts it into a rom
#Right now, defaults to samus.png and sm_orig.sfc
#But you can specify other files on the command line (ask --help)
#Saves the modified rom as <orig_name>_modified.<ext>

#KNOWN ISSUES:
#Bad things happen if some of the image names are shared between the upper and lower columns of the filemap
# (not sure why yet)
#Spin jump is hard-wired in the game to not display its lower tilemap...but then it cannot easily be converted
# to use the sparks in order to implement screw attack without space jump
#Some animations are fused between their upper/lower animations (e.g. morphball pointers) <-- there are more that break the existing animations
# Other poses are hard fused either in tilemaps, AFP, or both, between poses in different animations
#The death sequence injection only has the left facing frames... I know where the tilemaps are,
# but where is the DMA pointer so that I can intercept it and make it load something else/more stuff/etc.?

#TODO:
#Inject death sequence (also ideally move this animation somewhere where there is more room, so that the artist is not confined to the hourglass shape)
#  Death sequence is located at position $D8000, in optimized form
#Make left/right animations for screw attack without space jump (requires some engine editing/disassembly)
#  Maybe there is a workaround that homogenizes the screw attack frames and uses the free pointer positions for control codes?
#Assign all unused animations to null pointers, just in case (after testing without making them null) <--especially DMA loads
#Do more "prayer/quake" separation using whatever tile space remains


import argparse
import os
import struct
import csv
import itertools
import numpy as np
from PIL import Image

from lib import romload
from resources import tilemaps
from lib.constants import *

rom = None
filemap = None
sprite_sheet = None
global_layout = None



def erase_all_samus_info():
    blank_tile = bytes(8*[0x00,0xFF]+16*[0x00]) #technically this is Samus's yellow color right now (Pac Man mode)
    for addr in range(convert_to_rom_address(SAMUS_TILES_START),convert_to_rom_address(SAMUS_TILES_END),TILESIZE):
        rom[addr:addr+TILESIZE] = blank_tile
    blank_DMA_entry = bytes(7*[0x00])
    for addr in range(convert_to_rom_address(DMA_ENTRIES_START),convert_to_rom_address(DMA_ENTRIES_END)-0x07,0x07):
        rom[addr:addr+0x07] = blank_DMA_entry

    #Blank the tile at $D5620 (this was used for symmetry breaks in elevator pose, and is no longer needed)
    transparent_tile = bytes(TILESIZE*[0x00])
    SYM_BREAK_TILE_ADDRESS = 0xd5620
    rom[SYM_BREAK_TILE_ADDRESS:SYM_BREAK_TILE_ADDRESS+TILESIZE] = transparent_tile

def write_new_palettes():
    power_palette = load_palette_from_image("power_palette")
    varia_palette = load_palette_from_image("varia_palette")
    gravity_palette = load_palette_from_image("gravity_palette")
    death_palette = load_palette_from_image("death_palette")
    flash_palette = load_palette_from_image("flash_palette")
    nightvision_colors = [load_palette_from_image(f"visor_nightvision_color{i}") for i in range(3)]
    ship_palette = load_palette_from_image("ship_palette")
    file_select_palette = load_palette_from_image("file_select_palette")
    ship_color_body = ship_palette[0]
    ship_color_window = ship_palette[1]
    ship_glow_color = ship_palette[2]

    set_palettes_at(0x1652C,[power_palette[4]]) #visor inside doors

    set_palettes_at(0x6DB8F,power_palette, modifier=(0,10,15)) #elevator palettes (power suit)
    set_palettes_at(0x6DC2D,power_palette, modifier=(0,5,15))
    set_palettes_at(0x6DC7C,power_palette, modifier=(0,0,10))
    set_palettes_at(0x6DBDE,power_palette, modifier=(0,10,15))

    set_palettes_at(0x6DCF5,varia_palette, modifier=(0,10,15)) #elevator palettes (varia suit)
    set_palettes_at(0x6DD44,varia_palette, modifier=(0,5,15))
    set_palettes_at(0x6DD93,varia_palette, modifier=(0,0,10))
    set_palettes_at(0x6DDE2,varia_palette, modifier=(0,10,15))

    set_palettes_at(0x6DE5B,gravity_palette, modifier=(0,10,15)) #elevator palettes (gravity suit)
    set_palettes_at(0x6DEAA,gravity_palette, modifier=(0,5,15))
    set_palettes_at(0x6DEF9,gravity_palette, modifier=(0,0,10))
    set_palettes_at(0x6DF48,gravity_palette, modifier=(0,10,15))

    set_palettes_at(0x6DB6B,power_palette) #loader palettes (power suit) <-- not sure what these do but SMILE thinks they're important
    set_palettes_at(0x6DBBA,power_palette)
    set_palettes_at(0x6DC09,power_palette)
    set_palettes_at(0x6DC58,power_palette)
    set_palettes_at(0x6DCA4,power_palette)

    set_palettes_at(0x6DCD1,varia_palette) #loader palettes (varia suit)
    set_palettes_at(0x6DD20,varia_palette)
    set_palettes_at(0x6DD6F,varia_palette)
    set_palettes_at(0x6DDBE,varia_palette)
    set_palettes_at(0x6DE0A,varia_palette)

    set_palettes_at(0x6DE37,gravity_palette) #loader palettes (gravity suit)
    set_palettes_at(0x6DE86,gravity_palette)
    set_palettes_at(0x6DED5,gravity_palette)
    set_palettes_at(0x6DF24,gravity_palette)
    set_palettes_at(0x6DF70,gravity_palette)

    for i in range(16):
        set_palettes_at(0x6E466+i*0x22,power_palette,heat_mod(i)) #heat palettes (power suit)
        set_palettes_at(0x6E692+i*0x22,varia_palette,heat_mod(i)) #heat palettes (varia suit)
        set_palettes_at(0x6E8BE+i*0x22,gravity_palette,heat_mod(i)) #heat palettes (gravity suit)
    

    set_palettes_at(0x66569,sepia(power_palette)) #Samus sepia during intro storyline
    set_palettes_at(0xDA380,sepia(power_palette), fade=0.6) #a sepia palette used when Samus is hurt in the intro animations
    set_palettes_at(0xDA3A0,sepia(power_palette)) #a sepia palette used when Samus is hurt in the intro animations


    set_palettes_at(0xD9400,power_palette) #power suit
    set_palettes_at(0xD9520,varia_palette) #varia suit
    for i in range(8):
        set_palettes_at(0xDA120+0x20*i, death_palette, fade = float(i)/8.0)   #death palette
    for i in range(6):
        set_palettes_at(0xD9C6A+0x20*i, flash_rotate(flash_palette,i))  #crystal flash bubble colors
    set_palettes_at(0xD9800,gravity_palette) #gravity suit

    for base_address,suit_palette in zip([0xD9820,0xD9920,0xD9A20],[power_palette, varia_palette, gravity_palette]):
        #charge
        for i in range(8):
            set_palettes_at(base_address + 0x20*i, suit_palette, fade = float(i)/8.0)


    for base_address,suit_palette in zip([0xD9B20,0xD9D20,0xD9F20],[power_palette, varia_palette, gravity_palette]):
        #speed boost
        set_palettes_at(base_address       , suit_palette, modifier=(0,0,0))
        set_palettes_at(base_address + 0x20, suit_palette, modifier=(0,0,10))
        set_palettes_at(base_address + 0x40, suit_palette, modifier=(0,5,20))
        set_palettes_at(base_address + 0x60, suit_palette, modifier=(0,15,20))

    for base_address,suit_palette in zip([0xD9BA0,0xD9DA0,0xD9FA0],[power_palette, varia_palette, gravity_palette]):
        #speed squat
        for i in range(4):
            set_palettes_at(base_address + 0x20*i, suit_palette, fade = float(i)/4.0)

    for base_address,suit_palette in zip([0xD9C20,0xD9E20,0xDA020],[power_palette, varia_palette, gravity_palette]):
        #shine spark classic
        # set_palettes_at(base_address       , suit_palette, modifier=(0,0,0))
        # set_palettes_at(base_address + 0x20, suit_palette, modifier=(10,10,5))
        # set_palettes_at(base_address + 0x40, suit_palette, modifier=(16,16,0))
        # set_palettes_at(base_address + 0x60, suit_palette, modifier=(26,26,10))
        #but my eyes hurt with so much yellow so I tried this instead
        set_palettes_at(base_address       , suit_palette, modifier=(0,0,0))
        set_palettes_at(base_address + 0x20, suit_palette, modifier=(8,8,4))
        set_palettes_at(base_address + 0x40, suit_palette, modifier=(13,13,0))
        set_palettes_at(base_address + 0x60, suit_palette, modifier=(22,22,8))

    for base_address,suit_palette in zip([0xD9CA0,0xD9EA0,0xDA0A0],[power_palette, varia_palette, gravity_palette]):
        #screw attack
        set_palettes_at(base_address       , suit_palette, modifier=(0,0,0))
        set_palettes_at(base_address + 0x20, suit_palette, modifier=(0,10,0))
        set_palettes_at(base_address + 0x40, suit_palette, modifier=(0,20,0))
        set_palettes_at(base_address + 0x60, suit_palette, modifier=(0,30,5))

    for i in range(3):
        set_palettes_at(0xDA3C6 + 0x02*i,nightvision_colors[i]) #nightvision/xray visor colors

    for i in range(10):   #rainbow palette
        set_palettes_at(0xDA240 + 0x20*i, rainbow(power_palette,i))

    #erase_palettes_at(0xD9420,0x10) #an all yellow palette that Samus flashes when about to die (and other things?)
    #erase_palettes_at(0x8D7A2,0x01) #charge release

    set_palettes_at(0x1125A0,get_dark_ship_colors(ship_color_body,ship_color_window))
    set_palettes_at(0x6668B,get_bright_ship_colors(ship_color_body,ship_color_window))   #ship in space
    for i in range(0x0E):
        set_palettes_at(0x6CA54+i*0x06, [ship_glow_color], fade = abs((7-i)/7.0), fade_color = (0,0,0))   #ship glowing underside
    for i in range(0x10):
        set_palettes_at(0x6D6C2+i*0x24,get_bright_ship_colors(ship_color_body,ship_color_window), fade = (15.0-float(i))/15.0)   #ship at endgame
    
    set_palettes_at(0x765E0,file_select_palette)

'''
def erase_palettes_at(addr, size, erase_color = None):
    if not erase_color:
        erase_color = [0x00,0x02] #(a deep green in BGR 555 little endian format)

    erase_info = bytes(size*erase_color)
    rom[addr:addr+2*size] = erase_info
'''

def set_palettes_at(addr,color_list,modifier=(0,0,0), fade = 0.0, fade_color = (248,248,248)):
    #modifier = strict color addition
    #fade = scale from 0 to 1 of how much to proportionally fade to white (technically white is 8 * 0x1F = 248)
    #fade_color = color to fade towards (usually white, but sometimes black)
    delta_red, delta_green, delta_blue = modifier
    for (red,green,blue) in color_list.copy():
        if fade < 0:
            print(f"raw: {(red,green,blue)}")
        red = (1.0-fade)*red + fade_color[0]*fade + delta_red*8
        green = (1.0-fade)*green + fade_color[1]*fade + delta_green*8
        blue = (1.0-fade)*blue + fade_color[2]*fade + delta_blue*8
        [red, green, blue] = [int(max(0,min(255,color))) for color in [red,green,blue]]   #make sure it is a proper color
        if fade < 0:
            print(f"modified: {(red,green,blue)}")
        color_555 = ((blue//8) << 10) + ((green//8) << 5) + (red//8)   #convert to 555 format
        rom[addr:addr+2] = little_endian(color_555,2)        #write to rom in little endian format
        addr += 2 

def heat_mod(step):
    if step == 0:
        return (0,0,0)
    elif step <= 2 or step >= 13:
        return (1,0,0)
    elif step <= 4 or step >= 11:
        return (2,0,0)
    elif step <= 6 or step >= 9:
        return (3,0,0)
    else:
        return (5,0,0)

def grayscale(palette):
    gray_palette = []
    for (r,g,b) in palette:
        #x = 0.21*r + 0.72*g + 0.07*b   #luminosity formula attempt
        x = 0.31*r + 0.52*g + 0.17*b    #modified luminosity
        #x = (r+g+b)//3                 #rote averaging
        gray_palette.append((x,x,x))
    max_visor = max(palette[4])
    gray_palette[4] = (max_visor,max_visor,max_visor)  #visor should be essentially white (as bright as the brightest color)
    return gray_palette

def sepia(palette):
    return [(r,g,b*14.0/16.0) for (r,g,b) in grayscale(palette)]

def rainbow(palette,frame):
    base_color = [  (0x16,0x04,0x04),
                    (0x16,0x0D,0x02),
                    (0x16,0x16,0x00),
                    (0x0B,0x16,0x00),
                    (0x00,0x16,0x00),
                    (0x01,0x11,0x08),
                    (0x01,0x0C,0x10),
                    (0x0A,0x06,0x12),
                    (0x12,0x00,0x12),
                    (0x15,0x02,0x0B)][frame]
    new_palette = []
    for (x,_,_) in grayscale(palette):
        new_palette.append((8*base_color[0]+x/3,8*base_color[1]+x/3,8*base_color[2]+x/3))

    return new_palette

def get_dark_ship_colors(ship_color_body,ship_color_window):
    color_list = []
    color_list.append(ship_color_body)
    color_list.append(tuple(16/21*color for color in ship_color_body))
    color_list.append(tuple( 3/21*color for color in ship_color_body))
    color_list.append(tuple( 1/21*color for color in ship_color_body))
    color_list.append(tuple(17/21*color for color in ship_color_body))
    color_list.append(tuple(13/21*color for color in ship_color_body))
    color_list.append(tuple( 9/21*color for color in ship_color_body))
    color_list.append(tuple(4 /21*color for color in ship_color_body))
    color_list.append(ship_color_window)
    color_list.append(tuple(0.7*color for color in ship_color_window))
    color_list.append(tuple(0.4*color for color in ship_color_window))

    return color_list

def get_bright_ship_colors(ship_color_body,ship_color_window):
    color_list = []
    color_list.append(tuple(color+72 for color in ship_color_body))
    color_list.append(tuple(25/21*color for color in ship_color_body))
    color_list.append(tuple(10/21*color for color in ship_color_body))
    color_list.append(tuple( 0/21*color for color in ship_color_body))
    color_list.append(tuple(color+5 for color in ship_color_body))
    color_list.append(tuple(22/21*color for color in ship_color_body))
    color_list.append(tuple(18/21*color for color in ship_color_body))
    color_list.append(tuple(13/21*color for color in ship_color_body))
    color_list.append(ship_color_window)
    color_list.append(tuple(0.7*color for color in ship_color_window))
    color_list.append(tuple(0.4*color for color in ship_color_window))

    return color_list

def flash_rotate(flash_palette,shift):
    flash_palette = flash_palette.copy()
    for _ in range(shift):
        last_color = flash_palette.pop()
        flash_palette.insert(0, last_color)
    return flash_palette

def write_new_tilemaps():
    current_addr = SAMUS_TILEMAPS_START

    #upper body tilemaps
    upper_map_addresses = {}
    tilemaps_to_create = tilemaps.upper_tilemaps
    for key in tilemaps_to_create:
        upper_map_addresses[key] = current_addr - 0x920000
        current_addr = write_tilemap(tilemaps_to_create[key], current_addr)

    #lower body tilemaps
    lower_map_addresses = {}
    tilemaps_to_create = tilemaps.lower_tilemaps
    for key in tilemaps_to_create:
        lower_map_addresses[key] = current_addr - 0x920000
        current_addr = write_tilemap(tilemaps_to_create[key], current_addr)

    #tilemaps for the death sequence
    for i,tilemap in enumerate(tilemaps.deathmaps.values()):
        pointer_location = convert_to_rom_address(0x9290C5+2*i)
        rom[pointer_location:pointer_location+2] = little_endian(current_addr - 0x920000,2)
        current_addr = write_tilemap(tilemap, current_addr)

    #tilemaps for the missile ports (only need to change them to not be flipped)
    for i in range(10):
        write_location = convert_to_rom_address(0x90C792 + 2*i)
        rom[write_location] = 0x28
    return upper_map_addresses, lower_map_addresses


def write_tilemap(tilemap, current_addr):
    tilemap_size = len(tilemap)
    rom_addr = convert_to_rom_address(current_addr)
    rom[rom_addr:rom_addr+tilemap_size] = bytes(tilemap)
    current_addr += tilemap_size
    if current_addr > SAMUS_TILEMAPS_END:
        raise AssertionError("Made too many tilemaps -- exceeded ROM tilemap allocation")
    return current_addr



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
    #animation_number_list = list(animation_number_list)[::-1]
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
    upper_files = set((single_pose_dict['upper_file'],single_pose_dict['upper_palette']) \
                             for single_pose_dict in filemap.values())
    lower_files = set((single_pose_dict['lower_file'],single_pose_dict['lower_palette']) \
                             for single_pose_dict in filemap.values())

    for file, palette in list(upper_files)+list(lower_files): #ordering this to have upper tiles first, like in original data
        row1, row2 = get_VRAM_data(file,palette)
        length = len(row1+row2)
        if (tile_ptr+length) % 0x10000 < 0x8000:   #will write over two banks -- this is bad for DMA
            tile_ptr = ((tile_ptr+length)//0x10000)*0x10000 + 0x8000  #go to next bank
        DMA_dict[file] = (tile_ptr,len(row1),len(row2))
        tile_ptr = write_single_row_of_tiles(row1, tile_ptr)
        tile_ptr = write_single_row_of_tiles(row2, tile_ptr)

    #write the missile port tiles
    pose_list = [   'port_aim_up_facing_right',
                    'port_up_and_right',
                    'port_right',
                    'port_down_and_right',
                    'port_aim_down_facing_right',
                    'port_aim_down_facing_left',
                    'port_down_and_left',
                    'port_left',
                    'port_up_and_left',
                    'port_aim_up_facing_left']
    for pose_number, name in enumerate(pose_list):
        for i in range(3):   #3 port graphics for each direction
            single_tile, _ = get_VRAM_data(f"{name}{i}", "power_palette")
            write_single_row_of_tiles(single_tile, 0x9A9A00+0x80*pose_number+0x20*i)

    #write the file select tiles
    row1A, row2A = get_VRAM_data("file_select_direct_injection0", "file_select_palette")
    row1B, row2B = get_VRAM_data("file_select_direct_injection1", "file_select_palette")
    row3A, _ = get_VRAM_data("file_select_direct_injection2", "file_select_palette")
    row3B, row4 = get_VRAM_data("file_select_direct_injection3", "file_select_palette")

    write_single_row_of_tiles(row1A,0x8EA600)
    write_single_row_of_tiles(row1B,0x8EA700)
    write_single_row_of_tiles(row2A,0x8EA800)
    write_single_row_of_tiles(row2B,0x8EA900)
    write_single_row_of_tiles(row3A,0x8EAA00)
    write_single_row_of_tiles(row3B,0x8EAB00)
    write_single_row_of_tiles(row4[-0x40:],0x8EADC0)

    
    #write the death tiles
    rows = {}
    for i in range(0,10,2):
        rows[f"{i+1}A"], rows[f"{i+2}A"] = get_VRAM_data(f"death_direct_injection{i}", "death_palette")
        rows[f"{i+1}B"], rows[f"{i+2}B"] = get_VRAM_data(f"death_direct_injection{i+1}", "death_palette")

        row1A, row2A = get_VRAM_data(f"death_direct_injection_alt{i}", "power_palette")
        row1B, row2B = get_VRAM_data(f"death_direct_injection_alt{i+1}", "power_palette")
        rows[f"{i+1}A"] = list(map(sum,itertools.zip_longest(rows[f"{i+1}A"],row1A,fillvalue = 0)))
        rows[f"{i+1}B"] = list(map(sum,itertools.zip_longest(rows[f"{i+1}B"],row1B,fillvalue = 0)))
        rows[f"{i+2}A"] = list(map(sum,itertools.zip_longest(rows[f"{i+2}A"],row2A,fillvalue = 0)))
        rows[f"{i+2}B"] = list(map(sum,itertools.zip_longest(rows[f"{i+2}B"],row2B,fillvalue = 0)))

    for i in range(10):
        write_single_row_of_tiles(rows[f"{i+1}A"],0x9B8000+0x200*i)
        write_single_row_of_tiles(rows[f"{i+1}B"],0x9B8100+0x200*i)

    return DMA_dict

def write_single_row_of_tiles(row,tile_ptr):
    length = len(row)
    rom_ptr = convert_to_rom_address(tile_ptr)
    rom[rom_ptr:rom_ptr+length] = bytes(row)

    tile_ptr += length
    if tile_ptr > SAMUS_TILES_END:
        raise AssertionError("Too many tiles have been written into the ROM -- no more space available")

    return tile_ptr



def get_VRAM_data(image_name,palette_filename):
    image = extract_sub_image(sprite_sheet, image_name)
    if not image:    #empty retrieval
        return [], []

    pixels = image.load()

    
    if palette_filename == 'flash_palette':
        palette = [(15,0,0)]*10 + load_palette_from_image(palette_filename)
        start_index = 10
    else:
        palette = load_palette_from_image(palette_filename)
        start_index = 1

    reverse_palette = {(r,g,b,0xFF):index for (index,(r,g,b)) in enumerate(palette) if index >= start_index}
    image_colors = [color for (count,color) in image.getcolors()]

    for (r,g,b,a) in image_colors:
        if a == 0:
            reverse_palette[(r,g,b,a)] = 0      #force all the transparent colors to index 0

    #audit the colors in the image to make sure we CAN translate them all using the palette
    for color in image_colors:
        if color not in reverse_palette:
            image.show()
            raise AssertionError(f"color {color} is present in image {image_name}, but it is not in the corresponding palette")

    image_raw_pixels = list(image.getdata())
    cols, rows = image.size

    if cols % 8 != 0 or rows % 8 != 0:
        raise AssertionError(f"image {image_name} is not sized correctly for 8x8 tiles")

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


    if len(row1)//TILESIZE > 0x08 or len(row2)//TILESIZE > 0x08:
        raise AssertionError(f"Too many tiles created for {image_name}")

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

    #Samus upper body DMA
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

    #Samus lower body DMA
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

    #Samus missile port locations (TODO: Pull out constants to a single source)
    payload = [ bytes([0x00, 0x00, 0x00, 0x9A, 0x20, 0x9A, 0x40, 0x9A]),   #vertical
                bytes([0x00, 0x00, 0x80, 0x9A, 0xA0, 0x9A, 0xC0, 0x9A]),   #up right
                bytes([0x00, 0x00, 0x00, 0x9B, 0x20, 0x9B, 0x40, 0x9B]),   #right
                bytes([0x00, 0x00, 0x80, 0x9B, 0xA0, 0x9B, 0xC0, 0x9B]),   #down left (h-flipped)
                bytes([0x00, 0x00, 0x00, 0x9C, 0x20, 0x9C, 0x40, 0x9C]),   #vertical (v-flipped)
                bytes([0x00, 0x00, 0x80, 0x9C, 0xA0, 0x9C, 0xC0, 0x9C]),   #vertical (hv-flipped)
                bytes([0x00, 0x00, 0x00, 0x9D, 0x20, 0x9D, 0x40, 0x9D]),   #down left
                bytes([0x00, 0x00, 0x80, 0x9D, 0xA0, 0x9D, 0xC0, 0x9D]),   #right (h-flipped)
                bytes([0x00, 0x00, 0x00, 0x9E, 0x20, 0x9E, 0x40, 0x9E]),   #up right (h-flipped)
                bytes([0x00, 0x00, 0x80, 0x9E, 0xA0, 0x9E, 0xC0, 0x9E])]   #vertical (h-flipped)

    missile_gfx_data_ptr = 0x90F800   #free space at end of bank is now used for writing tile addresses
    for i in range(10):
        #start at 90C7A5
        target_addr = convert_to_rom_address(0x90C7A5+2*i)
        #write a pointer to somewhere near 90F800
        rom[target_addr:target_addr+2] = little_endian(missile_gfx_data_ptr-0x900000,2)
        target_addr = convert_to_rom_address(missile_gfx_data_ptr)
        #at that spot, write 8 bytes
        rom[target_addr:target_addr+8] = payload[i]
        missile_gfx_data_ptr += 8

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

def load_palette_from_image(palette_name):
    pixels = extract_sub_image(sprite_sheet, palette_name).getdata()
    return ([(r,g,b) for (r,g,b,a) in pixels])


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
            upper_palette = row[6]
            lower_map = row[7]
            lower_file = row[8]
            lower_palette = row[9]

            filemap[(animation_number,timeline_number)] = { 'pose_number': pose_number,
                                                        'upper_map': upper_map,
                                                        'upper_file': upper_file,
                                                        'upper_palette': upper_palette,
                                                        'lower_map': lower_map,
                                                        'lower_file': lower_file,
                                                        'lower_palette': lower_palette}
    return filemap


def load_sprite_sheet(filename):
    return Image.open(filename)

def load_layout(filename):
    #TODO: JSON this part
    from resources import layout

    new_layout = flatten_layout(layout.layout)

    return new_layout

def flatten_layout(layout):
    if 'offset' in layout:
        master_offset = layout['offset']
    else:
        raise AssertionError(f"Missing offset in layout file, only found {layout.keys()}")

    images = {}

    if 'images' in layout:
        #append images
        append_to_image_list(layout['images'],images,master_offset)
    if 'blocks' in layout:
        #append flatten_layout on the blocks
        for block in layout['blocks'].values():
            append_to_image_list(flatten_layout(block),images,master_offset)

    return images

def append_to_image_list(append_dict,image_list,master_offset):
    for key in append_dict:
        append_item = append_dict[key]
        for tile_ref in append_item:
            for i in range(2):
                tile_ref['source'][i] += master_offset[i]   #apply the master offset
        if key not in image_list:
            image_list[key] = append_item
        else:
            raise AssertionError(f"Tried to add image {key} from layout file, but it was defined twice")


def extract_sub_image(sprite_sheet, image_name):
    if image_name not in global_layout:
        raise AssertionError(f"image name {image_name} was not found in the layout file")
    if not global_layout[image_name]:  #if empty
        return None

    final_size = [max([supertile['dest'][i]+supertile['size'][i] for supertile in global_layout[image_name]]) for i in range(2)]
    cropped_image = Image.new("RGBA",tuple(final_size),(0,0,0,0))

    for supertile in global_layout[image_name]:
        source = supertile['source']
        dest = supertile['dest']
        size = supertile['size']
        cropped_image.paste(sprite_sheet.crop((source[0],source[1],source[0]+size[0],source[1]+size[1])),tuple(dest))

    return cropped_image

def process_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom",
                        dest=ROM_FILENAME_ARG_KEY,
                        help="Location of the rom file; e.g. /my_dir/sm_orig.sfc",
                        metavar="<rom_filename>",
                        default='sm_orig.sfc')
    parser.add_argument("--sheet",
                        dest=SPRITE_SHEET_FILENAME_ARG_KEY,
                        help="Location of the sprite sheet; e.g. /my_dir/samus.png",
                        metavar="<sprite_sheet_filename>",
                        default='resources/samus.png')
    parser.add_argument("--layout",
                        dest=LAYOUT_FILENAME_ARG_KEY,
                        help="Location of the layout file; e.g. /my_dir/layout.json",
                        metavar="<layout_filename>",
                        default='resources/layout.json')

    command_line_args = vars(parser.parse_args())

    return command_line_args

def convert_to_rom_address(snes_addr):
    #convert from memory address to ROM address (lorom 0x80)
    bank = snes_addr // 0x10000 - 0x80
    offset = (snes_addr % 0x10000) - 0x8000

    if offset < 0x0000 or bank < 0x00:
        raise AssertionError(f"Function convert_to_rom_address() called on {hex(snes_addr)}, but this is not a valid SNES address.")
    
    new_address = bank*0x8000 + offset

    return new_address

def convert_to_ram_address(rom_addr):
    #convert from ROM address to memory address (lorom 0x80)
    bank = rom_addr // 0x8000
    offset = rom_addr % 0x8000

    if bank < 0x00:
        raise AssertionError(f"Function convert_to_ram_address() called on {hex(rom_addr)}, but this is not a valid SNES address.")
    
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
    global sprite_sheet
    global global_layout


    command_line_args = process_command_line_args()
    rom = romload.load_rom_contents(command_line_args[ROM_FILENAME_ARG_KEY])
    filemap = load_filemap()
    sprite_sheet = load_sprite_sheet(command_line_args[SPRITE_SHEET_FILENAME_ARG_KEY])
    global_layout = load_layout(command_line_args[LAYOUT_FILENAME_ARG_KEY])

    erase_all_samus_info()   #technically this is not needed, but it provides a stronger argument that there are no bugs/oversights

    upper_map_addresses, lower_map_addresses = write_new_tilemaps()

    DMA_dict = write_tiles()
    DMA_info_address_dict = create_DMA_tables(DMA_dict)

    assign_new_tilemaps(upper_map_addresses, lower_map_addresses, DMA_dict, DMA_info_address_dict)

    write_new_palettes()

    #the file saves automatically because it is an mmap (see romload.py)
    

if __name__ == "__main__":
    main()

