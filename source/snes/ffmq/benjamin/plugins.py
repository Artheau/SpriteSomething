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
			("Download SpriteSomething Unofficial Sprites",None,self.get_spritesomething_sprites),
			("Equipment",None,self.equipment_test)
		]
		self.set_plugins(plugins)

	def equipment_test(self, save=False):
		return equipment.equipment_test(save)

	def get_spritesomething_sprites(self):
		success = gui_common.get_sprites(
			self,
			"Unofficial SpriteSomething FFMQ/Benjamin",
			"snes/ffmq/benjamin/sheets/unofficial",
			"https://miketrethewey.github.io/SpriteSomething-collections/snes/ffmq/benjamin/sprites.json"
		)
		return success
