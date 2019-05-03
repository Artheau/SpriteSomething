import importlib
from ..gamelib import GameParent

class Game(GameParent):
	def __init__(self):
		super().__init__()
		self.name = "The Legend of Zelda: A Link to the Past"
		self.internal_name = "zelda3"
