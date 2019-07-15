import itertools
import struct
from string import ascii_uppercase
from source import common

def rdc_export(sprite,author,rdc):
	author = author.encode('utf8') if author else bytes()
	header_format = b"RETRODATACONTAINER"
	version = 0x01

	blocks = 1;
	block_type = 0x01
	block_offset = len(header_format) + 1 + 3 * 4 + len(author) + 1

	rdc.write(header_format)
	rdc.write(as_u8(version))

	rdc.write(as_u32(blocks))
	rdc.write(as_u32(block_type))
	rdc.write(as_u32(block_offset))

	rdc.write(author)
	rdc.write(as_u8(0))

	rdc.write(sprite_sheet(sprite))

	rdc.write(palettes(sprite))

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

def as_u8(value):
	return struct.pack('B',value)

def as_u16(value):
	return struct.pack('<H',value)

def as_u32(value):
	return struct.pack('<L',value)
