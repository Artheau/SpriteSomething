import importlib
import io
import itertools
import json
from PIL import Image
from source.meta.classes.spritelib import SpriteParent
from source.meta.common import common

class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.load_plugins()

        self.link_globals = {
          "greyscale_mail": [
            (190,190,190),  # lt mail
            (255,255,255),  # skin
            (117,117,117),  # dk mail
          ]
        }

    def import_cleanup(self):
        '''
        Post-import cleanup
        '''
        self.load_plugins()
        self.equipment = self.plugins.equipment_test(True)
        if hasattr(self, "images"):
            self.images["transparent"] = Image.new("RGBA",(0,0),0)
            self.images = dict(self.images,**self.equipment)

    def get_rdc_export_blocks(self):
        Z1LINK_EXPORT_BLOCK_TYPE = 2
        block = io.BytesIO()
        for image_names in [
            ["liftingItem"],            # 0
            ["walk1ProfileBigshield"],  # 1
            [                           # 2
                "walk1Profile",
                "walk2Profile",
                "facingDownNoShield",
                "facingUp",
                "attackingProfile",
                "attackingDown",
                "attackingUp"
            ],
            ["walk2ProfileBigshield"],  # 3
            [                           # 4
                "walk1DownSmallshield",
                "walk2DownSmallshield"
            ],
            ["facingDownBigshield"]     # 5
        ]:
            block.write(self.get_binary_sprite_sheet(image_names))
        block.write(self.get_binary_palettes()) # 6,7,8,9
        return [(Z1LINK_EXPORT_BLOCK_TYPE, block.getvalue())]

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
                if "blue_mail" in palettes:
                    #skip to second set
                    palette_indices[i] += range_end * 1
                if "red_mail" in palettes:
                    #skip to third set
                    palette_indices[i] += range_end * 2

        if palette_indices:
            for i,_ in enumerate(palette_indices):
                this_palette[i] = self.master_palette[palette_indices[i]]

        if "greyscale_mail" in palettes:
            this_palette = self.link_globals["greyscale_mail"]

        return this_palette

    def get_binary_sprite_sheet(self, image_names):
        if isinstance(image_names, str):
            image_names = [image_names]

        top_half_of_rows = bytearray()
        bottom_half_of_rows = bytearray()

        for image_name in image_names:
            image = self.images[image_name]
            raw_image = common.convert_image_to_4bpp(
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
            "green_mail",
            "blue_mail",
            "red_mail"
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
