import importlib
import itertools
import json
from PIL import Image
from source.meta.classes.spritelib import SpriteParent
from source.meta.common import common

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.overhead = False
        self.samus_globals = {
            "loader1_palette": [
                (142,  0,117),  # helmet
                (  0, 69,  0),  # visor
                (125,  8,  0),  # suit
                (  0,  0,  0),  # bg
            ],
            "loader2_palette": [
                (170,  0, 16),  # helmet
                (  0, 69,  0),  # visor
                (203, 77, 12),  # suit
                (  0,  0,  0),  # bg
            ],
            "loader3_palette": [
                (166,  0,  0),  # helmet
                (  0, 81,  0),  # visor
                (255,117, 97),  # suit
                (  0,  0,  0),  # bg
            ],
            "screw1_palette": [ # blue
                ( 32, 56,239),  # helmet
                (255,255,255),  # visor
                ( 60,190,255),  # suit
                (  0,  0,  0),  # bg
            ],
            "screw2_palette": [ # orange
                (255,154, 56),  # helmet
                (219, 40,  0),  # visor
                (255,255,255),  # suit
                (  0,  0,  0),  # bg
            ],
            "screw3_palette": [ # power
                (219, 40,  0),  # helmet
                ( 77,223, 73),  # visor
                (255,219,170),  # suit
                (  0,  0,  0),  # bg
            ]
        }

    def get_alternative_direction(self, animation, direction):
        # suggest an alternative direction, which can be referenced if the original direction doesn't have an animation
        alt_direction = None
        direction_dict = self.animations[animation]
        split_string = direction.split("_aim_")
        facing = split_string[0]
        aiming = split_string[1] if len(split_string) > 1 else ""

        # now start searching for this facing and aiming in the JSON dict
        # start going down the list of alternative aiming if a pose does not have the original
        ALTERNATIVES = {
        }
        while(self.concatenate_facing_and_aiming(facing,aiming) not in direction_dict):
            if aiming in ALTERNATIVES:
                aiming = ALTERNATIVES[aiming]
                # print(f"FOUND ALTERNATIVE, {aiming}")
            elif facing in direction_dict:     #no aim was available, try the pure facing
                alt_direction = facing
                # print(f"USING FACING, {facing}")
                break
            elif len(direction_dict.keys()) > 0:   #now we are really screwed, so just do anything
                alt_direction = next(
                    iter(
                        [
                            x for x in list(
                                direction_dict.keys()
                            ) if "#" not in x
                        ]
                    )
                )
                # print(f"USING FIRST, {alt_direction}")
                break
            else:
                #we couldn't find anything, abort
                break

        # if things went well, we are here
        if alt_direction is None:
            alt_direction = "_aim_".join([facing,aiming])
            # print(f"CONCATING Facing & Aiming, {alt_direction}")
        # print(f"{facing},{aiming},{alt_direction}")
        return alt_direction

    def concatenate_facing_and_aiming(self, facing, aiming):
        return "_aim_".join([facing,aiming])

    def get_palette(self, palettes, default_range=[], frame_number=0):
        '''
        Get palette based on input strings and frame number
        '''
        palette_indices = None
        this_palette = []
        range_end = 4
        for i in range(1,range_end):
            this_palette.append((0,0,0))

        #start with power suit and modify as needed
        palette_indices = list(range(1,range_end))
        for i,_ in enumerate(palette_indices):
            if palette_indices[i] in range(0,range_end):
                if "varia_suit" in palettes:
                    #skip to third row
                    palette_indices[i] += 8
                if "yes_missile-mode" in palettes:
                    #skip to next row
                    palette_indices[i] += 4

        if palette_indices:
            for i,_ in enumerate(palette_indices):
                this_palette[i] = self.master_palette[palette_indices[i]]

        for i in range(1,4):
            for check in [f"loader{i}", f"screw{i}"]:
                if f"{check}_variant" in palettes:
                    if f"{check}_palette" in self.samus_globals:
                        this_palette = self.samus_globals[f"{check}_palette"]

        this_palette = [(0,0,0)] + this_palette

        return this_palette

    def get_binary_sprite_sheet(self, image_names):
        if isinstance(image_names, str):
            image_names = [image_names]

        top_half_of_rows = bytearray()
        bottom_half_of_rows = bytearray()

        for image_name in image_names:
            image = self.images[image_name]
            raw_image = common.convert_to_4bpp(
                image,
                (0,0),
                (0,0,image.size[0],image.size[1]),
                None
            )
            top_half_of_rows += bytes(raw_image[:0x40])
            bottom_half_of_rows += bytes(raw_image[0x40:])

        return bytes(b for row_offset in range(0,len(top_half_of_rows),0x200) \
                         for b in top_half_of_rows[
                            row_offset:row_offset+0x200
                        ]+
                        bottom_half_of_rows[
                            row_offset:row_offset+0x200
                        ]
                    )

    def get_binary_palettes(self, palette_name=""):
        '''
        Get binary palettes
        '''
        raw_palette_data = bytearray()
        colors_555 = common.convert_to_555(self.master_palette)

        palette_names = [
            "normal_colors",
            "varia_colors",
            "missile_colors",
            "varia_missile_colors"
        ]

        start = 0
        end = len(palette_names)
        if palette_name != "":
            if palette_name in palette_names:
                start = palette_names.index(palette_name)
                end = start + 1

        # Mail palettes
        raw_palette_data.extend(
            itertools.chain.from_iterable(
                [
                    common.as_u16(
                        c
                    )
                    for i in range(start, end)
                    for c in colors_555[
                        0x10*i+1:0x10*i+0x10
                    ]
                ]
            )
        )

        return raw_palette_data
