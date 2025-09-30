import json
import os
from tkinter import messagebox
from functools import partial
from source.meta.common import common
from source.meta.gui import gui_common
from source.meta.classes.pluginslib import PluginsParent
from source.meta.plugins import trawler
from . import equipment

# FIXME: English

class Plugins(PluginsParent):
	def __init__(self):
		super().__init__()
		plugins = [
			# ("Download ALttPR Official Sprites",None,self.get_alttpr_sprites),
			# ("Download SpriteSomething Unofficial Sprites",None,self.get_spritesomething_sprites),
			# ("Sheet Trawler",None,self.sheet_trawler)#,
			#("Equipment",None,self.equipment_test)
		]
		# self.set_plugins(plugins)

	def equipment_test(self, save=False):
		return equipment.equipment_test(save)

	def get_alttpr_sprites(self):
		success = gui_common.get_sprites(
			self,
			"Official ALttPR",
			"snes/zelda3/link/sheets/official",
			"http://alttpr.com/sprites"
		)
		return success

	def get_spritesomething_sprites(self):
		success = gui_common.get_sprites(
			self,
			"Unofficial SpriteSomething ALttP/Link",
			"snes/zelda3/link/sheets/unofficial",
			"https://miketrethewey.github.io/SpriteSomething-collections/snes/zelda3/link/sprites.json"
		)
		return success

