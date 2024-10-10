# Originally written by Murder Who
# In October 2024 while beating YY-CHR into submission to verify the fruits of the labor

import os
from pathlib import Path

from PIL import Image
from string import ascii_uppercase, digits
import itertools
import numpy as np
from source.meta.common import common
from ..classes import layoutlib
from ..classes import spritelib


class LZ2CommandException(Exception):
    def __init__(self, message, payload=None):
        self.message = message
        if isinstance(message, list):
            self.message = "\n".join(message)
        if isinstance(message, dict):
            opcodes = [
                "Direct Write",
                "Byte Fill",
                "Word Fill",
                "Incresting Fill",
                "Repeat",
                "NOOP",
                "NOOP",
                "Long Code"
            ]
            opcode = opcodes[message["high"]] if message["high"] < len(opcodes) else "???"
            self.message = [
                "Index:     " + f"${str(message['index'])}; 0x" + format(message["index"], '04x').upper(),
                "A[Index]:  " + "0x" + format(message["a"][message["index"]], '04x').upper(),
                "OpCode:    " + str(opcode),
                "High Bits: " + "0x" + format(message["high"], '04x').upper(),
                "Low Bits:  " + "0x" + format(message["low"], '04x').upper(),
                "---",
                "Output:    " + str(["0x" + format(byte, '02x').upper() for byte in message["b"]])
            ]
            self.message = "\n".join(self.message)
        self.payload = payload

    def __str__(self):
        return "\n".join(["An illegal command has occurred", str(self.message)])


def compress(a):
    if not isinstance(a, bytearray):
        raise TypeError("Input data is not a bytearray!")
    index = 0
    b = bytearray()
    dic = {}

    BYTE_LIMIT = 0xFFFF
    if len(a) > BYTE_LIMIT:
        raise IndexError(f"This compression algorithm only supports lengths up to {BYTE_LIMIT} (two bytes). It may fail after that length.")

    prev_command = 9
    prev_direct_address = 0
    prev_length = 0

    while index < len(a):
        # Our commands are: direct write(000), repeat next byte (001), repeat next two bytes (010), increasing repeat next byte (011), and read from output buffer (100)
        # These are CCCL LLLL, with the length = L+1 for all of them
        # we also have long command: 111C CCLL LLLL LLLL, where C is the true command
        length = 0
        command = 0

        # this could be done way faster, but considering the amount of data we're compressing, IDGAF
        # I'm going to take the very simple route of looking for the maximum bytes that can be encoded with each method, and take the one that encodes the most following bytes.

        for i in range(1,0x0400):
            if index+i < len(a) and a[index+i] == a[index] + i:
                if i > max(1,length):
                    length = i
                    command = 3
            else:
                break

        for i in range(1,0x0400):
            if index+i < len(a) and a[index + i%2] == a[index + i]:

                if i > max(2,length):
                    length = i
                    command = 2
            else:
                break

        for i in range(1,0x0400):
            if index+i < len(a) and a[index] == a[index+i]:
                if i > 1:
                    length = i
                    command = 1
            else:
                break

        address = 0

        # this will be a very slow part of the compression. If we need to make compression faster, start here
        # important that i never equals index. Otherwise this'll just try to pass out the entire buffer as though you already know it

        for i in range(index-1):
            if a[i] == a[index]:
                # note that this can go beyond the current buffer.
                # For example, if we have a pattern like FF 77 11 FF 77 11 FF 11 C2, then once you get to the fourth byte, you'll want to repeat from index 0 for 5 bytes
                for j in range(len(a) - index):
                    if a[i+j] == a[index+j]:
                        if j > max(2,length):
                            address = i
                            length = j
                            command = 4
                    else:
                        break

        if (prev_command == 0 and index == len(a) -1) or (prev_command == 0 and command != 0):
            if prev_command == 0 and command != 0:
                prev_length -= 1
            if prev_length >= 0x001F:
                b.append((0x00E0 + (prev_length >>8)))
                b.append(prev_length & 0x00FF)
            else:
                b.append(prev_length)
            for i in range(prev_length+1):
                b.append(a[prev_direct_address + i])
            if index == len(a)-1:
                break

        elif prev_command == 0 and command == 0:
            prev_length += 1
            index += 1
            continue
        elif command == 0:
            prev_command = 0
            prev_length = 1
            prev_direct_address = index
            index += 1
            continue

        prev_command = command

        length = min(length, 0x0400)

        if length >= 0x001F:
            outputbyte = 0x00E0 + (command << 2) + (length >> 8)
            outputbyteb = length & 0x00FF
            b.append(outputbyte)
            b.append(outputbyteb)
        else:
            output_byte = (command<<5) + length
            b.append(output_byte)

        if command == 1 or command == 2 or command == 3:
            b.append(a[index])
        if command == 2:
            # two words!
            b.append(a[index+1])
        if command == 4:
            # little endian for Z3's decompression, so we need to reverse the order of these bytes
            if address > 0x00FF:
                # append the low bits first
                b.append(address & 0x00FF)
                # And then the high bits
                b.append(address >> 8)
            else:
                b.append(address)
                b.append(0)

        index += length + 1

    b.append(0x00FF)

    return b


