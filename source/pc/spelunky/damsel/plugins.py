import json
import os
import urllib
from functools import partial
from source.meta.common import common
from source.meta.gui import gui_common
from source.meta.classes.pluginslib import PluginsParent

#FIXME: English
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
			"Unofficial SpriteSomething Spelunky/Damsel",
			"pc/spelunky/damsel/sheets/unofficial",
			"https://raw.githubusercontent.com/Artheau/SpriteSomething/gh-pages/resources/app/pc/spelunky/damsel/sprites.json"
		)
		return success
