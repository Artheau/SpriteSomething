import os.path
from typing import List, Tuple

from PIL import Image

from source.nes.colors import COLORS_2C02

Palette = List[Tuple[int, int, int, int]]


class RomHandlerParent:
    _HEADER_SIZE = 0xf
    _HEADER_SIGNATURE = bytes([0x4e, 0x45, 0x53, 0x1a])  # ASCII "NES" followed by MS-DOS end-of-file

    _header = bytearray()
    _contents = bytearray()

    def __init__(self, filename):
        with open(filename, "rb") as file:
            self._header = bytearray(file.read(self._HEADER_SIZE))
            self._contents = bytearray(file.read())

        if self._header[0:4] != self._HEADER_SIGNATURE:
            raise AssertionError("Rom has invalid header")

    def get_name(self):
        # TODO: NES ROMs do not contain metadata like game titles, etc...
        #       will have to find a different way to detect game, like hashing
        return "MARIO 3"

    def read(self, offset, length, from_header_start=True):
        """
        Read ROM bytes.
        """
        if length <= 0:
            AssertionError("Length must be greater than zero")

        if from_header_start:
            offset -= self._HEADER_SIZE

        if offset < 0 or offset + length > len(self._contents):
            AssertionError(f"Tried to read out of bounds data: {offset} : {offset + length}")

        return self._contents[offset:offset + length]

    def read_rgba_palette(self, offset: int, colors=None) -> Palette:
        """
        Read a 4 byte palette and map to RGBA values. The first palette color will always be fully transparent.
        The other palette colors will always be fully opaque.
        """
        if colors is None:
            colors = COLORS_2C02

        color_indices = self.read(offset, 4)
        return [colors[i] + (0 if i == 0 else 255,) for i in color_indices]

    def read_chr(self, offset: int):
        """
        Read an 8 by 8 CHR tile and return it as a list of 64 palette indices.
        """
        raw_data = self.read(offset, 16)

        lo_bits = raw_data[:8]
        hi_bits = raw_data[8:]

        chr_data = bytearray(64)

        for y in range(8):
            lb = lo_bits[y]
            hb = hi_bits[y]

            for x in range(8):
                n = 7 - x
                chr_data[8 * y + x] = (lb >> n & 1) | ((hb >> n & 1) << 1)

        return chr_data

    def read_chr_to_image(self, offset: int, palette: Palette) -> Image.Image:
        """
        Read an 8 by 8 CHR tile and return it as an 8 by 8 image, colored using the given palette.
        """
        chr_data = self.read_chr(offset)
        rbga_data = [palette[i] for i in chr_data]

        image = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        image.putdata(rbga_data)

        return image

    def read_tiles_to_image(self, offset: int, palette: Palette, length: int, pattern="x16") -> Image.Image:
        """
        Read a number of consecutive 8 by 8 CHR tiles, ordered by the given pattern,
        and return as a composed image, colored using the given palette.
        """
        # TODO: for now, assume the pattern is always FC/NES x16
        width = 8 * (length // 2 + 1)
        height = 8 if length <= 1 else 16

        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        for n in range(length):
            tile_image = self.read_chr_to_image(offset + n * 16, palette)
            x = 8 * (n // 2)
            y = 0 if n % 2 == 0 else 8
            image.paste(tile_image, (x, y))

        return image

    def write(self, offset, data, from_header_start=True):
        """
        Write ROM bytes.
        """
        if from_header_start:
            offset -= self._HEADER_SIZE

        end = offset + len(data)

        if offset < 0 or end > len(self._contents):
            AssertionError(f"Tried to write out of bounds data: {offset} : {end}")

        self._contents[offset:end] = bytearray(data)

    def save(self, filename, overwrite=False):
        """
        Save ROM data to a file located at the given filename.
        """
        if not overwrite and os.path.isfile(filename):
            raise FileExistsError(f"{filename} already exists")

        with open(filename, "wb") as file:
            file.write(self._header)
            file.write(self._contents)
