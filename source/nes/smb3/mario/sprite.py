import json
import os
from typing import Tuple

from PIL import Image

from source.meta.classes.spritelib import SpriteParent
from source.meta.common import common
from source.nes.colors import find_closest_color_index
from source.nes.romhandler import RomHandlerParent


class Sprite(SpriteParent):
    def __init__(self, filename, manifest_dict, my_subpath, _):
        super().__init__(filename, manifest_dict, my_subpath, _)
        self.load_plugins()

        self.mario_globals = {}
        self.mario_globals["mario_palette"] = [
            # (  0,  0,  0),
            (  0,  0,  0),  # outline
            (178, 50, 38),  # shirt color
            (254,206,199),  # skin color
        ]
        self.mario_globals["luigi_palette"] = [
            # (  0,  0,  0),
            (  0,  0,  0),  # outline
            ( 98,226, 64),  # shirt color
            (254,206,199),  # skin color
        ]
        self.mario_globals["fire_palette"] = [
            # (  0,  0,  0),
            (178, 50, 38),  # outline
            (232,157, 52),  # shirt color
            (254,206,199),  # skin color
        ]
        self.mario_globals["tanooki_palette"] = [
            # (  0,  0,  0),
            (  0,  0,  0),  # outline
            (152, 78, 15),  # tanooki costume
            (254,206,199),  # skin color
            ( 99, 99, 99),  # tanooki statue "dark"
        ]
        self.mario_globals["tanooki_statue_palette"] = [
            # (  0,  0,  0),
            (  0,  0,  0),  # outline
            ( 99, 99, 99),  # tanooki statue "dark"
            (173,173,173),  # tanooki statue "light"
        ]
        self.mario_globals["hammer_palette"] = [
            # (  0,  0,  0),
            (  0,  0,  0),  # outline
            (255,255,255),  # hammer "light"
            (232,157, 52),  # hammer "skin"
        ]
        self.mario_globals["global_palette"] = [
            # (  0,  0,  0),
            (  0,  0,  0),  # outline
            (255,255,255),  # body color
        ]

    def import_from_ROM(self, rom: RomHandlerParent):
        # TODO: prob move logic to a separate class, similar to how importing from PNG does it
        layout_filename = common.get_resource(
            os.path.join(
                self.resource_subpath,
                "manifests"
            ),
            "rom_layout.json")
        with open(layout_filename, "r") as file:
            layout = json.loads(file.read())

        # Extract the palette first
        self.master_palette = []

        for palette_offset in layout["palette"].values():
            rgba_palette = rom.read_rgba_palette(palette_offset)
            self.master_palette.extend(rgba_palette)

        palette_image = Image.new("RGB", (4, 1), (0, 0, 0, 0))
        palette_image.putdata(self.master_palette)
        self.images["palette_block"] = palette_image

        self.images["null_block"] = Image.new("RGB", (0, 0))

        # Now extract the images
        chr_offset = layout["settings"]["address_offset"]
        pattern = layout["settings"]["pattern"]

        for name, pose in layout["poses"].items():
            pose_palette = self.master_palette[(pose["palette"] * 4): (pose["palette"] * 4 + 4)]

            tiles = pose["tiles"]
            pose_image = Image.new("RGBA", self._get_blocks_size(tiles), (0, 0, 0, 0))

            for tile in tiles:
                tile_offset = chr_offset + tile["offset"] * 16
                tile_image = rom.read_tiles_to_image(tile_offset, pose_palette, tile["length"], pattern)
                (tile_x, tile_y) = tile["position"]
                pose_image.paste(tile_image, (tile_x * 8, tile_y * 8))

            self.images[name] = pose_image

    def inject_into_ROM(self, spiffy_dict, rom: RomHandlerParent):
        # Inject palette data
        all_palette_data = list(self.images.get("palette_block").getdata())

        palette_offsets = [
            0x10539,  # mario small/big/tail
        ]

        for i, palette_offset in enumerate(palette_offsets):
            palette_data = all_palette_data[(4 * i):(4 * i + 4)]
            color_index_data = [find_closest_color_index(x) for x in palette_data]
            rom.write(palette_offset, color_index_data)

        # Inject chr data
        for image_name, image in self.images.items():
            # TODO: do the thing
            pass

        return rom

    def get_palette(self, palettes, default_range=[], frame_number=0):
        palette_indices = None
        this_palette = []
        range_end = 8
        for i in range(1,range_end):
            this_palette.append((0,0,0))

        for scheme in [
            "mario",
            "luigi",
            "fire",
            "frog",
            "tanooki",
            "tanooki_statue",
            "hammer",
            "global"
        ]:
            check = f"{scheme}_brother"
            if check in palettes:
                if scheme == "frog":
                    scheme = "luigi"
                this_palette = self.mario_globals[f"{scheme}_palette"]

        if len(this_palette) < 1:
            palette_indices = list(range(1,range_end))     #start with normal mail and modify it as needed

        if palette_indices:
            for i,_ in enumerate(palette_indices):
                this_palette[i] = self.master_palette[palette_indices[i]]

        return this_palette

    def import_from_PNG(self):
        with Image.open(self.filename) as master:
            self.images, self.master_palette = self.layout.extract_all_images_from_master(master)

    def _get_blocks_size(self, blocks) -> Tuple[int, int]:
        # TODO: implement and find better place
        return 24, 32
