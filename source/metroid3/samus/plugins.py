import json
import os
import urllib
from functools import partial
from source import common
from source import gui_common
from source.pluginslib import PluginsParent
from . import equipment

#FIXME: English
class Plugins(PluginsParent):
	def __init__(self):
		super().__init__()
		plugins = [
			("Download SpriteSomething Unofficial Sprites",None,self.get_spritesomething_sprites)
#			("Equipment",None,partial(self.equipment_test,True))
		]
		self.set_plugins(plugins)

	def equipment_test(self, save=False):
		return equipment.equipment_test(save)

	def get_spritesomething_sprites(self):
		success = gui_common.get_sprites(
			self,
			"Unofficial SpriteSomething Samus",
			"metroid3/samus/sheets/unofficial",
			"https://raw.githubusercontent.com/Artheau/SpriteSomething/gh-pages/app_resources/metroid3/samus/sprites.json"
		)
		return success
