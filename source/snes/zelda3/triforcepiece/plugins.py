import json
import os
from source.meta.classes.pluginslib import PluginsParent
from source.snes.zelda3.link import equipment

# FIXME: English

class Plugins(PluginsParent):
    def __init__(self):
        super().__init__()
        plugins = [
        ]
        self.set_plugins(plugins)

    def equipment_test(self, save=False):
        return equipment.equipment_test(save)
