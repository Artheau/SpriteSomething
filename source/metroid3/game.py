import importlib
from ..gamelib import GameParent

class Game(GameParent):
	def __init__(self):
		super().__init__()
		self.name = "Super Metroid"    #to be replaced by a name like "Super Metroid"
		self.internal_name = "metroid3"        #to be replaced by the specific folder name that this app uses, e.g. "metroid3"
