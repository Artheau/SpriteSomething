import json
import os
import urllib
from functools import partial
from source.meta.common import common
from source.meta.gui import gui_common
from source.meta.classes.pluginslib import PluginsParent
from . import pseudoimages

# FIXME: English
class Plugins(PluginsParent):
    def __init__(self):
        super().__init__()
        plugins = [
            ("Download SpriteSomething Unofficial Sprites",None,self.get_spritesomething_sprites)
        ]
        self.set_plugins(plugins)

    def pseudoimages_test(self, save=False):
        return pseudoimages.pseudoimages_test(save)

    def get_spritesomething_sprites(self):
        success = gui_common.get_sprites(
            self,
            "Unofficial SpriteSomething FFMQ/Dark King",
            "snes/ffmq/darkking/sheets/unofficial",
            "https://miketrethewey.github.io/SpriteSomething-collections/snes/ffmq/darkking/sprites.json"
        )
        return success
