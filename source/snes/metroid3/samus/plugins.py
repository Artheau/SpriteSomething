import json
import os
import urllib
from functools import partial
from source.meta.common import common
from source.meta.gui import gui_common
from source.meta.classes.pluginslib import PluginsParent
from . import equipment

# FIXME: English
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
			"snes/metroid3/samus/sheets/unofficial",
			"https://raw.githubusercontent.com/miketrethewey/SpriteSomething-collections/gh-pages/snes/metroid3/samus/sprites.json"
#			"https://raw.githubusercontent.com/Artheau/SpriteSomething/gh-pages/resources/app/snes/metroid3/samus/sprites.json"
		)
		return success
