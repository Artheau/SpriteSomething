#Written by Artheau
#over several days in Feb. 2019
#while looking out the window and dreaming of being outside in the sunshine



#TODO: Change large tiles to supertiles
#TODO: Try to merge supertiles when they are iff located correctly, and align


'''
ROADMAP:

Samus:
    animations = list of Animations

Animation:
    ID = unique identifying string
    index = actual value for the animation in-game
    used = True if the animation is used
    description = string with info about the animation
    poses = list of Poses
    gif(filename,palette): save a GIF of this animation

Pose:
    ID = unique identifying string
    duration = how long to hold this pose (in frames)
    VRAM = a 0x20 length list specifying the memory address of tiles loaded into VRAM during this pose
    upper_tiles = list of upper body Tiles
    lower_tiles = list of lower body Tiles
    tiles = list of all Tiles
    to_image(palette): retrieve n image of this pose

Tile:
    large = True if 16x16
    addresses = list of ROM addresses that this tile references
    x_offset = x offset
    y_offset = y offset
    auto_flag = ???
    v_flip = True if v flip
    h_flip = True if h flip
    priority = True if priority flag set
    palette = Palette
    draw_on(dict): inject raw pixel data into this dict
'''

import struct
import csv
import math
from PIL import Image
from pprint import pprint

rom = None

TILESIZE = 0x20
TILE_DIMENSION = int(math.sqrt(2 * TILESIZE))           #4 bits per pixel => 2 pixels per byte

class Samus:
    def __init__(self, rom_filename="metroid.smc", animation_data_filename="animations.csv"):
        global rom
        rom = load_rom_contents(rom_filename)
        self.animations = self.load_animations(animation_data_filename)
        self.palettes = self.load_palettes()

    def load_animations(self, animation_data_filename):
        #generated this csv data from community disassembly data (thank you to all contributors)
        #format: [ANIMATION_ID, NUM_POSES, USED, DESCRIPTION]
        animations = []
        with open(animation_data_filename, 'r') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            for row in spamreader:
                index = int(row[0],0)    #the second argument specifies to determine if it is hex or not automatically
                num_poses = int(row[1])
                used = row[2].lower() in ['true','t','y']
                description = row[3]
                animations.append(Animation(index, num_poses, used, description))
        return animations

    def load_palettes(self):
        palettes = {}

        palettes['standard'] = self.get_palette_at(0x9B9400)

        return palettes

    def get_palette_at(self, addr):
        raw_palette = get_indexed_values(addr,0,0x02,'2'*0x10)   #retrieve 0x10 2-byte colors in BGR 555 format
        palette = []
        for color in raw_palette:
            red = 8*(color & 0b11111)
            green = 8*((color >> 5) & 0b11111)
            blue = 8*((color >> 10) & 0b11111)
            palette.append((red,green,blue))
        return palette

class Animation:
    def __init__(self, index, num_poses, used, description):
        self.ID = hex(index)
        self.index = index
        self.used = used
        self.description = description
        self.poses = self.load_poses(num_poses)

    def gif(self, filename, palette,zoom=1):
        canvases = [pose.to_canvas() for pose in self.poses]

        MARGIN = 0x08
        BACKGROUND_COLOR = (0,0,255)

        x_min = min([min([x for (x,y) in canvas.keys()]) for canvas in canvases]) - MARGIN
        x_max = max([max([x for (x,y) in canvas.keys()]) for canvas in canvases]) + MARGIN
        y_min = min([min([y for (x,y) in canvas.keys()]) for canvas in canvases]) - MARGIN
        y_max = max([max([y for (x,y) in canvas.keys()]) for canvas in canvases]) + MARGIN

        width = x_max-x_min+1
        height = y_max-y_min+1
        origin = (-x_min,-y_min)

        images = []
        for canvas in canvases:

            image = Image.new("RGBA", (width, height),BACKGROUND_COLOR)

            pixels = image.load()

            for (i,j) in canvas.keys():
                pixels[i+origin[0],j+origin[1]] = palette[canvas[(i,j)]] # set the colour accordingly

            images.append(image)

        #FRAME_DURATION = 1000/60    #for true-to-NTSC attempts
        FRAME_DURATION = 20          #given GIF limitations, this seems like a good compromise
        durations = [int(FRAME_DURATION*pose.duration) for pose in self.poses]

        #scale
        images = [image.resize((zoom*width, zoom*height), Image.NEAREST) for image in images]

        if len(durations) > 1:
            images[0].save(filename, 'GIF', save_all=True, append_images=images[1:], duration=durations, transparency=0, disposal=2, loop=0)
        else:
            images[0].save(filename, transparency=0)





    def load_poses(self,num_poses):
        [upper_offset] = get_indexed_values(0x929263,self.index,0x02,'2')
        [lower_offset] = get_indexed_values(0x92945D,self.index,0x02,'2')

        upper_tilemap_offsets = get_indexed_values(0x92808D,upper_offset,0x02,'2'*num_poses)
        lower_tilemap_offsets = get_indexed_values(0x92808D,lower_offset,0x02,'2'*num_poses)

        [duration_list_location] = get_indexed_values(0x91B010,self.index,0x02,'2')
        duration_list_location += 0x910000

        duration_list = get_indexed_values(duration_list_location,0,0x02,'1'*num_poses)

        poses = []
        for pose_number in range(num_poses):
            upper_tilemap = get_tilemap(upper_tilemap_offsets[pose_number])
            lower_tilemap = get_tilemap(lower_tilemap_offsets[pose_number])
            
            poses.append( Pose(f"{self.ID},P{pose_number}", \
                          self.get_VRAM_data(pose_number), \
                          duration_list[pose_number],
                          upper_tilemap, \
                          lower_tilemap)
                        )

        return poses

    def get_VRAM_data(self, pose_number):
        [DMA_table_info_location] = get_indexed_values(0x92D94E,self.index,0x02,'2')
        DMA_table_info_location += 0x920000

        [upper_table_location,upper_index,lower_table_location,lower_index] = get_indexed_values(DMA_table_info_location,pose_number,0x04,'1111')

        [upper_DMA_table] = get_indexed_values(0x92D91E,upper_table_location,0x02,'2')
        [lower_DMA_table] = get_indexed_values(0x92D938,lower_table_location,0x02,'2')
        upper_DMA_table += 0x920000
        lower_DMA_table += 0x920000


        upper_graphics_data = get_indexed_values(upper_DMA_table,upper_index,0x07,'322')  
        lower_graphics_data = get_indexed_values(lower_DMA_table,lower_index,0x07,'322')  

        VRAM = load_virtual_VRAM(upper_graphics_data,lower_graphics_data)

        return VRAM


