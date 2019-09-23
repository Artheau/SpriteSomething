from source.meta.common import common

class PluginsParent():
	def __init__(self):
		self.plugins = []

	def get_plugins(self):
		return self.plugins

	def set_plugins(self, plugins):
		self.plugins = plugins
