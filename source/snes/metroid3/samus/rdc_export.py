import itertools
import io
from PIL import Image
from source.meta.common import common
from . import rom_inject

def get_raw_rdc_samus_block(sprite):
	block = io.BytesIO()

	block.write(dma_banks(sprite))
	block.write(death_bank("left",sprite))
	block.write(death_bank("right",sprite))
	block.write(gun_port(sprite))
	block.write(file_select(sprite))
	block.write(palettes(sprite))

	return block.getvalue()

def dma_banks(sprite):
	return bytes(itertools.chain.from_iterable(rom_inject.get_raw_pose(sprite,name) for name in sprite.layout.data["dma_sequence"]))

def death_bank(direction,sprite):
	length = 0x3F60
	image = rom_inject.compile_death_image(direction,sprite)
	return bytes(itertools.chain.from_iterable(common.convert_to_4bpp(image,(0,0),(0,16*i,128,16*(i+1)),None) for i in range(16)))[:length]

def gun_port(sprite):
	# Ten directions, times three levels of gun port opening.
	# Data is layed out according to their reference number
	data = bytearray()
	for n in range(30):
		image_name = sprite.layout.get_image_name("gun",n)
		data.extend(rom_inject.get_raw_pose(sprite,image_name))
	return data

def file_select(sprite):
	file_select_sprites = Image.new("P",(128,24),0)

	for image_name,src,dest in [
		("file_select_head",        None,         (  0, 0)),
		("file_select_head1",       None,         ( 24, 0)),
		("file_select_head2",       None,         ( 48, 0)),
		("file_select_visor",       None,         ( 72, 0)),
		("file_select_visor1",      None,         ( 88, 0)),
		("file_select_visor2",      None,         (104, 0)),
		("file_select_visor3",      None,         ( 72, 8)),
		("file_select_visor4",      None,         ( 88, 8)),
		("file_select_cursor_array",( 0,24, 8,32),(112,16)),
		("file_select_cursor_array",( 0,16, 8,24),(112, 8)),
		("file_select_cursor_array",( 0, 8, 8,16),(120, 0)),
		("file_select_cursor_array",( 8, 8,16,16),(120, 8)),
		("file_select_cursor_array",( 8,16,16,24),(120,16)),
		("file_select_piping",      ( 0, 0,24, 8),( 72,16)),   # Top
		("file_select_piping",      (16, 8,24,24),(104, 8)),   # Side
		("file_select_piping",      ( 0,16, 8,24),( 96,16)),   # Corner
	]:
		source_image = sprite.images[image_name]
		source_image = source_image.crop(src) if src else source_image
		file_select_sprites.paste(source_image,dest)

	cursor_array = sprite.images["file_select_cursor_array"]
	file_select_missile = cursor_array.crop(( 0, 0, 8, 8))
	file_select_missile_head = cursor_array.crop(( 8,24,16,32))

	data = bytearray()
	# Due to how convert_to_4bpp package the data we must first get a whole sheet row, then extract the third row (first 0x200 bytes)
	data.extend(common.convert_to_4bpp(file_select_sprites,     (0,0),(0, 0,128,16),None))
	data.extend(common.convert_to_4bpp(file_select_sprites,     (0,0),(0,16,128,32),None)[:0x200])
	data.extend(common.convert_to_4bpp(file_select_missile,     (0,0),(0, 0,  8, 8),None))
	data.extend(common.convert_to_4bpp(file_select_missile_head,(0,0),(0, 0,  8, 8),None))
	return data

# Palettes are stored as just fifteen colors, not sixteen.
# For some of the palettes the timer is in the spot normally taken by color 0
def palettes(sprite):
	data = bytearray()

	every = lambda p: p
	all_rev = lambda p: p[::-1]
	first = lambda p: p[:1]
	index_3 = lambda p: p[3:4]
	first_14 = lambda p: p[:14]
	first_15 = lambda p: p[:15]
	last = lambda p: p[-1:]
	last_15 = lambda p: p[-15:]

	palette_manifest = [
		("power",  "standard",    first,  [(first_15,range(1))]),
		("varia",  "standard",    first,  [(first_15,range(1))]),
		("gravity","standard",    first,  [(first_15,range(1))]),
		("power",  "loader",      every    [(first_15,[0x00,0x01,0x48,0x49,0x4E,0x4F,0x54,0x55,0x58])]),
		("varia",  "loader",      every    [(first_15,[0x00,0x01,0x48,0x49,0x4E,0x4F,0x54,0x55,0x58])]),
		("gravity","loader",      every    [(first_15,[0x00,0x01,0x48,0x49,0x4E,0x4F,0x54,0x55,0x58])]),
		("power",  "heat",        every    [(last_15, range(16))]),
		("varia",  "heat",        every    [(last_15, range(16))]),
		("gravity","heat",        every    [(last_15, range(16))]),
		("power",  "charge",      every    [(first_15,range(8))]),
		("varia",  "charge",      every    [(first_15,range(8))]),
		("gravity","charge",      every    [(first_15,range(8))]),
		("power",  "speed boost", every    [(first_15,range(4))]),
		("varia",  "speed boost", every    [(first_15,range(4))]),
		("gravity","speed boost", every    [(first_15,range(4))]),
		("power",  "speed squat", every    [(first_15,range(4))]),
		("varia",  "speed squat", every    [(first_15,range(4))]),
		("gravity","speed squat", every    [(first_15,range(4))]),
		("power",  "shinespark",  every    [(first_15,range(4))]),
		("varia",  "shinespark",  every    [(first_15,range(4))]),
		("gravity","shinespark",  every    [(first_15,range(4))]),
		("power",  "screw attack",every    [(first_15,range(4))]),
		("varia",  "screw attack",every    [(first_15,range(4))]),
		("gravity","screw attack",every    [(first_15,range(4))]),
		("power",  "flash",       every    [(first_15,range(6))]),
		("power",  "death",       every    [(first_15,range(9))]),
		("power",  "hyper",       all_rev,[(first_15,range(10))]),
		("power",  "sepia",       first,  [(first_15,range(1))]),
		("power",  "sepia hurt",  first,  [(first_15,range(1))]),
		("power",  "xray",        every    [(index_3, range(3))]),
		("power",  "door",        first,  [(index_3, range(1))]),
		("power",  "file select", first,  [(first_15,range(1))]),
		("ship",   "intro",       first,  [(first_15,range(1))]),
		("ship",   "outro",       every    [(first_15,range(16))]),
		("ship",   "standard",    every    [(first_14,range(1)),      # first 14 colors
		                                   (last,    range(14))]),   # 15th color is underglow
	]

	for category,pose,palette_set,data_sets in palette_manifest:
		palettes = [pal for _,pal in palette_set(sprite.get_timed_palette(category,pose))]
		for color_set,indices in data_sets:
			colors_555 = [common.convert_to_555(color_set(pal)) for pal in palettes]
			data.extend(itertools.chain.from_iterable([common.as_u16(c) for i in indices for c in colors_555[i]]))

	return data
