#common functions for all entities (i.e. "Sprites")
#sprites are responsible for maintaining their widgets
#they have to contain PIL images of all of their data, and the offset info, and how to assemble it
#and they have to interpret the global frame timer, and communicate back when to next check in

import random
import os
import json
import itertools
import importlib
import io
from functools import partial
from PIL import Image
from source import layoutlib
from source import common

class SpriteParent():
	#parent class for sprites to inherit
	def __init__(self, filename, manifest_dict, my_subpath):
		self.classic_name = manifest_dict["name"]    #e.g. "Samus" or "Link"
		self.resource_subpath = my_subpath           #the path to this sprite's subfolder in resources
		self.metadata = {"sprite.name": "","author.name":"","author.name-short":""}
		self.filename = filename
		self.plugins = None
		self.has_plugins = False
		self.layout = layoutlib.Layout(common.get_resource(self.resource_subpath,"layout.json"))
		with open(common.get_resource(self.resource_subpath,"animations.json")) as file:
			self.animations = json.load(file)
		self.import_from_filename()

	#to make a new sprite class, you must write code for all of the functions in this section below.
	############################# BEGIN ABSTRACT CODE ##############################

	def load_plugins(self):
		try:
			plugins_path,_ = os.path.split(self.resource_subpath)
			_,plugins_dir = os.path.split(plugins_path)
			plugins_module = importlib.import_module(f"source.{plugins_dir}.{self.classic_name.lower()}.plugins")
			self.plugins = plugins_module.Plugins()
			self.has_plugins = True
		except ModuleNotFoundError as err:
			print(err)

	def import_from_ROM(self, rom):
		#self.images, self.master_palette = ?, ?
		raise AssertionError("called import_from_ROM() on Sprite base class")

	def import_from_binary_data(self,pixel_data,palette_data):
		#self.images, self.master_palette = ?, ?
		raise AssertionError("called import_from_binary_data() on Sprite base class")

	def inject_into_ROM(self, rom):
		#return the injected ROM
		raise AssertionError("called export_to_ROM() on Sprite base class")

	def get_rdc_export_blocks(self):
		#return the binary blocks that are used to pack the RDC format
		raise AssertionError("called get_sprite_export_blocks() on Sprite base class")

	def get_current_palette(self, palette_type, default_range):
		#in most cases the child class will override this in order to provide functionality to things like spiffy buttons
		# and to implement dynamic palettes by leveraging self.frame_getter() to find the frame number

		#if the child class didn't tell us what to do, just go back to whatever palette it was on when it was imported
		return self.master_palette[default_range[0]:default_range[1]]

	############################# END ABSTRACT CODE ##############################

	#the functions below here are special to the parent class and do not need to be overwritten, unless you see a reason

	def import_from_filename(self):
		_,file_extension = os.path.splitext(self.filename)
		if file_extension.lower() == '.png':
			self.import_from_PNG()
		elif file_extension.lower() == '.zspr':
			self.import_from_ZSPR()
		elif file_extension.lower() in ['.sfc','.smc']:
			#dynamic import
			rom_path,_ = os.path.split(self.resource_subpath)
			_,rom_dir = os.path.split(rom_path)
			rom_module = importlib.import_module(f"source.{rom_dir}.rom")
			self.import_from_ROM(rom_module.RomHandler(self.filename))

	def import_from_PNG(self):
		self.images, self.master_palette = self.layout.extract_all_images_from_master(Image.open(self.filename))

	def import_from_ZSPR(self):
		with open(self.filename,"rb") as file:
			data = bytearray(file.read())

		if data[0:4] != bytes(ord(x) for x in 'ZSPR'):
			raise AssertionError("This file does not have a valid ZSPR header")
		if data[4] == 1:
			pixel_data_offset = int.from_bytes(data[9:13], byteorder='little', signed=False)
			pixel_data_length = int.from_bytes(data[13:15], byteorder='little', signed=False)
			palette_data_offset = int.from_bytes(data[15:19], byteorder='little', signed=False)
			palette_data_length = int.from_bytes(data[19:21], byteorder='little', signed=False)
			offset = 29
			'''
			 4 (header) +
			 1 (version) +
			 4 (checksum) +
			 4 (sprite data offset) +
			 2 (sprite data size) +
			 4 (pal data offset) +
			 2 (pal data size) +
			 2 (sprite type) +
			 6 (reserved)
			==
			29 (start of metadata)
			'''
			#I hate little endian so much.  So much.
			for key,byte_size in [("sprite.name",2),("author.name",2),("author.name-short",1)]:
				i = 0
				null_terminator = b"\x00"*byte_size
				while data[offset+i:offset+i+byte_size] != null_terminator:
					i += byte_size

				raw_string_slice = data[offset:offset+i]
				if byte_size == 1:
					self.metadata[key] = str(raw_string_slice,encoding="ascii")
				else:
					self.metadata[key] = str(raw_string_slice,encoding="utf-16-le")
				offset += i+byte_size   #have to add another byte_size to go over the null terminator

			pixel_data = data[pixel_data_offset:pixel_data_offset+pixel_data_length]
			palette_data = data[palette_data_offset:palette_data_offset+palette_data_length]
			self.import_from_binary_data(pixel_data,palette_data)
		else:
			raise AssertionError(f"No support is implemented for ZSPR version {int(data[4])}")


	def reload(self):
		#activated when the reload button is pressed.  Should reload the sprite from the file but not manipulate the buttons
		self.import_from_filename()
		self.update_overview_panel()
		#self.update_animation()

	def update_pose_number(self):
		if hasattr(self, "frame_progression_table"):
			mod_frames = self.frame_getter() % self.frame_progression_table[-1]
			self.pose_number = self.frame_progression_table.index(min([x for x in self.frame_progression_table if x > mod_frames]))

	def get_tiles_for_pose(self, animation, direction, pose_number, palettes):
		pose_list = self.get_pose_list(animation, direction)
		full_tile_list = []
		for tile_info in pose_list[pose_number]["tiles"][::-1]:
			base_image = self.images[tile_info["image"]]
			if "crop" in tile_info:
				base_image = base_image.crop(tuple(tile_info["crop"]))
			if "flip" in tile_info:
				hflip = "h" in tile_info["flip"].lower()
				vflip = "v" in tile_info["flip"].lower()
				if hflip and vflip:
					base_image = base_image.transpose(Image.ROTATE_180)
				elif hflip:
					base_image = base_image.transpose(Image.FLIP_LEFT_RIGHT)
				elif vflip:
					base_image = base_image.transpose(Image.FLIP_TOP_BOTTOM)

			#some poses have extra palette information, e.g. use "bunny" or "crystal_flash" palettes
			# which can (whole or in part) override certain parts of the palette specified in the argument
			if "palette" in pose_list[pose_number]:
				palettes.append(pose_list[pose_number]["palette"])

			default_range = self.layout.get_property("import palette interval", tile_info["image"])
			this_palette = self.get_current_palette(palettes, default_range)

			base_image = common.apply_palette(base_image, this_palette)

			full_tile_list.append((base_image,tile_info["pos"]))

		return full_tile_list

	def get_pose_list(self, animation, direction):
		direction_dict = self.animations[animation]
		if direction in direction_dict:
			return direction_dict[direction]
		else:
			return []

	def assemble_tiles_to_completed_image(self, tile_list):
		min_x = min([x for im,(x,y) in tile_list])
		min_y = min([y for im,(x,y) in tile_list])
		max_x = max([im.size[0]+x for im,(x,y) in tile_list])
		max_y = max([im.size[1]+y for im,(x,y) in tile_list])

		working_image = Image.new('RGBA',(max_x-min_x,max_y-min_y))
		for new_image,(x,y) in tile_list:
			working_image.paste(new_image,(x,y))    #TODO: need to mask this with an 'L' image so that transparency is honored
	
		return working_image,(min_x,min_y)

	def get_image(self, animation, direction, pose, palettes):
		#What I hope for this to do is to just retrieve a single PIL Image that corresponds to a particular pose in a particular animation using the specified list of palettes
		# e.g. get_image("Walk", "right", 2, ["red_mail", "master_sword"])
		#and it will return (Image, position_offset)
		tile_list = self.get_tiles_for_pose(animation, direction, pose, palettes)
		assembled_image = self.assemble_tiles_to_completed_image(tile_list)
		return assembled_image

	def frames_in_this_animation(self):
		return self.frame_progression_table[-1]

	def frames_left_in_this_pose(self):
		mod_frames = self.frame_getter() % self.frame_progression_table[-1]
		next_pose_at = min(x for x in self.frame_progression_table if x > mod_frames)
		return next_pose_at - mod_frames

	def frames_to_previous_pose(self):
		mod_frames = self.frame_getter() % self.frame_progression_table[-1]
		prev_pose_at = max((x for x in self.frame_progression_table if x <= mod_frames), default=0)
		return mod_frames - prev_pose_at + 1

	def save_as(self, filename):
		_,file_extension = os.path.splitext(filename)
		if file_extension.lower() == ".png":
			return self.save_as_PNG(filename)
		elif file_extension.lower() == ".zspr":
			return self.save_as_ZSPR(filename)
		elif file_extension.lower() == ".rdc":
			return self.save_as_RDC(filename)
		else:
			tk.messagebox.showerror("ERROR", f"Did not recognize file type \"{file_extension}\"")
			return False

	def save_as_PNG(self, filename):
		master_image = self.get_master_PNG_image()
		master_image.save(filename)
		return True

	def save_as_ZSPR(self, filename):
		#check to see if the functions exist (e.g. crashes hard if used on Samus)
		if hasattr(self, "get_binary_sprite_sheet") and hasattr(self, "get_binary_palettes"):
			sprite_sheet = self.get_binary_sprite_sheet()
			palettes = self.get_binary_palettes()
			HEADER_STRING = b"ZSPR"
			VERSION = 0x01
			SPRITE_TYPE = 0x01   #this format has "1" for the player sprite
			RESERVED_BYTES = b'\x00\x00\x00\x00\x00\x00'
			QUAD_BYTE_NULL_CHAR = b'\x00\x00\x00\x00'
			DOUBLE_BYTE_NULL_CHAR = b'\x00\x00'
			SINGLE_BYTE_NULL_CHAR = b'\x00'

			write_buffer = bytearray()

			write_buffer.extend(HEADER_STRING)
			write_buffer.extend(common.as_u8(VERSION))
			checksum_start = len(write_buffer); write_buffer.extend(QUAD_BYTE_NULL_CHAR)
			sprite_sheet_pointer = len(write_buffer); write_buffer.extend(QUAD_BYTE_NULL_CHAR)
			write_buffer.extend(common.as_u16(len(sprite_sheet)))
			palettes_pointer = len(write_buffer); write_buffer.extend(QUAD_BYTE_NULL_CHAR)
			write_buffer.extend(common.as_u16(len(palettes)))
			write_buffer.extend(common.as_u16(SPRITE_TYPE))
			write_buffer.extend(RESERVED_BYTES)
			write_buffer.extend(self.metadata["sprite.name"].encode('utf-16-le'))
			write_buffer.extend(DOUBLE_BYTE_NULL_CHAR)
			write_buffer.extend(self.metadata["author.name"].encode('utf-16-le'))
			write_buffer.extend(DOUBLE_BYTE_NULL_CHAR)
			write_buffer.extend(self.metadata["author.name-short"].encode('ascii'))
			write_buffer.extend(SINGLE_BYTE_NULL_CHAR)
			write_buffer[sprite_sheet_pointer:sprite_sheet_pointer+4] = common.as_u32(len(write_buffer))
			write_buffer.extend(sprite_sheet)
			write_buffer[palettes_pointer:palettes_pointer+4] = common.as_u32(len(write_buffer))
			write_buffer.extend(palettes)

			checksum = (sum(write_buffer) + 0xFF + 0xFF) % 0x10000
			checksum_complement = 0xFFFF - checksum

			write_buffer[checksum_start:checksum_start+2] = common.as_u16(checksum)
			write_buffer[checksum_start+2:checksum_start+4] = common.as_u16(checksum_complement)

			with open(filename, "wb") as zspr_file:
				zspr_file.write(write_buffer)

			return True       #report success to caller
		else:
			return False      #report failure to caller

	def save_as_RDC(self, filename):
		raw_author_name = self.metadata["author.name-short"]
		author = raw_author_name.encode('utf8') if raw_author_name else bytes()
		HEADER_STRING = b"RETRODATACONTAINER"
		VERSION = 0x01

		blocks_with_type = self.get_rdc_export_blocks()
		number_of_blocks = len(blocks_with_type)

		preample_length = len(HEADER_STRING) + 1
		block_list_length = 4 + number_of_blocks * 8
		author_field_length = len(author) + 1
		block_offset = preample_length + block_list_length + author_field_length

		with open(filename, "wb") as rdc_file:
			rdc_file.write(HEADER_STRING)
			rdc_file.write(common.as_u8(VERSION))
			rdc_file.write(common.as_u32(number_of_blocks))
			for block_type,block in blocks_with_type:
				rdc_file.write(common.as_u32(block_type))
				rdc_file.write(common.as_u32(block_offset))
				block_offset += len(block)
			rdc_file.write(author)
			rdc_file.write(common.as_u8(0))

			for _,block in blocks_with_type:
				rdc_file.write(block)

		return True   #indicate success to caller

	def export_frame_as_PNG(self, filename):
		#i = 0
		for tile,_ in self.get_tiles_for_current_pose():
			new_size = tuple(int(dim*self.zoom_getter()) for dim in tile.size)
			img_to_save = Image.new("RGBA", new_size, 0)
			img_to_save = tile.resize(new_size,resample=Image.NEAREST)
			#filename = filename[:filename.rfind('.')] + str(i) + filename[filename.rfind('.'):]
			img_to_save.save(filename)
			#i += 1

	def export_animation_as_collage(self, filename, orientation="horizontal"):
		image_names = []
		image_list = []
		poses = self.get_current_pose_list()
		for pose in poses:
			tiles = pose["tiles"]
			for tile in tiles:
				image_names.append(tile["image"])

		for i,row in enumerate(self.layout.get_rows()): #FIXME: i unused variable

			for image_name in row:   #for every image referenced explicitly in the layout
				if image_name in image_names:
					image = self.images[image_name]

					xmin,ymin,xmax,ymax = self.layout.get_bounding_box(image_name)
					if not image:    #there was no image there to grab, so make a blank image
						image = Image.new("RGBA", (xmax-xmin,ymax-ymin), 0)

					palette = self.layout.get_property("import palette interval", image_name)
					palette = self.master_palette[palette[0]:palette[1]] if palette else []

					image = common.apply_palette(image, palette)
					bordered_image, origin = self.layout.add_borders_and_scale(image, (-xmin,-ymin), image_name)
					image_list.append((bordered_image, origin))

		collage = None
		if orientation == "horizontal":
			# HORIZONTAL
			collage = self.layout.make_horizontal_collage(image_list)
		elif orientation == "vertical":
			# VERTICAL
			raise NotImplementedError()
		collage.save(filename)

	def get_master_PNG_image(self):
		return self.layout.export_all_images_to_PNG(self.images,self.master_palette)

	def update_overview_panel(self):
		image = self.get_master_PNG_image()
		scaled_image = image.resize(tuple(int(x*self.overview_scale_factor) for x in image.size))

		if hasattr(self,"overview_ID") and self.overview_ID is not None:
			del self.overview_image
			self.overview_image = common.get_tk_image(scaled_image)
			self.overview_canvas.itemconfig(self.overview_ID, image=self.overview_image)
		else:
			import time
			scaled_image = scaled_image.copy()
			self.overview_image = common.get_tk_image(scaled_image)
			self.overview_ID = self.overview_canvas.create_image(0, 0, image=self.overview_image, anchor=tk.NW)
