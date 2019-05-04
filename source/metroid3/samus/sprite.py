import importlib
from source.spritelib import SpriteParent

class Sprite(SpriteParent):
	def __init__(self, filename, manifest_dict, my_subpath):
		super().__init__(filename, manifest_dict, my_subpath)

		self.overview_scale_factor = 1    #Samus's sheet is BIG, so don't zoom in on the overview
		
