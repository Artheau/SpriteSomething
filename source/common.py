import tkinter as tk
import os
import numpy as np
from PIL import Image
import base64
from io import BytesIO    #for shenanigans


def get_all_resources(desired_filename, subdir=None):
	#gets the file from overrides AND resources (returns a list of filenames)
	file_list = []
	for directory in ["overrides","resources"]:
		if subdir: directory = os.path.join(directory,subdir)
		if os.path.isdir(directory):
			for filename in os.listdir(directory):
				if filename == desired_filename:
					file_list.append(os.path.join(directory,filename))
	return file_list

def get_resource(desired_filename, subdir=None):
	#gets the file from overrides.  If not there, then from resources.
	file_list = get_all_resources(desired_filename,subdir=subdir)
	return file_list[0] if file_list else None

def gather_all_from_resource_subdirectory(subdir):
	#gathers all the filenames from a subdirectory in resources,
	# and then also throws in all the filenames from the same subdirectory in overrides
	#does not recurse
	file_list = []
	for directory in ["resources","overrides"]:
		directory = os.path.join(directory,subdir)
		if os.path.isdir(directory):
			for filename in os.listdir(directory):
				if os.path.isfile(os.path.join(directory,filename)):
					file_list.append(filename)    #just the filename, not the path, so that this overrrides correctly
	return file_list

def apply_palette(image, palette):
	if image.mode == "P":
		flat_palette = [0 for _ in range(3*256)]
		flat_palette[3:3*len(palette)+3] = [x for color in palette for x in color]
		alpha_mask = image.point(lambda x: 0 if x==0 else 1,mode="1")
		image.putpalette(flat_palette)
		image = image.convert('RGBA')
		image.putalpha(alpha_mask)
	return image

def get_tk_image(image):
	#needed because the tkImage.PhotoImage conversion is SO slow for big images.  Like, you don't even know.
	#LET THE SHENANIGANS BEGIN
	buffered = BytesIO()
	image.save(buffered, format="GIF")
	img_str = base64.b64encode(buffered.getvalue())
	return tk.PhotoImage(data=img_str)

def convert_555_to_rgb(color, recurse=True):
	#converts either a single color or a list of colors in 555 format to their RGB 3-tuple equivalents
	try:
		iter(color)
	except TypeError:
		FIVE_BITS = 0b100000
		red = 8*(color % FIVE_BITS)
		green = 8*((color//FIVE_BITS) % FIVE_BITS)
		blue = 8*((color//(FIVE_BITS*FIVE_BITS)) % FIVE_BITS)
		return (red,green,blue)
	#else it is iterable
	if recurse:
		return [convert_555_to_rgb(x,recurse=False) for x in color]
	else:
		raise AssertionError("convert_555_to_rgb() called with doubly-iterable argument")

def image_from_raw_data(tilemaps, DMA_writes, bounding_box):
	#expects:
	#  a list of tilemaps in the 5 byte format: essentially [X position, size+Xmsb, Y, index, palette]
	#  a dictionary consisting of writes to the DMA and what should be there

	canvas = {}

	for tilemap in tilemaps:
		#tilemap[0] and the 0th bit of tilemap[1] encode the X offset
		x_offset = tilemap[0] - (0x100 if (tilemap[1] & 0x01) else 0)

		#tilemap[1] also contains information about whether the tile is 8x8 or 16x16
		big_tile = (tilemap[1] & 0xC2 == 0xC2)

		#tilemap[2] contains the Y offset
		y_offset = (tilemap[2] & 0x7F) - (0x80 if (tilemap[2] & 0x80) else 0)

		#tilemap[3] contains the index of which tile to grab (or tiles in the case of a 16x16)
		index = tilemap[3]

		#tilemap[4] contains palette info, priority info, and flip info
		v_flip = tilemap[4] & 0x80
		h_flip = tilemap[4] & 0x40
		#priority = (tilemap[4] //0x10) % 0b100                   #TODO: implement a priority system
		palette = (tilemap[4] //2) % 0b1000

		def draw_tile_to_canvas(new_x_offset, new_y_offset, new_index):
			tile_to_write = convert_tile_from_bitplanes(DMA_writes[new_index])
			if h_flip:
			   tile_to_write = np.flipud(tile_to_write)
			if v_flip:
			   tile_to_write = np.fliplr(tile_to_write)
			for (i,j), value in np.ndenumerate(tile_to_write):
				if value != 0:   #if not transparent
					canvas[(new_x_offset+i,new_y_offset+j)] = int(value)

		if big_tile:   #draw all four 8x8 tiles
			draw_tile_to_canvas(x_offset+(8 if h_flip else 0),y_offset+(8 if v_flip else 0),index       )
			draw_tile_to_canvas(x_offset+(0 if h_flip else 8),y_offset+(8 if v_flip else 0),index + 0x01)
			draw_tile_to_canvas(x_offset+(8 if h_flip else 0),y_offset+(0 if v_flip else 8),index + 0x10)
			draw_tile_to_canvas(x_offset+(0 if h_flip else 8),y_offset+(0 if v_flip else 8),index + 0x11)
		else:
			draw_tile_to_canvas(x_offset,y_offset,index)

	tight_image,(x0,y0) = to_image(canvas)
	cropped_image = tight_image.crop((bounding_box[0]+x0,bounding_box[1]+y0,bounding_box[2]+x0,bounding_box[3]+y0))

	return cropped_image

def to_image(canvas):

	if canvas.keys():
		x_min = min([x for (x,y) in canvas.keys()])
		y_min = min([y for (x,y) in canvas.keys()])
		x_max = max([x for (x,y) in canvas.keys()])
		y_max = max([y for (x,y) in canvas.keys()])

		x_min = min(x_min,0)
		y_min = min(y_min,0)
		x_max = max(x_max,0)
		y_max = max(y_max,0)

		width = x_max-x_min+1
		height = y_max-y_min+1

		image = Image.new("P", (width, height), 0)

		pixels = image.load()

		for (i,j),value in canvas.items():
			pixels[(i-x_min,j-y_min)] = value

	else:                #the canvas is empty
		image = Image.new("P", (1,1), 0)
		x_min,y_min = 0,0

	return image, (-x_min, -y_min)

def convert_tile_from_bitplanes(raw_tile):
	#an attempt to make this ugly process mildly efficient
	tile = np.zeros((8,8), dtype=np.uint8)

	tile[:,4] = raw_tile[31:15:-2]
	tile[:,5] = raw_tile[30:14:-2]
	tile[:,6] = raw_tile[15::-2]
	tile[:,7] = raw_tile[14::-2]

	shaped_tile = tile.reshape(8,8,1)

	tile_bits = np.unpackbits(shaped_tile, axis=2)
	fixed_bits = np.packbits(tile_bits, axis=1)
	returnvalue = fixed_bits.reshape(8,8)
	returnvalue = returnvalue.swapaxes(0,1)
	returnvalue = np.fliplr(returnvalue)
	return returnvalue

