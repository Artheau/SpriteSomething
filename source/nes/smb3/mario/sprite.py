import json
import os
from typing import Tuple

from PIL import Image

from source.meta.classes.spritelib import SpriteParent
from source.meta.common import common
from source.nes.colors import find_closest_color_index
from source.nes.romhandler import RomHandlerParent


class Sprite(SpriteParent):
    images = {}
    master_palette = []

    def import_from_ROM(self, rom: RomHandlerParent):
        # TODO: prob move logic to a separate class, similar to how importing from PNG does it
        layout_filename = common.get_resource(os.path.join("nes", "smb3", "mario", "manifests"), "rom_layout.json")
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

    def import_from_PNG(self):
        with Image.open(self.filename) as master:
            self.images, self.master_palette = self.layout.extract_all_images_from_master(master)

    def _get_blocks_size(self, blocks) -> Tuple[int, int]:
        # TODO: implement and find better place
        return 24, 32
