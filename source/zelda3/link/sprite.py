import importlib
import itertools
from PIL import Image
from source import common
from source import widgetlib
from string import ascii_uppercase
from source.spritelib import SpriteParent

class Sprite(SpriteParent):
	def __init__(self, filename, manifest_dict, my_subpath):
		super().__init__(filename, manifest_dict, my_subpath)

		# self.plugins = [
		# 	("Sheet Trawler",None)
		#	("Tracker Images",None)
		# ]

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

	def get_spiffy_buttons(self, parent):
		spiffy_buttons = widgetlib.SpiffyButtons(self, parent)

		mail_group = spiffy_buttons.make_new_group("Mail")
		mail_group.add_blank_space()
		mail_group.add("green", "Green Mail", "mail-1.png")
		mail_group.add("blue", "Blue Mail", "mail-2.png")
		mail_group.add("red", "Red Mail", "mail-3.png")
		mail_group.add("bunny", "Bunny Palette", "mail-4.png")

		sword_group = spiffy_buttons.make_new_group("Sword")
		sword_group.add("none", "No Sword", "no-thing.png")
		sword_group.add("fighter", "Fighter's Sword", "sword-1.png")
		sword_group.add("master", "Master Sword", "sword-2.png")
		sword_group.add("tempered", "Tempered Sword", "sword-3.png")
		sword_group.add("gold", "Gold Sword", "sword-4.png")

		shield_group = spiffy_buttons.make_new_group("Shield")
		shield_group.add("none", "No Sword", "no-thing.png")
		shield_group.add("fighter", "Fighter's Shield", "shield-1.png")
		shield_group.add("fire", "Fire Shield", "shield-2.png")
		shield_group.add("mirror", "Mirror Shield", "shield-3.png")

		gloves_group = spiffy_buttons.make_new_group("Gloves")
		gloves_group.add("none", "No Sword", "no-thing.png")
		gloves_group.add("power", "Power Glove", "gloves-1.png")
		gloves_group.add("titan", "Titan's Mitt", "gloves-2.png")

		return spiffy_buttons
