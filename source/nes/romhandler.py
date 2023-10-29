import os.path

from PIL import Image


class RomHandlerParent:
    _HEADER_SIZE = 0xf
    _HEADER_SIGNATURE = bytes([0x4e, 0x45, 0x53, 0x1a])  # ASCII "NES" followed by MS-DOS end-of-file
    _CHR_OFFSET = 0x40010

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

    def read_chr(self, offset):
        """
        Read an 8 by 8 CHR tile and return it as a list of 64 palette indexes.
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

    def read_chr_to_image(self, offset, palette) -> Image.Image:
        """
        Read an 8 by 8 CHR tile and return it as an 8 by 8 image, colored using the given palette.
        """
        chr_data = self.read_chr(offset)
        image_data = [palette[idx] for idx in chr_data]

        image = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        image.putdata(image_data)

        return image

    def write(self, offset, data, from_header_start=True):
        if from_header_start:
            offset -= self._HEADER_SIZE

        end = offset + len(data)

        if offset < 0 or end > len(self._contents):
            AssertionError(f"Tried to write out of bounds data: {offset} : {end}")

        self._contents[offset:end] = bytearray(data)

    def save(self, filename, overwrite=False):
        if not overwrite and os.path.isfile(filename):
            raise FileExistsError(f"{filename} already exists")

        with open(filename, "wb") as file:
            file.write(self._header)
            file.write(self._contents)
