'''
Plugins
'''
from source.meta.classes.pluginslib import PluginsParent

class Plugins(PluginsParent):
    '''
    Plugins
    '''
    def __init__(self):
        super().__init__()
        plugins = []
        self.set_plugins(plugins)
