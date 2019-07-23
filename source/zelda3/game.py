import importlib
from ..gamelib import GameParent

class Game(GameParent):
	def __init__(self):
		super().__init__()
		#FIXME: Do we want to translate the game's display name?
		self.name = "The Legend of Zelda: A Link to the Past"
		self.internal_name = "zelda3"
