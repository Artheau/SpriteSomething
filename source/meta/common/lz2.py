# Originally written by Murder Who
# In October 2024 while beating YY-CHR into submission to verify the fruits of the labor

import os
from pathlib import Path


class LZ2CommandException(Exception):
    def __init__(self, message, payload=None):
        self.message = message
        if isinstance(message, list):
            self.message = "\n".join(message)
        self.payload = payload

    def __str__(self):
        return str(self.message)


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
                [
                    "An illegal command has occurred",
                    index,
                    a[index].hex(),
                    high.hex(),
                    low.hex(),
                    "---",
                    b.hex()
                ]
            )
    return b


def decompress_from_file(src_filename):
    with open(src_filename, "rb") as file:
        return decompress(bytearray(file.read()))


def decompress_to_file(src_filename, dest_filename=None):
    if not dest_filename:
        dest_dir = os.path.dirname(src_filename).replace(
            os.path.join("", "app", ""), os.path.join("", "user", ""))
        dest_filename = f"u_{os.path.splitext(os.path.basename(src_filename))[0]}.bin"
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        dest_filename = os.path.join(dest_dir, dest_filename)
        dest_filename = dest_filename
    b = decompress_from_file(src_filename)
    with open(dest_filename, "wb") as file:
        file.write(b)


if __name__ == "__main__":
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
