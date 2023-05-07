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
		]
		self.set_plugins(plugins)