class Pose:
    def __init__(self, ID, VRAM, duration, upper_tilemap, lower_tilemap):
        self.ID = ID
        self.duration = duration
        self.VRAM = VRAM
        self.upper_tiles = self.get_tiles(upper_tilemap)
        self.lower_tiles = self.get_tiles(lower_tilemap)

    @property
    def tiles(self):
        return self.upper_tiles + self.lower_tiles

    def to_image(self,palette):
        #TODO: zoom
        canvas = self.to_canvas()

        width = 1+max([abs(x) for (x,y) in canvas.keys()])
        height = 1+max([abs(y) for (x,y) in canvas.keys()])
        
        image = Image.new("RGBA", (2*width, 2*height), (0, 0, 0))

        pixels = image.load()

        for (i,j) in canvas.keys():
            pixels[i+width,j+height] = palette[canvas[(i,j)]] # set the colour accordingly

        return image

    def to_canvas(self):
        canvas = {}
        for tile in self.tiles:
            canvas = tile.draw_on(canvas)
        return canvas

    def get_tiles(self, raw_tilemap):
        tiles = []
        for i,raw_tile in enumerate(raw_tilemap):
            tiles.append(Tile(f"{self.ID},T{i}",self.VRAM, raw_tile))
        return tiles


class Tile:
    def __init__(self, ID, VRAM, raw_tile):
        self.large = raw_tile[1] & 0x80 != 0x00    #what do bits 1 and 6 of raw_tile[1] do?
        self.ID = ID
        if self.large:
            self.addresses = [VRAM[raw_tile[3] + offset] for offset in [0x00,0x01,0x10,0x11]]
        else:
            self.addresses = [VRAM[raw_tile[3]]]
        self.auto_flag = raw_tile[1] & 0x01 != 0x00
        self.x_offset = convert_int_to_signed_int(raw_tile[0])# - (1 if self.auto_flag else 0)
        self.y_offset = convert_int_to_signed_int(raw_tile[2])
        self.h_flip = raw_tile[4] & 0x40 != 0x00
        self.v_flip = raw_tile[4] & 0x80 != 0x00
        self.priority = raw_tile[4] & 0x20 != 0x00
        self.palette = (raw_tile[4] >> 2) & 0b111

    def draw_on(self,canvas):
        if self.palette != 0b010:
            raise AssertionError(f"Received call to palette {self.palette} which is not implemented")

        if self.large:
            pass   #TODO

        for tile_no,addr in enumerate(self.addresses):
            chunk_offsets = [(0,0),(TILE_DIMENSION,0),(0,TILE_DIMENSION),(TILE_DIMENSION,TILE_DIMENSION)]
            pixels = self.retrieve_tile(addr)

            #TODO: implement flips for larger tiles
            #TODO: implement priority
            if self.h_flip:
                pixels = pixels[::-1]
                if self.large:
                    chunk_offsets = [(TILE_DIMENSION-x,y) for (x,y) in chunk_offsets]
            if self.v_flip:
                pixels = [row[::-1] for row in pixels]
                if self.large:
                    chunk_offsets = [(x,TILE_DIMENSION-y) for (x,y) in chunk_offsets]

            chunk_offset = chunk_offsets[tile_no]


            for i in range(TILE_DIMENSION):
                for j in range(TILE_DIMENSION):
                    if pixels[i][j] != 0:             #if not transparent_pixel
                        canvas[(i+self.x_offset+chunk_offset[0],j+self.y_offset+chunk_offset[1])] = pixels[i][j]
        return canvas

    def retrieve_tile(self, addr):
        raw_tile = rom[addr:addr+TILESIZE]
        pixels = [[0 for _ in range(TILE_DIMENSION)] for _ in range(TILE_DIMENSION)]
        for i in range(TILE_DIMENSION):
            for j in range(TILE_DIMENSION):
                for bit in range(2):            #bitplanes 1 and 2
                    index = i*2 + bit
                    amt_to_inc = (get_bit(raw_tile[index],TILE_DIMENSION-j-1)) * (0x01 << bit)
                    pixels[j][i] += amt_to_inc
                for bit in range(2):            #bitplanes 3 and 4
                    index = i*2 + bit + 2*TILE_DIMENSION
                    amt_to_inc = (get_bit(raw_tile[index],TILE_DIMENSION-j-1)) * (0x01 << (bit+2))
                    pixels[j][i] += amt_to_inc
              #notes in comments here are from https://mrclick.zophar.net/TilEd/download/consolegfx.txt
              # [r0, bp1], [r0, bp2], [r1, bp1], [r1, bp2], [r2, bp1], [r2, bp2], [r3, bp1], [r3, bp2]
              # [r4, bp1], [r4, bp2], [r5, bp1], [r5, bp2], [r6, bp1], [r6, bp2], [r7, bp1], [r7, bp2]
              # [r0, bp3], [r0, bp4], [r1, bp3], [r1, bp4], [r2, bp3], [r2, bp4], [r3, bp3], [r3, bp4]
              # [r4, bp3], [r4, bp4], [r5, bp3], [r5, bp4], [r6, bp3], [r6, bp4], [r7, bp3], [r7, bp4]
        return pixels











