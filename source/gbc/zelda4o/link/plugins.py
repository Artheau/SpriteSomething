import json
import os
from tkinter import messagebox
from functools import partial
from source.meta.common import common
from source.meta.gui import gui_common
from source.meta.classes.pluginslib import PluginsParent

from .plugin import ips

# FIXME: English

class Plugins(PluginsParent):
    def __init__(self):
        super().__init__()
        plugins = [
            ("Output IPS Patches",None,partial(ips.doTheThing, "linkwhite.png")),
        ]
        self.set_plugins(plugins)
