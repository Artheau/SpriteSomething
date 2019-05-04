import importlib
from source.spritelib import SpriteParent
from . import rom_import, rom_export

class Sprite(SpriteParent):
	def __init__(self, filename, manifest_dict, my_subpath):
		super().__init__(filename, manifest_dict, my_subpath)

		self.overview_scale_factor = 1    #Samus's sheet is BIG, so don't zoom in on the overview


	def import_from_ROM(self, rom):
		#The history of the Samus import code is a story I will tell to my children
		self.images = rom_import.rom_import(self, rom)
		self.master_palette = list(self.images["palette_block"].getdata())

	def inject_into_ROM(self, rom):
		#The history of the Samus export code is a story I will tell to my grandchildren
		rom_export.rom_export(self, rom)

		
