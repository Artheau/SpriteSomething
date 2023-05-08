from source.meta.classes.spritelib import SpriteParent

class Sprite(SpriteParent):
	def __init__(self, filename, manifest_dict, my_subpath, _):
		super().__init__(filename, manifest_dict, my_subpath, _)
		self.load_plugins()
