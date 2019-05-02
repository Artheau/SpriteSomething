import importlib
from source.spritelib import SpriteParent

class Sprite(SpriteParent):
	def __init__(self, manifest_dict, my_subpath):
		super().__init__(manifest_dict, my_subpath)
		self.classic_name = "Samus"       #the original name, before the player replaces this sprite
		self.internal_name = "samus"      #the specific folder name that this app uses
