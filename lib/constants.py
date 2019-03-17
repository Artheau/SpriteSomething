USE_MODIFIED_ROM = True     #use the output of rom_modify.py to make animations/poses

APPLY_BUGFIXES = not USE_MODIFIED_ROM   #turn on to fix vanilla bugs, but off for my custom tilemaps

DEBUG_VRAM = False

IGNORED_ANIMATIONS = []

GIF_MARGIN = 0x08      #for exporting images, a margin this large is produced
PNG_MARGIN = 0x01


ROM_FILENAME_ARG_KEY = 'rom_filename'
SPRITE_SHEET_FILENAME_ARG_KEY = 'sprite_sheet_filename'
LAYOUT_FILENAME_ARG_KEY = 'layout_filename'
PALETTE_ARG_KEY = 'palette_specified'
SUPERTILES_ARG_KEY = 'supertile_optimize'

TILESIZE = 0x20          #8x8 tiles with 4bpp = 0x20 bytes
TILE_DIMENSION = 0x08    #8x8 tiles
BACKGROUND_COLOR = '#00007F'         #used to be Discord grey: '#36393f'

#FRAME_DURATION = 1000/60    #for true-to-NTSC attempts
FRAME_DURATION = 20          #given GIF limitations, this seems like a good compromise


SUPERTILE_JSON_FILENAME = "supertiles.json"
SUPERTILE_FRIENDLY_FILENAME = "supertiles_debug.txt"


#There is a bug in Pillow version 5.4.1 that does not display GIF transparency correctly
#It is because of Line 443 in GifImagePlugin.py not taking into account the disposal method
#Please help fix this
#https://github.com/python-pillow/Pillow/issues/3665
import PIL
if int(PIL.PILLOW_VERSION.split('.')[0]) <= 5:
    TRANSPARENCY = 255
    DISPOSAL = 0
else:
    TRANSPARENCY = 0
    DISPOSAL = 2




#address information
SAMUS_TILES_START = 0x9BCC00 #0x0DCC00 ROM
#SAMUS_TILES_START = 0x9C8000 #0x0DCC00 ROM
SAMUS_TILES_END = 0xA08000   #0x100000 ROM

TILEMAP_TABLE = 0x92808D
UPPER_TILEMAP_TABLE_POINTER = 0x929263
LOWER_TILEMAP_TABLE_POINTER = 0x92945D

SAMUS_TILEMAPS_START = 0x929700  #0x091700 ROM   #there is a little room before this, and also in a separate block a little before this
SAMUS_TILEMAPS_END = 0x92CB00  #0x094B00 ROM   #there is a little room after this (not much)

DMA_ENTRIES_START = 0x92CBEE  #0x94BEE ROM
DMA_ENTRIES_END = 0x92D910   #maybe a couple more bytes here but that's it.  No more room.

AFP_TABLE_ARRAY = 0x92D94E  #POSE POINTERS TO ANIMATION FRAME PROGRESSION TABLES

DMA_PAGESIZE = 0x20 #might be used for quick lookup, but more likely just the effective LSB for image number (MSB is page number)

UPPER_DMA_POINTER_TABLE = 0x92D91E
LOWER_DMA_POINTER_TABLE = 0x92D938