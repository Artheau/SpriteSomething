import json
import os
from tkinter import messagebox
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
			("Download ALttPR Official Sprites",None,self.get_alttpr_sprites),
			("Download SpriteSomething Unofficial Sprites",None,self.get_spritesomething_sprites),
			("Sheet Trawler",None,None)#
			#("Equipment",None,self.equipment_test)
		]
		self.set_plugins(plugins)

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
			"Unofficial SpriteSomething Link",
			"snes/zelda3/link/sheets/unofficial",
			"https://raw.githubusercontent.com/miketrethewey/SpriteSomething-collections/gh-pages/snes/zelda3/link/sprites.json"
#			"https://raw.githubusercontent.com/Artheau/SpriteSomething/gh-pages/resources/app/snes/zelda3/link/sprites.json"
		)
		return success