#######################################













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

def get_bit(byteval,idx):
    #https://stackoverflow.com/questions/2591483/getting-a-specific-bit-value-in-a-byte-string
    return ((byteval&(1<<idx))!=0)


def convert_to_rom_address(snes_addr):
    #convert from memory address to ROM address (lorom 0x80)
    bank = snes_addr // 0x10000 - 0x80
    offset = (snes_addr % 0x10000) - 0x8000

    if offset < 0x0000 or bank < 0x00:
        raise AssertionError(f"Function convert_to_rom_address() called on {hex(snes_addr)}, but this is not a valid SNES address.")
    
    new_address = bank*0x8000 + offset

    return new_address

def convert_int_to_signed_int(byte):
    if byte > 127:
        return (256-byte) * (-1)
    else:
        return byte


def load_virtual_VRAM(upper_graphics_data,lower_graphics_data):
    [upper_graphics_ptr,upper_top_row_amt,upper_bottom_row_amt] = upper_graphics_data
    [lower_graphics_ptr,lower_top_row_amt,lower_bottom_row_amt] = lower_graphics_data

    VRAM = [None] * 0x20    #initialize

    for i in range(upper_top_row_amt//TILESIZE):
        VRAM[i] = convert_to_rom_address(upper_graphics_ptr + i * TILESIZE)

    for i in range(lower_top_row_amt//TILESIZE):
        VRAM[0x08 + i] = convert_to_rom_address(lower_graphics_ptr + i * TILESIZE)

    for i in range(upper_bottom_row_amt//TILESIZE):
        VRAM[0x10 + i] = convert_to_rom_address(upper_graphics_ptr + upper_top_row_amt + i * TILESIZE)

    for i in range(lower_bottom_row_amt//TILESIZE):
        VRAM[0x18 + i] = convert_to_rom_address(lower_graphics_ptr + lower_top_row_amt + i * TILESIZE)

    return VRAM


def get_tilemap(offset):
    tilemap = []

    if offset != 0x00:             #offset can be zero for empty tilemaps (no tiles in this half of Samus body)
        tilemap_location = 0x920000+offset

        [tilemap_size] = get_indexed_values(tilemap_location,0,0x01,'2')

        for tile_number in range(tilemap_size):
            raw_tile = get_indexed_values(tilemap_location+(0x02+tile_number*0x05),0,0x01,'11111')
            tilemap.append(raw_tile)

    return tilemap


def load_rom_contents(rom_filename):
    with open(rom_filename, mode='rb') as file:
        rom = file.read()
    return rom



def main():
    data = Samus()
    raise AssertionError("Compiled utility library directly")
    
if __name__ == "__main__":
    main()