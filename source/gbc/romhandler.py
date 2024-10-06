#Originally written by Minnie Trethewey
#In January 2024 while freezing temperatures plague the Pacific Northwest
#
#This file defines a class that contains all the functions necessary to do the expected operations to an SNES ROM
#e.g. read/write/etc.
#Note: it abstracts away little endian notation.  Just write into memory in big endian, and read out in big endian.

import enum
import json
import os
import struct

class RomHandlerParent():
    def __init__(self, filename):
        #internal constants
        self._HEADER_SIZE = 0x150
        self._MEGABIT = 0x20000

        #figure out if it has a header by inferring from the overall file size
        file_size = os.path.getsize(filename)
        if file_size % 0x8000 == 0:
            self._rom_is_headered = False
            self._rom_size = file_size
        elif file_size % 0x8000 == self._HEADER_SIZE:
            self._rom_is_headered = True
            self._rom_size = file_size - self._HEADER_SIZE
        else:
                        # FIXME: English
            raise AssertionError(f"{filename} does not contain an even number of half banks...is this a valid ROM?")

        #open the file and store the contents
        with open(filename, "rb") as file:
            self._contents = bytearray(file.read())

    def save(self, filename, overwrite=False,fix_checksum=True,strip_header=False):
        #check to see if a file by this name already exists
        if not overwrite and os.path.isfile(filename):
                        # FIXME: English
            raise FileExistsError(f"{filename} already exists")

        # fix checksum
        # if fix_checksum:
        #     self._fix_checksum()

        with open(filename, "wb") as file:
            # if self._rom_is_headered and not strip_header:
            #     file.write(self._header)
            file.write(self._contents)

    def get_size_in_MB(self):
        return self._rom_size/(8*self._MEGABIT)

    def read_raw(self):
        return self._contents

    def write_raw(self, rom_bytes):
        self._contents = rom_bytes

    def read(self,addr,encoding):
        #expects a ROM address and an encoding
        #
        #if encoding is an integer:
        #returns a single value which is the unpacked integer in normal (big-endian) format from addr to addr+encoding
        #example: .read(0x7FDC, 2) will return the big-endian conversion of bytes 0x7FDC and 0x7FDD
        #
        #if encoding is a string:
        #starting from addr, starts unpacking values according to the encoding string,
        # converting them from little endian as it goes
        #example: .read(0x7FDC, "22") will read two words that start at 0x7FDC and return them in normal (big-endian) format as a list

        if isinstance(encoding,int):
            return self._read_single(addr,encoding)
        if isinstance(encoding,str):
            returnvalue = []
            for code in encoding:
                size = int(code)
                returnvalue.append(self._read_single(addr, size))
                addr += size
            return returnvalue
                # FIXME: English
        raise AssertionError(f"received call to read() but the encoding was not recognized: {encoding}")

    def write(self,addr,values,encoding):
        #if encoding is an integer:
        #expects a value and an address to write to.  It will convert it to little-endian format automatically.
        #example: .write(0x7FDC, 0x1f2f, 2) will write 0x2f to 0x7FDC and 0x1f to 0x7FDD
        #
        #if encoding is a string:
        #does essentially the same thing, but expects a list of values instead of a single value
        # converting them to little endian and writing them in order.
        #example: .write(0x7FDC, [0x111f,0x222f], "22") will write $1f $11 $2f $22 to 0x7FDC-0x7FDF

        if isinstance(encoding,int):
                        # FIXME: English
            if isinstance(values,int):
                self._write_single(values,addr,encoding)
            else:
                raise AssertionError(f"received call to write() a single value, but {values} was not a single value")
        elif isinstance(encoding,str):
            if isinstance(values,int):
                raise AssertionError("received call to do multiple writes, but only one value was given.  Should encoding be an integer instead of a string?")
            if len(values) != len(encoding):
                raise AssertionError(f"received call to write() but length of values and encoding did not match: i.e. {len(values)} vs. {len(encoding)}")
            for value,code in zip(values,encoding):
                size = int(code)
                self._write_single(value, addr, size)
                addr += size
        else:
            raise AssertionError(f"received call to write() but the encoding was not recognized: {encoding}")

    def bulk_write(self,addr,values,num_bytes):
        if len(values) != num_bytes:
                        # FIXME: English
            raise AssertionError("call to bulk_write() with data not of length specified")
        self._contents[addr:addr+num_bytes] = bytearray(values)

    def read_from_gbc_address(self,addr,encoding):
        return self.read(addr,encoding)

    def get_name(self):
        raw_name = bytes(self._read_from_internal_header(0x34, "1"*11))
        try:
            return raw_name.decode("ascii")
        except:
            return raw_name

    def _read_single(self, addr, size):
        if addr+size > self._rom_size:
                        # FIXME: English
            raise AssertionError(f"function _read_single() called for address beyond ROM file boundary: : {hex(addr)}, size {size}")
        extracted_bytes = self._contents[addr:addr+size]

        if size == 1:
            unpack_code = 'B'
        elif size == 2:
            unpack_code = 'H'
        elif size == 3:
            unpack_code = 'L'
            extracted_bytes.append(0x00)    #no native 3-byte unpacking format in Python; this is a workaround to pad the 4th byte
        elif size == 4:
            unpack_code = 'L'
        else:
                        # FIXME: English
            raise NotImplementedError(f"_read_single() called to read size {size}, but this is not implemented.")

        return struct.unpack('<'+unpack_code,extracted_bytes)[0]           #the '<' forces it to read as little-endian

    def _write_single(self, value, addr, size):
        if addr+size > self._rom_size:
                        # FIXME: English
            raise AssertionError(f"function _write_single() called for address beyond ROM file boundary: {hex(addr)}, size {size}")
        if size == 1:
            pack_code = 'B'
        elif size == 2:
            pack_code = 'H'
        elif size == 3:
            pack_code = 'L'
        elif size == 4:
            pack_code = 'L'
        else:
            raise NotImplementedError(f"_write_single() called to write size {size}, but this is not implemented.")

        self._contents[addr:addr+size] = struct.pack('<'+pack_code,value)[0:size]  #the '<' forces it to write as little-endian
        if isinstance(value,list):
            for i in range(addr + size - addr):
                val = struct.unpack('<'+pack_code,struct.pack('>'+pack_code,value[i]))[0]
                self._patch[addr] = hex(val)
        else:
            val = struct.unpack('<'+pack_code,struct.pack('>'+pack_code,value))[0]
            self._patch[addr] = hex(val)

    def _read_from_internal_header(self, offset, size):
        return self.read_from_gbc_address(offset + 0x100, size)

def main():
    print(f"Called main() on utility library {__file__}")

if __name__ == "__main__":
    main()
