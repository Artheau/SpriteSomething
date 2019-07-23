import importlib			#for dynamic imports
import itertools
import json						#for reading JSON
import os							#for filesystem manipulation
import io							#for filesystem manipution
import urllib.request	#for downloading stuff
from PIL import Image
from source import common
from source import widgetlib
from string import ascii_uppercase
from source.spritelib import SpriteParent

class Sprite(SpriteParent):
	def __init__(self, filename, manifest_dict, my_subpath):
		super().__init__(filename, manifest_dict, my_subpath)

		self.plugins += [
			("Download Official Sprites",None,self.get_alttpr_sprites),
			("Sheet Trawler","plugins-sprite-sheet-trawler",None),
			("Tracker Images",None,None)
		]

	def import_from_ROM(self, rom):
		pixel_data = rom.bulk_read_from_snes_address(0x108000,0x7000)    #the big Link sheet
		palette_data = rom.bulk_read_from_snes_address(0x1BD308,120)     #the palettes
		palette_data.extend(rom.bulk_read_from_snes_address(0x1BEDF5,4)) #the glove colors
		self.import_from_binary_data(pixel_data,palette_data)

	def import_from_binary_data(self,pixel_data,palette_data):
		self.master_palette = [(0,0,0) for _ in range(0x40)]   #initialize the palette
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

	def inject_into_ROM(self, rom):
		#should work for the combo rom, VT rando, and the (J) rom.  Not sure about the (U) rom...maybe?

		#the sheet needs to be placed directly into address $108000-$10F000
		for i,row in enumerate(itertools.chain(ascii_uppercase, ["AA","AB"])):  #over all 28 rows of the sheet
			for column in range(8):    #over all 8 columns
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

	def get_spiffy_buttons(self, parent, fish):
		spiffy_buttons = widgetlib.SpiffyButtons(self, parent)

		mail_group = spiffy_buttons.make_new_group("mail", fish)
		mail_group.adds([
			(None,"",None), #a blank space, baby
			("green","mail-green.png",True),
			("blue","mail-blue.png",False),
			("red","mail-red.png",False)
		],fish)

		sword_group = spiffy_buttons.make_new_group("sword", fish)
		sword_group.adds([
			("none","no-thing.png",True),
			("fighter","sword-fighters.png",False),
			("master","sword-master.png",False),
			("tempered","sword-tempered.png",False),
			("gold","sword-butter.png",False)
		],fish)

		shield_group = spiffy_buttons.make_new_group("shield", fish)
		shield_group.adds([
			("none","no-thing.png",True),
			("fighter","shield-fighters.png",False),
			("fire","shield-fire.png",False),
			("mirror","shield-mirror.png",False)
		],fish)

		gloves_group = spiffy_buttons.make_new_group("gloves", fish)
		gloves_group.adds([
			("none","no-thing.png",True),
			("power","glove1.png",False),
			("titan","glove2.png",False)
		],fish)

		return spiffy_buttons

	def get_current_palette(self, palette_type, default_range):
		if self.spiffy_buttons_exist:
			if palette_type == "bunny":
				palette_indices = range(0x31,0x40)   #use the bunny colors, skipping the transparency color
			else:
				palette_indices = list(range(1,16))   #start with green mail and modify it as needed
				mail_type = self.mail_var.get() if hasattr(self,"mail_var") else ""
				gloves_type = self.gloves_var.get() if hasattr(self,"gloves_var") else ""
				for i in range(0,len(palette_indices)):

					if gloves_type != "none" and palette_indices[i] == 0x0D:
						if gloves_type == "power":
							palette_indices[i] = 0x10
						elif gloves_type == "titan":
							palette_indices[i] = 0x20
						else:
							raise AssertionError(f"unknown gloves type given by spiffy buttons: '{gloves_type}'")

					elif mail_type != "green" and palette_indices[i] in range(0,16):
						if mail_type == "blue":
							palette_indices[i] += 16
						elif mail_type == "red":
							palette_indices[i] += 32
						else:
							raise AssertionError(f"unknown mail type given by spiffy buttons: '{mail_type}'")
		else:
			#do whatever the parent would do as a default
			return super().get_current_palette(palette_type, default_range)

		return [self.master_palette[i] for i in palette_indices]

	#download ALttPR sprites
	def get_alttpr_sprites(self):
		success = False	#report success
		official = os.path.join('.',"resources","zelda3","link","official")	#save to resources/zelda3/link/official/*.zspr
		if not os.path.exists(official):
			os.makedirs(official)	#make it if we don't have it

		#make the request!
		alttpr_sprites_filename = "http://alttpr.com/sprites"
		alttpr_sprites_req = urllib.request.urlopen(alttpr_sprites_filename)
		alttpr_sprites = json.loads(alttpr_sprites_req.read().decode("utf-8"))
		#get an iterator and a counter for a makeshift progress bar
		i = 0
		total = len(alttpr_sprites)
		print("   Downloading Official ALttPR Sprites")
		for sprite in alttpr_sprites:
			sprite_filename = sprite["file"][sprite["file"].rfind('/')+1:]	#get the filename
			sprite_destination = os.path.join(official,sprite_filename)	#set the destination
			i += 1	#iterate iterator
			if not os.path.exists(sprite_destination):	#if we don't have it, download it
				with open(sprite_destination, "wb") as g:
					sprite_data_req = urllib.request.urlopen(sprite["file"])
					sprite_data = sprite_data_req.read()
					print("    Writing " + str(i).rjust(len(str(total))) + '/' + str(total) + ": " + sprite_filename)
					g.write(sprite_data)
					success = True
			else:	#if we do have it, next!
				print("    Skipping " + str(i).rjust(len(str(total))) + '/' + str(total) + ": " + sprite_filename)
		return success

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