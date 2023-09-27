import json
import os
from source.meta.common import common
from source.meta.plugins import trawler

def sheet_trawler():
	animations = json.load(open(common.get_resource(os.path.join("snes","zelda3","link","manifests"),"animations.json")))
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
										"flip": tile["flip"].lower() if "flip" in tile else "",
										"crop": tile["crop"] if "crop" in tile else ""
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
	trawler.show_trawler(frames_by_animation,animations_by_frame,False)
