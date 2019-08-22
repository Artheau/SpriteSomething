import json
import os
import urllib
from functools import partial
from source import common
from source.pluginslib import PluginsParent
from . import equipment

class Plugins(PluginsParent):
	def __init__(self):
		super().__init__()
		plugins = [
			("Equipment",None,partial(self.equipment_test,True))
		]
		self.set_plugins(plugins)

	def equipment_test(self, save=False):
		return equipment.equipment_test(save)
