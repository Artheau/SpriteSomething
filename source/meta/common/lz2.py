# Originally written by Murder Who
# In October 2024 while beating YY-CHR into submission to verify the fruits of the labor

import os
from pathlib import Path

from PIL import Image
from string import ascii_uppercase, digits
import itertools
from source.meta.common import common
from ..classes import layoutlib


class LZ2CommandException(Exception):
    def __init__(self, message, payload=None):
        self.message = message
        if isinstance(message, list):
            self.message = "\n".join(message)
        if isinstance(message, dict):
            self.message = [
                "Index:     " + str(message["index"]),
                "A[Index]:  " + hex(message["a"][message["index"]]),
                "High Bits: " + hex(message["high"]),
                "Low Bits:  " + hex(message["low"]),
                "---",
                "Output:    " + str(["0x" + format(byte, '02x').upper() for byte in message["b"]])
            ]
            self.message = "\n".join(self.message)
        self.payload = payload

    def __str__(self):
        return "\n".join(["An illegal command has occurred", str(self.message)])


def decompress(a):
    if not isinstance(a, bytearray):
        raise TypeError("Input data is not a bytearray!")
    index = 0
    b = bytearray()

    while index < len(a):
        # first three bits are the command, last 5 bits are the length
        if a[index] == 0xFF:
            # then we are finished
            break

        high = a[index] >> 5
        high &= 0x7
        low = a[index] & 0x1F

        index += 1

        # long command. 000C CCLL LLLL LLLL
        if high == 0x7:
            high = a[index-1] >> 2
            high &= 0x7
            low = int.from_bytes(a[index-1:index+1], "big") & 0x03FF
            index += 1

        # direct write, copy L +1 bytes
        if high == 0x0:
            for _ in range(low+1):
                b.append(a[index])
                index += 1
        # byte fill, copy next byte L+1 times
        elif high == 0x1:
            for _ in range(low+1):
                b.append(a[index])
            index += 1
        # word fill, copy next 2 bytes in sequence until L+1 bytes are copied
        elif high == 0x2:
            for i in range(low+1):
                b.append(a[index + i % 2])
            index += 2
        # increasing fill, copy next byte, but add 1 each time, for L+1 times
        elif high == 0x3:
            for i in range(low+1):
                b.append(i+a[index])
            index += 1
        # repeat, use next two bytes as an address in the output buffer to copy L+1 sequence of bytes from
        elif high == 0x4:
            b_index = int.from_bytes(a[index:index+2], "little")
            fo = a[index:index+2]
            index += 2
            for i in range(low+1):
                b.append(b[b_index+i])
        else:
            raise LZ2CommandException(
                {
                    "index": index,
                    "a": a,
                    "b": b,
                    "low": low,
                    "high": high
                }
            )
    return b


def convert_3bpp_to_png(src_filename):
    #FIXME: In the end, we just want the Power Star for the TFP implementation
    with open(src_filename, "rb") as file:
        layout = layoutlib.Layout(
            os.path.join(
                ".",
                "resources",
                "app",
                "snes",
                "zelda3",
                "triforcepiece",
                "manifests",
                "layout.json"
            )
        )
        images = {}
        data_3bpp = bytearray(file.read())

        pixel_data = data_3bpp
        for i, row in enumerate(itertools.chain(ascii_uppercase, ["AA", "AB"])):
            for column in range(8):
                this_image = Image.new("P", (16, 16), 0)
                image_name = f"{row}{column}"
                raw_tile = None
                planes = 3
                for offset, position in [
                    (0x0000*planes, (0, 0)),
                    (0x0008*planes, (8, 0)),
                    (0x0080*planes, (0, 8)),
                    (0x0088*planes, (8, 8))
                ]:
                    read_pointer = 0x100*planes*i+(16*planes)*column+offset
                    raw_tile = pixel_data[read_pointer:read_pointer+(8*planes)]
                    if raw_tile:
                        pastable_tile = common.image_from_bitplanes_base(
                            raw_tile
                        )
                        this_image.paste(pastable_tile, position)
                if raw_tile:
                    images[image_name] = this_image
        layout.images = images
        palettes = {
            "1": [  # Red, Grey
                (248, 248, 248),
                (200, 88, 48),
                (176, 40, 40),
                (224, 112, 112),
                (40, 40, 40),
                (184, 184, 200),
                (120, 120, 136)
            ],
            "2": [  # Blue
                (248, 248, 248),
                (248, 128, 176),
                (80, 104, 168),
                (144, 168, 232),
                (40, 40, 40),
                (248, 176, 80),
                (184, 96, 40)
            ],
            "4": [  # Green
                (248, 248, 248),
                (200, 48, 24),
                (72, 144, 48),
                (152, 208, 112),
                (40, 40, 40),
                (248, 208, 56),
                (184, 136, 32)
            ],
            "7": [
                (248, 248, 248),
                (240, 216, 64),
                (184, 104, 32),
                (240, 160, 104),
                (40, 40, 40),
                (248, 120, 0),
                (192, 24, 32),
                (232, 96, 176)
            ]
        }
        palette_preview = Image.new("RGBA",(1,1),(0,0,0,0))
        dest_filename = ""
        i = 0
        for paletteID, palette in palettes.items():
            image = layout.export_these_images_to_PNG(layout.images, palette)
            scale = 4 if True else 1
            if scale != 1:
                image = image.resize(
                    (
                        image.size[0]*scale,
                        image.size[1]*scale
                    ),
                    Image.NEAREST
                )
            if palette_preview.size == (1,1):
                palette_preview = palette_preview.resize(
                    (
                        image.size[0],
                        image.size[1]*len(palettes.keys())
                    )
                )
            palette_preview.paste(image,(0,image.size[1]*i))
            i += 1
            dest_filename = os.path.join(
                os.path.dirname(src_filename),
                os.path.splitext(os.path.basename(src_filename))[0]
            )
            dest_filename = f"{dest_filename}_p-{paletteID}.png"
            image.save(dest_filename)
        palette_preview.save(dest_filename.replace(f"p-{paletteID}", "p-preview"))


def decompress_from_file(src_filename):
    with open(src_filename, "rb") as file:
        return decompress(bytearray(file.read()))


def decompress_to_file(src_filename, dest_filename=None):
    if not dest_filename:
        dest_dir = os.path.dirname(
            src_filename
        ).replace(os.path.join("","app",""),os.path.join("","user",""))
        dest_filename = f"u_{os.path.splitext(os.path.basename(src_filename))[0]}.bin"
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        dest_filename = os.path.join(dest_dir, dest_filename)
    b = decompress_from_file(src_filename)
    with open(dest_filename, "wb") as file:
        file.write(b)


if __name__ == "__main__":
    # Compressed 3BPP -> Decompressed 3BPP
    decompress_to_file(
        os.path.join(
            "resources",
            "app",
            "snes",
            "zelda3",
            "triforcepiece",
            "sheets",
            "triforce.bin"
        )
    )
    # Decompressed 3BPP -> PNG
    convert_3bpp_to_png(
        os.path.join(
            "resources",
            "user",
            "snes",
            "zelda3",
            "triforcepiece",
            "sheets",
            "u_triforce.bin"
        )
    )
    # Now, for icing on the cake:
    #  Convert PNG  -> 4BPP
    #  Convert 4BPP -> 3BPP
    #  Compress using LZ2
    #  Save to disk or inject into game file