def decompress(a, offset=0x00):
    if not isinstance(a, bytearray):
        raise TypeError("Input data is not a bytearray!")
    index = offset
    b = bytearray()

    while index < len(a):
        # first three bits are the command, last 5 bits are the length
        if a[index] == 0xFF:
            # then we are finished
            break

        high = a[index] >> 5
        high &= 0x07
        low = a[index] & 0x1F

        index += 1

        # long command. 000C CCLL LLLL LLLL
        if high == 0x07:
            high = a[index-1] >> 2
            high &= 0x07
            low = int.from_bytes(a[index-1:index+1], "big") & 0x03FF
            index += 1

        # direct write, copy L +1 bytes
        if high == 0x00:
            for _ in range(low+1):
                b.append(a[index])
                index += 1
        # byte fill, copy next byte L+1 times
        elif high == 0x01:
            for _ in range(low+1):
                b.append(a[index])
            index += 1
        # word fill, copy next 2 bytes in sequence until L+1 bytes are copied
        elif high == 0x02:
            for i in range(low+1):
                b.append(a[index + i % 2])
            index += 2
        # increasing fill, copy next byte, but add 1 each time, for L+1 times
        elif high == 0x03:
            for i in range(low+1):
                b.append(i+a[index])
            index += 1
        # repeat, use next two bytes as an address in the output buffer to copy L+1 sequence of bytes from
        elif high == 0x04:
            b_index = int.from_bytes(a[index:index+2], "little")
            fo = a[index:index+2]
            index += 2
            for i in range(low+1):
                if b_index+i < len(b):
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


def convert_3bpp_to_png(src_filename, dest_filename=None, verbose=False):
    if verbose:
        print(f" 3BPPtoPNG:     {src_filename.ljust(70)}", end="")
    # FIXME: In the end, we just want the Power Star for the TFP implementation
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
            ),
            "",
            False
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
                        pastable_tile = common.image_from_bitplanes_base(raw_tile)
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
            scale = 4 if False else 1
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
                os.path.dirname(src_filename).replace(
                    os.path.join("","app",""),
                    os.path.join("","user","")
                ),
                os.path.splitext(os.path.basename(src_filename))[0]
            )
            dest_filename = f"{dest_filename}_p-{paletteID}.png"
            image.save(dest_filename)
        dest_filename = dest_filename.replace(f"p-{paletteID}", "p-preview")
        if verbose:
            print(f" -> {dest_filename}")
        palette_preview.save(dest_filename)
        return dest_filename
    return False


def decompress_from_file(src_filename, dest_filename=None, verbose=False, offset=0x00):
    with open(src_filename, "rb") as file:
        return decompress(bytearray(file.read()), offset)


def decompress_to_file(src_filename, dest_filename=None, verbose=False, offset=0x00):
    if not dest_filename:
        dest_dir = os.path.dirname(
            src_filename
        ).replace(
            os.path.join("","app",""),
            os.path.join("","user","")
        )
        dest_filename = f"u_{os.path.splitext(os.path.basename(src_filename))[0]}.bin"
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        dest_filename = os.path.join(dest_dir, dest_filename)
    if verbose:
        print(f" Decompressing: {src_filename.ljust(70)} -> ", end="")
    b = decompress_from_file(src_filename, dest_filename, verbose, offset)
    if verbose:
        print(dest_filename)
    with open(dest_filename, "wb") as file:
        file.write(b)
        return dest_filename
    return False


def compress_from_file(src_filename):
    with open(src_filename, "rb") as file:
        return compress(bytearray(file.read()))


