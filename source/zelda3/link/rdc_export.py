import itertools
import io
from string import ascii_uppercase
from source import common, rdc_format
from source.rdc_format import BlockType, as_u16

def rdc_export(sprite,author,rdc):
	rdc_format.create(author,rdc,(BlockType.LinkSprite,link_data(sprite)))

def link_data(sprite):
	block = io.BytesIO()

	block.write(sprite_sheet(sprite))
	block.write(palettes(sprite))

	return block.getvalue()

def sprite_sheet(sprite):	
	upper = bytearray()
	lower = bytearray()

	# 28 rows, 8 columns
	for image_name in [f"{row}{column}" for row in itertools.chain(ascii_uppercase, ["AA","AB"]) for column in range(8)]:
		# AB7 holds the palette block so use null_block instead
		image_name = image_name if image_name != "AB7" else "null_block"
		data = common.convert_to_4bpp(sprite.images[image_name],(0,0),(0,0,16,16),None)
		upper += bytes(data[:0x40])
		lower += bytes(data[0x40:])

	return bytes(b for i in range(0,len(upper),0x200) for b in upper[i:i+0x200]+lower[i:i+0x200])

def palettes(sprite):
	data = bytearray()
	colors_555 = common.convert_to_555(sprite.master_palette)

	# Mail and bunny palettes
	data.extend(itertools.chain.from_iterable([as_u16(c) for i in range(4) for c in colors_555[0x10*i+1:0x10*i+0x10]]))

	# Glove colors
	data.extend(itertools.chain.from_iterable([as_u16(colors_555[0x10*i+0x10]) for i in range(2)]))

	return data
