ROM_FILENAME_ARG_KEY = 'rom_filename'
PALETTE_ARG_KEY = 'palette_specified'
SUPERTILES_ARG_KEY = 'supertile_optimize'

TILESIZE = 0x20          #8x8 tiles with 4bpp = 0x20 bytes
TILE_DIMENSION = 0x08    #8x8 tiles
BACKGROUND_COLOR = '#000080'#36393f'

#FRAME_DURATION = 1000/60    #for true-to-NTSC attempts
FRAME_DURATION = 20          #given GIF limitations, this seems like a good compromise


SUPERTILE_JSON_FILENAME = "supertiles.json"


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