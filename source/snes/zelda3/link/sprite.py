import importlib			#for dynamic imports
import itertools
import json						#for reading JSON
import os							#for filesystem manipulation
import io							#for filesystem manipution
import urllib.request	#for downloading stuff
from PIL import Image
from source.meta.common import common
from string import ascii_uppercase
from source.meta.classes.spritelib import SpriteParent

class Sprite(SpriteParent):
	def __init__(self, filename, manifest_dict, my_subpath):
		super().__init__(filename, manifest_dict, my_subpath)
		self.load_plugins()

		self.link_globals = {}
		self.link_globals["zap_palette"] = [
#				(	0,	0,	0),
				(	0,	0,	0),
				(208,184, 24),
				(136,112,248),
				(	0,	0,	0),
				(208,192,248),
				(	0,	0,	0),
				(208,192,248),

				(112, 88,224),
				(136,112,248),
				( 56, 40,128),
				(136,112,248),
				( 56, 40,128),
				( 72, 56,144),
				(120, 48,160),
				(192,128,240)
		]
		self.link_globals["sword_palette"] = [
			#blade, border, hilt
			[(248,248,248),(248,248, 72),(104,136,184)], #fighters
			[(112,144,248),(160,248,216),(168, 56, 56)], #master
			[(216, 72, 16),(248,160, 40),(104,160,248)], #tempered
			[(248,200,	0),(248,248,200),(	0,144, 72)]	#golden
		]

	def get_representative_images(self, style):
		return_images = []
		return_images += super().get_representative_images(style)

		if style == "crossproduct":
			return_images += self.get_tracker_images()
		elif style == "spiffy":
			return_images += self.get_spiffy_images(return_images)

		return return_images

	def get_tracker_images(self):
		return_images = []

		#cycle through mail levels
		for i,mail in enumerate(["green","blue","red"]):
			#get a container for tile lists
			tile_list = {}
			#get Bunny tile list for Stand:down to grab the bunny head
			tile_list["bunny"] = self.get_tiles_for_pose("Bunny stand","down",0,["bunny_mail"],0)
			#get Link tile list for File select for base
			tile_list["link"] = self.get_tiles_for_pose("File select","right",0,[mail + "_mail"],0)
			#get the bunny head
			bunny_head = tile_list["bunny"][2]
			#copy Link over Bunny
			tile_list["bunny"] = tile_list["link"] + []
			#set the bunny head
			tile_list["bunny"][1] = bunny_head

			#cycle through tile lists
			for tileset_id in tile_list:
				#make src image from tile list
				src_img,_ = self.assemble_tiles_to_completed_image(tile_list[tileset_id])
				#crop out the actual pixels
				src_img = src_img.crop((5,7,21,29))
				#make a new 32x32 transparent image
				dest_img = Image.new("RGBA",(32,32))
				#paste the pixels to (7,7)
				dest_img.paste(src_img,(7,6))
				#resize using nearest neighbor to 400% because that's what Cross' tracker uses
				dest_img = dest_img.resize((32*4,32*4),Image.NEAREST)
				#save to disk
				filename = "tunic"
				if tileset_id == "bunny":
					filename += "bunny"
				filename += str(i+1)
				filename += ".png"
				return_images.append((filename,dest_img))

		return return_images

	def get_spiffy_images(self, return_images):
		# FIXME: somehow get these from representative-images.json
		pose_coords = [
			(49,40),
			(75,30),
			(118,30),
			(160,31),
			(32,69),
			(138,67),
			(32,103),
			(67,88),
			(95,117),
			(126,107),
			(168,91),
			(24,146),
			(64,143),
			(104,161),
			(134,143)
		]
		# FIXME: somehow get this from representative-images.json
		bgfilename = "titlecard.png"

		if "sprite.name" in self.metadata and self.metadata["sprite.name"]:
			sprite_save_name = self.metadata["sprite.name"].lower()
		else:
			# FIXME: English
			sprite_save_name = "unknown"
		bgimg = Image.open(os.path.join(".","resources","app",self.resource_subpath,"sheets",bgfilename)).convert("RGBA")
		for i in range(0,len(return_images)):
			img = return_images[i][1]
			bgimg.paste(img,pose_coords[i],img)
		bgimg = bgimg.resize((bgimg.size[0] * 2, bgimg.size[1] * 2), Image.NEAREST)
		return_images.append(("-".join([sprite_save_name,bgfilename]),bgimg))

		return return_images

	def get_alternate_tile(self, image_name, palettes):
		slugs = {}
		found_alt = ""
		for palette in palettes:
			if '_' in palette:
				slugs[palette[palette.rfind('_')+1:]] = palette[:palette.rfind('_')]
		for item in ["SWORD","SHIELD"]:
			if image_name.startswith(item):
				if item.lower() in slugs:
					found_alt = True
					image_name = image_name.replace(item,slugs[item.lower()] + '_' + item.lower()) if not ("none_" + item.lower()) in palettes else "transparent"
		if "accessories" in slugs.keys():
			for item in [
				"BED",
				"BOOMERANG",
				"BOW",
				"BUGNET",
				"CANE",
				"HAMMER",
				"HOOK",
				"POWDER",
				"ROD",
				"SHALLOW_WATER",
				"SHOVEL",
				"SWAGDUCK",
				"TALL_GRASS"
				]:
				if image_name.startswith(item):
					found_alt = True
					image_name = image_name.lower() if (not "none_accessories" in palettes) else "transparent"
			for item,default in [
				("ITEM","pendant"),
				("CRYSTAL","crystal"),
				("BUSH_SHADOW","main_shadow")
				]:
				if image_name.startswith(item):
					found_alt = True
					image_name = default.lower() if (not "none_accessories" in palettes) else "transparent"
			for item in ["BUSH","BOOK"]:
				if image_name.startswith(item):
					found_alt = True
					image_name = item.lower() if (not "none_accessories" in palettes) else "transparent"
		if found_alt:
			return self.images[image_name]
		elif True:
			return Image.new("RGBA",(0,0),0)		#TODO: Track down why this function is being called without spiffy button info during sprite load
		else:
			# FIXME: English
			raise AssertionError(f"Could not locate tile with name {image_name}")

	def import_cleanup(self):
		self.load_plugins()
		self.images["transparent"] = Image.new("RGBA",(0,0),0)
		self.equipment = self.plugins.equipment_test(False)
		self.images = dict(self.images,**self.equipment)

	def import_from_ROM(self, rom):
		pixel_data = rom.bulk_read_from_snes_address(0x108000,0x7000)		#the big Link sheet
		palette_data = rom.bulk_read_from_snes_address(0x1BD308,120)		 #the palettes
		palette_data.extend(rom.bulk_read_from_snes_address(0x1BEDF5,4)) #the glove colors
		self.import_from_binary_data(pixel_data,palette_data)

	def import_from_binary_data(self,pixel_data,palette_data):
		self.master_palette = [(0,0,0) for _ in range(0x40)]	 #initialize the palette
		#main palettes
		converted_palette_data = [int.from_bytes(palette_data[i:i+2], byteorder='little') \
															for i in range(0,len(palette_data),2)]
		for i in range(4):
			palette = common.convert_555_to_rgb(converted_palette_data[0x0F*i:0x0F*(i+1)])
			self.master_palette[0x10*i+1:0x10*(i+1)] = palette
		#glove colors
		for i in range(2):
			glove_color = common.convert_555_to_rgb(converted_palette_data[-2+i])
			self.master_palette[0x10+0x10*i] = glove_color

		palette_block = Image.new('RGB',(8,8),0)
		palette_block.putdata(self.master_palette)
		palette_block = palette_block.convert('RGBA')

		self.images = {}
		self.images["palette_block"] = palette_block

		for i,row in enumerate(itertools.chain(ascii_uppercase, ["AA","AB"])):
			for column in range(8):
				this_image = Image.new("P",(16,16),0)
				image_name = f"{row}{column}"
				if image_name == "AB7":
					image_name = "null_block"
				for offset, position in [(0x0000,(0,0)),(0x0020,(8,0)),(0x0200,(0,8)),(0x0220,(8,8))]:
					read_pointer = 0x400*i+0x40*column+offset
					raw_tile = pixel_data[read_pointer:read_pointer+0x20]
					pastable_tile = common.image_from_bitplanes(raw_tile)
					this_image.paste(pastable_tile,position)
				self.images[image_name] = this_image

	def get_rdc_export_blocks(self):
		LINK_EXPORT_BLOCK_TYPE = 1
		block = io.BytesIO()
		block.write(self.get_binary_sprite_sheet())
		block.write(self.get_binary_palettes())
		return [(LINK_EXPORT_BLOCK_TYPE, block.getvalue())]

	def inject_into_ROM(self, spiffy_dict, rom):
		#should work for the combo rom, VT rando
		#should work for the (J) & (U) ROMs but won't automatically include the extra code needed to manage gloves, etc

		#this'll check VT rando Tournament Flag
		tournament_flag = rom.read(0x180213, 2) == 1
		#this'll check combo Tournament Flag
		if rom.type() == "EXHIROM" and not tournament_flag:
			config = rom.read_from_snes_address(0x80FF52, 2)
			fieldvals = {}
			fieldvals["gamemode"] = [ "singleworld", "multiworld" ]
			fieldvals["z3logic"] = [ "normal", "hard" ]
			fieldvals["m3logic"] = [ "normal", "hard" ]
			field = {}
			field["race"] = ((config & (1 << 15)) >> 15) > 0 # 1 bit
			field["keysanity"] = ((config & (0b11 << 13)) >> 13) > 0 # 2 bits
			field["gamemode"] = ((config & (1 << 12)) >> 12) # 1 bit
			field["z3logic"] = ((config & (0b11 << 10)) >> 10) # 2 bits
			field["m3logic"] = ((config & (0b11 << 8)) >> 8) # 2 bits
			field["version"] = {}
			field["version"]["major"] = ((config & (0b1111 << 4)) >> 4) # 4 bits
			field["version"]["minor"] = ((config & (0b1111 << 0)) >> 0) # 4 bits

			field["gamemode"] = fieldvals["gamemode"][field["gamemode"]]
			field["z3logic"] = fieldvals["z3logic"][field["z3logic"]]
			field["m3logic"] = fieldvals["m3logic"][field["m3logic"]]

			tournament_flag = field["race"]

		if tournament_flag:
			# FIXME: English
			raise AssertionError(f"Cannot inject into a Race/Tournament ROM!")
		else:
			#the sheet needs to be placed directly into address $108000-$10F000
			for i,row in enumerate(itertools.chain(ascii_uppercase, ["AA","AB"])):	#over all 28 rows of the sheet
				for column in range(8):		#over all 8 columns
					image_name = f"{row}{column}"
					if image_name == "AB7":
						#AB7 is special, because the palette block sits there in the PNG, so this can't be actually used
						image_name = "null_block"
					raw_image_data = common.convert_to_4bpp(self.images[image_name], (0,0), (0,0,16,16), None)

					rom.bulk_write_to_snes_address(0x108000+0x400*i+0x40*column,raw_image_data[:0x40],0x40)
					rom.bulk_write_to_snes_address(0x108200+0x400*i+0x40*column,raw_image_data[0x40:],0x40)

			#the palettes need to be placed directly into address $1BD308-$1BD380, not including the transparency or gloves colors
			converted_palette = common.convert_to_555(self.master_palette)
			for i in range(4):
				rom.write_to_snes_address(0x1BD308+0x1E*i,converted_palette[0x10*i+1:0x10*i+0x10],0x0F*"2")
			#the glove colors are placed into $1BEDF5-$1BEDF8
			for i in range(2):
				rom.write_to_snes_address(0x1BEDF5+0x02*i,converted_palette[0x10+0x10*i],2)

		return rom

	def get_palette(self, palettes, default_range, frame_number):
		palette_indices = None
		this_palette = []
		for i in range(1,16):
			this_palette.append((0,0,0))

		if "zap_mail" in palettes:
			this_palette = self.link_globals["zap_palette"]
		elif "bunny_mail" in palettes:
			palette_indices = range(0x31,0x40)	 #use the bunny colors, skipping the transparency color
		else:
			palette_indices = list(range(1,16))	 #start with green mail and modify it as needed
			for i in range(0,len(palette_indices)):

				if palette_indices[i] == 0x0D:
					if "power_gloves" in palettes:
						palette_indices[i] = 0x10
					elif "titan_gloves" in palettes:
						palette_indices[i] = 0x20

				if palette_indices[i] in range(0,16):
					if "blue_mail" in palettes:
						palette_indices[i] += 16
					elif "red_mail" in palettes:
						palette_indices[i] += 32

		if palette_indices:
			for i in range(0,len(palette_indices)):
				this_palette[i] = self.master_palette[palette_indices[i]]

		return this_palette

	def get_binary_sprite_sheet(self):
		top_half_of_rows = bytearray()
		bottom_half_of_rows = bytearray()

		# 28 rows, 8 columns
		for image_name in [f"{row}{column}" for row in itertools.chain(ascii_uppercase, ["AA","AB"]) for column in range(8)]:
			# AB7 holds the palette block so use null_block instead
			image_name = image_name if image_name != "AB7" else "null_block"
			raw_image = common.convert_to_4bpp(self.images[image_name],(0,0),(0,0,16,16),None)
			top_half_of_rows += bytes(raw_image[:0x40])
			bottom_half_of_rows += bytes(raw_image[0x40:])

		return bytes(b for row_offset in range(0,len(top_half_of_rows),0x200) \
						 for b in top_half_of_rows[row_offset:row_offset+0x200]+bottom_half_of_rows[row_offset:row_offset+0x200])

	def get_binary_palettes(self):
		raw_palette_data = bytearray()
		colors_555 = common.convert_to_555(self.master_palette)

		# Mail and bunny palettes
		raw_palette_data.extend(itertools.chain.from_iterable([common.as_u16(c) for i in range(4) for c in colors_555[0x10*i+1:0x10*i+0x10]]))

		# Glove colors
		raw_palette_data.extend(itertools.chain.from_iterable([common.as_u16(colors_555[0x10*i+0x10]) for i in range(2)]))

		return raw_palette_data
