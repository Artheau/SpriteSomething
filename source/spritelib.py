#common functions for all entities (i.e. "Sprites")
#sprites are responsible for maintaining their widgets
#they have to contain PIL images of all of their data, and the offset info, and how to assemble it
#and they have to interpret the global frame timer, and communicate back when to next check in

import tkinter as tk
import random
import os
import json
import itertools
import importlib
import io
from functools import partial
from PIL import Image, ImageTk
from source import ssTranslate as fish
from source import widgetlib
from source import layoutlib
from source import common

class SpriteParent():
	#parent class for sprites to inherit
	def __init__(self, filename, manifest_dict, my_subpath):
		self.classic_name = manifest_dict["name"]    #e.g. "Samus" or "Link"
		self.resource_subpath = my_subpath           #the path to this sprite's subfolder in resources
		self.metadata = {"sprite.name": "","author.name":"","author.name-short":""}
		self.filename = filename
		self.layout = layoutlib.Layout(common.get_resource("layout.json",subdir=self.resource_subpath))
		with open(common.get_resource("animations.json",subdir=self.resource_subpath)) as file:
			self.animations = json.load(file)
		self.import_from_filename()
		self.spiffy_buttons_exist = False
		self.overhead = True                         #by default, this will create NESW direction buttons.  If false, only left/right buttons

		self.overview_scale_factor = 2               #when the overview is made, it is scaled up by this amount
		self.plugins = []

	# def __del__(self):
	# 	tk.messagebox.showinfo("Notification", "I am destroyed")

	#to make a new sprite class, you must write code for all of the functions in this section below.
	############################# BEGIN ABSTRACT CODE ##############################

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

	def attach_metadata_panel(self,parent):
		PANEL_HEIGHT = 64
		metadata_section = tk.Frame(parent, name="metadata_section")
		row = 0
		for key in self.metadata.keys():
			label = fish.translate("meta",key,os.path.join("meta"))
			metadata_label = tk.Label(metadata_section, text=label, name=label.lower().replace(' ', '_'))
			metadata_label.grid(row=row,column=1)
			metadata_input = tk.Entry(metadata_section, name=label.lower().replace(' ', '_') + "_input")
			metadata_input.insert(0,self.metadata[key])
			metadata_input.grid(row=row,column=2)
			row += 1
		parent.add(metadata_section,minsize=PANEL_HEIGHT)

	def attach_animation_panel(self, parent, canvas, overview_canvas, zoom_getter, frame_getter, coord_getter):
		ANIMATION_DROPDOWN_WIDTH = 25
		PANEL_HEIGHT = 25
		self.canvas = canvas
		self.overview_canvas = overview_canvas
		self.zoom_getter = zoom_getter
		self.frame_getter = frame_getter
		self.coord_getter = coord_getter
		self.current_animation = None
		self.pose_number = None
		self.palette_number = None

		animation_panel = tk.Frame(parent, name="animation_panel")
		widgetlib.right_align_grid_in_frame(animation_panel)
		animation_label = tk.Label(animation_panel, text=fish.translate("meta","animations",os.path.join("meta")) + ':')
		animation_label.grid(row=0, column=1)
		self.animation_selection = tk.StringVar(animation_panel)

		self.animation_selection.set(random.choice(list(self.animations.keys())))

		animation_dropdown = tk.ttk.Combobox(animation_panel, state="readonly", values=list(self.animations.keys()), name="animation_dropdown")
		animation_dropdown.configure(width=ANIMATION_DROPDOWN_WIDTH, exportselection=0, textvariable=self.animation_selection)
		animation_dropdown.grid(row=0, column=2)
		self.set_animation(self.animation_selection.get())

		widgetlib.leakless_dropdown_trace(self, "animation_selection", "set_animation")

		parent.add(animation_panel,minsize=PANEL_HEIGHT)

		direction_panel, height = self.get_direction_buttons(parent).get_panel()
		parent.add(direction_panel, minsize=height)

		spiffy_panel, height = self.get_spiffy_buttons(parent).get_panel()
		self.spiffy_buttons_exist = True
		parent.add(spiffy_panel,minsize=height)

		palette_panel, height = self.get_palette_buttons(parent).get_panel()
		self.palette_buttons_exist = True
		parent.add(palette_panel,minsize=height)

		self.update_overview_panel()

		return animation_panel

	def reload(self):
		#activated when the reload button is pressed.  Should reload the sprite from the file but not manipulate the buttons
		self.import_from_filename()
		self.update_overview_panel()
		self.update_animation()

	def set_animation(self, animation_name):
		self.current_animation = animation_name
		self.update_animation()

	def update_pose_number(self):
		if hasattr(self, "frame_progression_table"):
			mod_frames = self.frame_getter() % self.frame_progression_table[-1]
			self.pose_number = self.frame_progression_table.index(min([x for x in self.frame_progression_table if x > mod_frames]))

	def get_tiles_for_current_pose(self):
		self.update_pose_number()
		pose_list = self.get_current_pose_list()
		full_tile_list = []
		for tile_info in pose_list[self.pose_number]["tiles"][::-1]:
			base_image = self.images[tile_info["image"]] #FIXME: Bombs if X-Ray is randomly chosen??? KEYERROR: xray_right0,xray_crouch_right0
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

			palette_type = pose_list[self.pose_number]["palette"] if "palette" in pose_list[self.pose_number] else None

			default_range = self.layout.get_property("import palette interval", tile_info["image"])
			this_palette = self.get_current_palette(palette_type, default_range)

			base_image = common.apply_palette(base_image, this_palette)

			full_tile_list.append((base_image,tile_info["pos"]))

		return full_tile_list

	def get_current_pose_list(self):
		direction_dict = self.animations[self.current_animation]
		if self.spiffy_buttons_exist:     #this will also indicate if the direction buttons exist
			if hasattr(self,"facing_var"):
				direction = self.facing_var.get().lower()   #grabbed from the direction buttons, which are named "facing"
				if direction in direction_dict:
					return direction_dict[direction]
		#otherwise just grab the first listed direction
		return next(iter(direction_dict.values()))

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

	def update_animation(self):
		pose_list = self.get_current_pose_list()
		if "frames" not in pose_list[0]:      #might not be a frame entry for static poses
			self.frame_progression_table = [1]
		else:
			self.frame_progression_table = list(itertools.accumulate([pose["frames"] for pose in pose_list]))

		if hasattr(self,"sprite_IDs"):
			for ID in self.sprite_IDs:
				self.canvas.delete(ID)       #remove the old tiles
		if hasattr(self,"active_tiles"):
			for tile in self.active_tiles:
				del tile                     #why this is not auto-destroyed is beyond me (memory leak otherwise)
		self.sprite_IDs = []
		self.active_tiles = []

		for tile,offset in self.get_tiles_for_current_pose():
			new_size = tuple(int(dim*self.zoom_getter()) for dim in tile.size)
			scaled_tile = ImageTk.PhotoImage(tile.resize(new_size,resample=Image.NEAREST))
			coord_on_canvas = tuple(int(self.zoom_getter()*(pos+x)) for pos,x in zip(self.coord_getter(),offset))
			self.sprite_IDs.append(self.canvas.create_image(*coord_on_canvas, image=scaled_tile, anchor = tk.NW))
			self.active_tiles.append(scaled_tile)     #if you skip this part, then the auto-destructor will get rid of your picture!

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

	#Mike likes spiffy buttons
	def get_spiffy_buttons(self, parent):
		#if this is not overriden by the child (sprite-specific) class, then there will be no spiffy buttons
		return widgetlib.SpiffyButtons(self, parent)

	#Mike likes palette buttons
	def get_palette_buttons(self, parent):
		#if this is not overridden by the child (sprite-specific) class, then there will be now palette buttons
		return widgetlib.SpiffyButtons(self, parent)

	#Art likes direction buttons
	def get_direction_buttons(self, parent):
		#if this is not overriden by the child (sprite-specific) class, then it will default to WASD layout for overhead, or just left/right if sideview (not overhead).
		direction_buttons = widgetlib.SpiffyButtons(self, parent, frame_name="direction_buttons", align="center")

		facing_group = direction_buttons.make_new_group("facing")
		if self.overhead:
			facing_group.add_blank_space()
			facing_group.add("up", "arrow-up.png")
			facing_group.add_blank_space()
			facing_group.add_newline()
		facing_group.add("left", "arrow-left.png")
		if self.overhead:
			facing_group.add("down", "arrow-down.png")
		facing_group.add("right", "arrow-right.png", default=True)

		return direction_buttons
