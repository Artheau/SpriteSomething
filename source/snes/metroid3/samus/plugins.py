import json
import os
import urllib
from functools import partial
from source.meta.common import common
from source.meta.gui import gui_common
from source.meta.classes.pluginslib import PluginsParent
from source.meta.plugins import trawler
from . import equipment

# FIXME: English
class Plugins(PluginsParent):
	def __init__(self):
		super().__init__()
		plugins = [
			("Download SpriteSomething Unofficial Sprites",None,self.get_spritesomething_sprites),
			("Sheet Trawler",None,self.sheet_trawler)#,
#			("Equipment",None,partial(self.equipment_test,True))
		]
		self.set_plugins(plugins)

	def equipment_test(self, save=False):
		return equipment.equipment_test(save)

	def get_spritesomething_sprites(self):
		success = gui_common.get_sprites(
			self,
			"Unofficial SpriteSomething Super Metroid/Samus",
			"snes/metroid3/samus/sheets/unofficial",
			"https://miketrethewey.github.io/SpriteSomething-collections/snes/metroid3/samus/sprites.json"
		)
		return success

	def sheet_trawler(self):
		animations = json.load(open(common.get_resource(os.path.join("snes","metroid3","samus","manifests"),"animations.json")))
		frames_by_animation = {}
		animations_by_frame = {}
		for ani,dirs in animations.items():				# {"Stand": {"right": [...], "up": [...]}}
			if "$schema" not in ani:
				if ani not in frames_by_animation:
					frames_by_animation[ani] = {}
				for direction,poses in dirs.items():	# {"right": [{"frames": 0, "tiles": [{"image": "cellID"}]}]}
					poseID = 0
					if direction not in frames_by_animation[ani]:
						frames_by_animation[ani][direction] = {}
					for pose in poses:									# {"frames": 0, "tiles": [{"image": "cellID"}]}
						if poseID not in frames_by_animation[ani][direction]:
							frames_by_animation[ani][direction][poseID] = []
						if "tiles" in pose:
							for tile in pose["tiles"]:			# {"image": "cellID"}
								if "image" in tile:
									cellID = tile["image"]
									if "_shadow" not in cellID.lower() and \
										"SWORD" not in cellID and \
										"SHIELD" not in cellID:
										cell = {
											"id": cellID,
											"flip": tile["flip"].lower() if "flip" in tile else ""
										}
										if cellID not in animations_by_frame:
											animations_by_frame[cellID] = {}
										if ani not in animations_by_frame[cellID]:
											animations_by_frame[cellID][ani] = {}
										if direction not in animations_by_frame[cellID][ani]:
											animations_by_frame[cellID][ani][direction] = {}
										if poseID not in animations_by_frame[cellID][ani][direction]:
											animations_by_frame[cellID][ani][direction][poseID] = []
										frames_by_animation[ani][direction][poseID].append(cell)
										animations_by_frame[cellID][ani][direction][poseID].append(cell)
						poseID += 1
		trawler.show_trawler(frames_by_animation,animations_by_frame,True)
