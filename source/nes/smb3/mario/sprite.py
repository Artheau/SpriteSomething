from PIL import Image

from source.meta.classes.spritelib import SpriteParent
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
            ( 35, 77, 90),  # shirt color
            (254,206,199),  # skin color
        ]
        self.mario_globals["global_palette"] = [
            # (  0,  0,  0),
            (  0,  0,  0),
            ( 98,226, 64),  # frog
            (152, 78, 15),  # tanooki costume
            ( 99, 99, 99),  # tanooki statue "dark"
            (173,173,173),  # tanooki statue "skin/light"
            (255,255,255),  # hammer "light"
            (232,157, 52),  # hammer "skin"
        ]

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
            pass

        return rom

    def get_palette(self, palettes, default_range=[], frame_number=0):
        palette_indices = None
        this_palette = []
        range_end = 4
        for i in range(1,range_end):
            this_palette.append((0,0,0))

        for scheme in [
            "mario",
            "luigi",
            "fire",
            "global"
        ]:
            if f"{scheme}_brother" in palettes:
                this_palette = self.mario_globals[f"{scheme}_palette"]

        if len(this_palette) < 1:
            palette_indices = list(range(1,range_end))     #start with normal mail and modify it as needed

        if palette_indices:
            for i,_ in enumerate(palette_indices):
                this_palette[i] = self.master_palette[palette_indices[i]]

        return this_palette
