import struct
from enum import Enum

class BlockType(Enum):
	LinkSprite = 1
	SamusSprite = 4

def create(author,rdc,*blocks):
	author = author.encode('utf8') if author else bytes()
	header_format = b"RETRODATACONTAINER"
	version = 0x01

	block_nrs = len(blocks)
	blocks = [(block_type.value,data) for block_type,data in blocks]
	
	preample_length = len(header_format) + 1
	block_list_length = 4 + block_nrs * 8
	author_field_length = len(author) + 1
	block_offset = preample_length + block_list_length + author_field_length

	rdc.write(header_format)
	rdc.write(as_u8(version))

	rdc.write(as_u32(block_nrs))
	write_inner_block_list(rdc,block_offset,blocks)

	rdc.write(author)
	rdc.write(as_u8(0))

	for _,data in blocks:
		rdc.write(data)

def write_inner_block_list(rdc,block_offset,blocks):
	for block_type,data in blocks:
		rdc.write(as_u32(block_type))
		rdc.write(as_u32(block_offset))
		block_offset += len(data)

def as_u8(value):
	return struct.pack('B',value)

def as_u16(value):
	return struct.pack('<H',value)

def as_u32(value):
	return struct.pack('<L',value)
