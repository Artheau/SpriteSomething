import json
import os
import urllib
from functools import partial
from source.meta.common import common
from source.meta.gui import gui_common
from source.meta.classes.pluginslib import PluginsParent

# FIXME: English
class Plugins(PluginsParent):
	def __init__(self):
		super().__init__()
		plugins = [
			("Download SpriteSomething Unofficial Sprites",None,self.get_spritesomething_sprites)
		]
		self.set_plugins(plugins)

	def get_spritesomething_sprites(self):
		success = gui_common.get_sprites(
			self,
			"Unofficial SpriteSomething Dragon Warrior/Loto-5",
			"nes/dragonwarrior/loto5/sheets/unofficial",
			"https://miketrethewey.github.io/SpriteSomething-collections/nes/dragonwarrior/loto5/sprites.json"
		)
		return success
