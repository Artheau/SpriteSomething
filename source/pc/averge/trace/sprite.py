from source.meta.classes.spritelib import SpriteParent
from source.meta.classes import layoutlib
from source.meta.common import common
import json

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.overhead = False     #Trace is sideview, so only left/right direction buttons should show

    def import_from_ROM(self, rom):
        pass

    def import_from_binary_data(self,pixel_data,palette_data):
        pass

    def inject_into_ROM(self, rom):
        pass

    def get_rdc_export_blocks(self):
        pass

    def get_palette(self, palettes, default_range, frame_number):
        pass

    def get_alternative_direction(self, animation, direction):
        #suggest an alternative direction, which can be referenced if the original direction doesn't have an animation
        direction_dict = self.animations[animation]
        split_string = direction.split("_aim_")
        facing = split_string[0]
        aiming = split_string[1] if len(split_string) > 1 else ""

        #now start searching for this facing and aiming in the JSON dict
        #start going down the list of alternative aiming if a pose does not have the original
        ALTERNATIVES = {
            "up": "diag_up",
            "diag_up": "shoot",
            "down": "diag_down",
            "diag_down": "shoot"
        }
        while(self.concatenate_facing_and_aiming(facing,aiming) not in direction_dict):
            if aiming in ALTERNATIVES:
                aiming = ALTERNATIVES[aiming]
            elif facing in direction_dict:     #no aim was available, try the pure facing
                return facing
            else:        #now we are really screwed, so just do anything
                print("Aiming: %s" % (aiming))
                print("Facing: %s" % (facing))
                print("Alternative: %s" % (ALTERNATIVES[aiming] if aiming in ALTERNATIVES else ""))
                if isinstance(direction_dict,dict):
                    print("Direction Dict: %s" % (direction_dict.keys()))
                else:
                    print("Direction Dict: %s" % (direction_dict))
                return next(
                    iter(
                        [
                            x for x in list(
                                direction_dict.keys()
                            ) if "#" not in x
                        ]
                    )
                )

        #if things went well, we are here
        return "_aim_".join([facing,aiming])

    def concatenate_facing_and_aiming(self, facing, aiming):
        return "_aim_".join([facing,aiming])