def compress_to_file(src_filename, dest_filename=None, verbose=False):
    if not dest_filename:
        dest_dir = os.path.dirname(
            src_filename
        ).replace(
            os.path.join("","app",""),
            os.path.join("","user","")
        )
        dest_filename = f"{os.path.splitext(os.path.basename(src_filename))[0]}.bin".replace("u_","c_")
        if dest_filename[:2] != "c_":
            dest_filename = f"c_{dest_filename}"
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        dest_filename = os.path.join(dest_dir, dest_filename)
    b = compress_from_file(src_filename)
    if verbose:
        print(f" Compressing:   {src_filename.ljust(70)} -> {dest_filename}")
    with open(dest_filename, "wb") as file:
        file.write(b)
        return dest_filename
    return False


def convert_png_to_3bpp(src_filename, dest_filename=None, verbose=False):
    if dest_filename is None:
        dest_filename = os.path.join(
            src_filename.replace(
                os.path.join("","app",""),
                os.path.join("","user","")
            ).replace(".png",".3bpp")
        )
    if verbose:
        print(f" PNGto3BPP:     {src_filename.ljust(70)} -> {dest_filename}")

    # FIXME: In the end, we just want the Power Star for the TFP implementation
    with Image.open(src_filename) as file:
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
            ),
            "",
            False
        )
        all_images, _ = layout.extract_these_images_from_master(file)
        data_4bpp = []
        planes = 4
        for row_num, row_id in enumerate(itertools.chain(ascii_uppercase, ["AA", "AB"])):
            top_halves = []
            low_halves = []
            for col_num in range(8):
                image_name = f"{row_id}{col_num}"
                if image_name in all_images:
                    image = all_images[image_name]
                    image = image.convert('P')
                    image_4bpp = common.convert_image_to_4bpp(image, (0,0), (0,0,16,16), None)
                    for top_half in image_4bpp[:0x10*planes]:
                        top_halves.append(top_half)
                    for low_half in image_4bpp[0x10*planes:]:
                        low_halves.append(low_half)
                else:
                    break
            for half_tile in top_halves:
                data_4bpp.append(half_tile)
            for half_tile in low_halves:
                data_4bpp.append(half_tile)

        with open(
            dest_filename.replace(".3bpp",".4bpp"),
            "wb"
        ) as file_4bpp:
            file_4bpp.write(bytearray(data_4bpp))

        pixel_data = bytearray(data_4bpp)
        data_3bpp = bytearray()
        for row_num, row_id in enumerate(itertools.chain(ascii_uppercase, ["AA", "AB"])):
            top_halves = []
            low_halves = []
            for col_num in range(8):
                image_name = f"{row_id}{col_num}"
                raw_tile = None
                planes = 4
                to_planes = 3
                for tile_num, (offset, position) in enumerate([
                    (0x0000*planes, (0, 0)),
                    (0x0008*planes, (8, 0)),
                    (0x0080*planes, (0, 8)),
                    (0x0088*planes, (8, 8))
                ]):
                    read_pointer = 0x100*planes*row_num+(16*planes)*col_num+offset
                    raw_tile = pixel_data[read_pointer:read_pointer+(8*planes)]
                    if len(raw_tile) == 0:
                        break
                    if False:
                        print(f"{image_name}[{tile_num}]", end="")
                    tile_3bpp = common.convert_tile_from_4bpp_to_3bpp(raw_tile)
                    if tile_num in [0,1]:
                        top_halves.append(tile_3bpp)
                    if tile_num in [2,3]:
                        low_halves.append(tile_3bpp)
            if len(top_halves):
                for tile in top_halves:
                    data_3bpp += tile
            if len(low_halves):
                for tile in low_halves:
                    data_3bpp += tile

        with open(
            dest_filename,
            "wb"
        ) as file_3bpp:
            file_3bpp.write(data_3bpp)
            return dest_filename
        return False


if __name__ == "__main__":
    if False:
        # PNG to u3BPP
        u3bpp_from_png = convert_png_to_3bpp(
            os.path.join(
                ".",
                "resources",
                "app",
                "snes",
                "zelda3",
                "triforcepiece",
                "sheets",
                "triforcepiece.png"
            ),
            None,
            True
        )
        # u3BPP -> c3BPP
        compress_to_file(u3bpp_from_png, None, True)
