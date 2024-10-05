from source.meta.classes.spritelib import SpriteParent
from source.meta.classes import layoutlib
from source.meta.common import common
import json

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)

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
        aiming = split_string[1] if len(split_string) > 1 else ""
        direction = aiming if aiming else "right"

        ALTERNATIVES = {
            "diag_upright": "up",
            "diag_downright": "down",
            "diag_upleft": "up",
            "diag_downleft": "down",
            "left": "down",
            "right": "down"
        }

        while(direction not in direction_dict):
            if direction in ALTERNATIVES:
                direction = ALTERNATIVES[direction]
            else:
                direction = next(
                    iter(
                        [
                            x for x in list(
                                direction_dict.keys()
                            ) if "#" not in x
                        ]
                    )
                )
        return direction
