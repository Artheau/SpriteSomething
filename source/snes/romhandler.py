#Originally written by Artheau
#In April 2019 while observing the subtle scent of cleaning chemicals
#
#This file defines a class that contains all the functions necessary to do the expected operations to an SNES ROM
#e.g. read/write/etc.
#Note: it abstracts away little endian notation.  Just write into memory in big endian, and read out in big endian.

import enum
import json
import os
import struct

#enumeration for the rom types
class RomType(enum.Enum):
    #using the least significant bits of the internal header here for consistency
    LOROM   = 0b000
    HIROM   = 0b001
    EXLOROM = 0b010
    EXHIROM = 0b101

class RomHandlerParent():
    def __init__(self, filename):
        #internal constants
        self._HEADER_SIZE = 0x200
        self._MEGABIT = 0x20000

        self._patch = {}

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
            if self._rom_is_headered:
                self._header = bytearray(file.read(self._HEADER_SIZE))
            self._contents = bytearray(file.read())

        #Determine the type of ROM (e.g. LoRom or HiRom)
        #by comparing against checksum complement
        LOWER_ASCII = 0x20
        UPPER_ASCII = 0x7E
        ROM_TITLE_SIZE = 21
        if self._rom_size > 32*self._MEGABIT: #larger than 32 MBit
            EXLOROM_CHECKSUM_OFFSET = 0x407FDE
            EXHIROM_CHECKSUM_OFFSET = 0x40FFDE
            if self.read(EXLOROM_CHECKSUM_OFFSET, 2) + self.read(EXLOROM_CHECKSUM_OFFSET-2, 2) == 0xFFFF:
                self._type = RomType.EXLOROM
            elif self.read(EXHIROM_CHECKSUM_OFFSET, 2) + self.read(EXHIROM_CHECKSUM_OFFSET-2, 2) == 0xFFFF:
                self._type = RomType.EXHIROM
            else:   #the checksum is bad, so try to infer from the internal header being valid characters or not
                lorom_char_count = sum(x >= LOWER_ASCII and x <= UPPER_ASCII for x in self.read(0x407FC0, "1"*ROM_TITLE_SIZE))
                hirom_char_count = sum(x >= LOWER_ASCII and x <= UPPER_ASCII for x in self.read(0x40FFC0, "1"*ROM_TITLE_SIZE))
                if lorom_char_count >= hirom_char_count:
                    self._type = RomType.EXLOROM
                else:
                    self._type = RomType.EXHIROM
        else:
            LOROM_CHECKSUM_OFFSET = 0x7FDE
            HIROM_CHECKSUM_OFFSET = 0xFFDE
            if self.read(LOROM_CHECKSUM_OFFSET, 2) + self.read(LOROM_CHECKSUM_OFFSET-2, 2) == 0xFFFF:
                self._type = RomType.LOROM
            elif self.read(HIROM_CHECKSUM_OFFSET, 2) + self.read(HIROM_CHECKSUM_OFFSET-2, 2) == 0xFFFF:
                self._type = RomType.HIROM
            else:   #the checksum is bad, so try to infer from the internal header being valid characters or not
                lorom_char_count = sum(x >= LOWER_ASCII and x <= UPPER_ASCII for x in self.read(0x7FC0, "1"*ROM_TITLE_SIZE))
                hirom_char_count = sum(x >= LOWER_ASCII and x <= UPPER_ASCII for x in self.read(0xFFC0, "1"*ROM_TITLE_SIZE))
                if lorom_char_count >= hirom_char_count:
                    self._type = RomType.LOROM
                else:
                    self._type = RomType.HIROM

        #check to make sure the makeup byte confirms our determination of the ROM type
        makeup_byte = self._read_from_internal_header(0x15, 1)
        if self._type == RomType.LOROM and makeup_byte in [0x20,0x30]:
            pass    #lorom confirmed
        elif self._type == RomType.HIROM and makeup_byte in [0x21, 0x31]:
            pass    #hirom confirmed
        elif self._type in [RomType.LOROM, RomType.HIROM] and makeup_byte == 0x23:
            pass    #Maybe SA-1 will work with this library.  MAYBE.
        elif self._type == RomType.EXLOROM and makeup_byte in [0x32,0x30]:  #technically 0x32 is the correct value, but not all hackers respect this
            pass    #exlorom confirmed
        elif self._type == RomType.EXHIROM and makeup_byte == 0x35:
            pass    #exhirom confirmed
        else:
                        # FIXME: English
            #raise AssertionError(f"Cannot recognize the makeup byte of this ROM: {hex(makeup_byte)}.")
            print(f"Cannot recognize the makeup byte of this ROM: {hex(makeup_byte)}.")

        #information about onboard RAM/SRAM and enhancement chips lives here
        rom_type_byte = self._read_from_internal_header(0x16, 1)
        exBit = len(str(rom_type_byte)) > 0 and int(str(rom_type_byte)[:1]) or None
        coBit = len(str(rom_type_byte)) > 1 and int(str(rom_type_byte)[1:]) or None
        self._extra_hardware = exBit and exBit or None
        self._co_processor = coBit and coBit or None
        
        #can also retrieve SRAM size if desired
        #self._SRAM_size = 0x400 << self._read_from_internal_header(0x18,1)

    def save(self, filename, overwrite=False,fix_checksum=True,strip_header=False):
        #check to see if a file by this name already exists
        if not overwrite and os.path.isfile(filename):
                        # FIXME: English
            raise FileExistsError(f"{filename} already exists")

        # fix checksum
        if fix_checksum:
            self._fix_checksum()

        with open(filename, "wb") as file:
            if self._rom_is_headered and not strip_header:
                file.write(self._header)
            file.write(self._contents)

    def get_size_in_MB(self):
        return self._rom_size/(8*self._MEGABIT)

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

    def bulk_read(self,addr,num_bytes):
        #for large reads, the read() function is too slow.  This returns the raw byte data.
        return self._contents[addr:addr+num_bytes].copy()

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

    def read_from_snes_address(self,addr,encoding):
        return self.read(self.convert_to_pc_address(addr),encoding)

    def bulk_read_from_snes_address(self,addr,num_bytes):
        return self.bulk_read(self.convert_to_pc_address(addr),num_bytes)

    def write_to_snes_address(self,addr,values,encoding):
        return self.write(self.convert_to_pc_address(addr),values,encoding)

    def bulk_write_to_snes_address(self,addr,values,num_bytes):
        return self.bulk_write(self.convert_to_pc_address(addr),values,num_bytes)

    def convert_to_snes_address(self, addr):
        #takes as input a PC ROM address and converts it into the address space of the SNES
        if addr > self._rom_size or addr < 0:
                        # FIXME: English
            raise AssertionError(f"Function convert_to_snes_address() called on {hex(addr)}, but this is outside the ROM file.")

        if self._type == RomType.LOROM:
            bank = addr // 0x8000
            offset = addr % 0x8000
            snes_address = (bank+0x80)*0x10000 + (offset+0x8000)

        elif self._type == RomType.HIROM:
            snes_address = addr + 0x800000   #hirom is so convenient in this way

        elif self._type == RomType.EXLOROM:
            bank = addr // 0x8000
            offset = addr % 0x8000
            if bank < 0x80:
                snes_address = (bank+0x80)*0x10000 + (offset+0x8000)
            elif bank < 0xFE:
                snes_address = (bank-0x80)*0x10000 + (offset+0x8000)
            else:
                                # FIXME: English
                raise AssertionError(f"Function convert_to_snes_address() called on address {hex(addr)}, but this part of ROM is not mapped in ExLoRom.")

        elif self._type == RomType.EXHIROM:
            if addr < 0x400000:
                snes_address = addr + 0xC00000
            elif addr < 0x7E0000:
                snes_address = addr
            elif addr % 0x10000 > 0x8000:   #only the upper banks of this last little bit are mapped
                snes_address = addr - 0x400000    #for instance, 0x7E8000 PC is mapped to 0x3E8000 SNES
            else:
                                # FIXME: English
                raise AssertionError(f"Function convert_to_snes_address() called on {hex(addr)}, but this part of ROM is not mapped in ExHiRom.")

        else:
            raise NotImplementedError(f"Function convert_to_snes_address() called with not implemented type {self._type}")

        return snes_address

    def convert_to_pc_address(self, addr):
        #takes as input an address in the SNES address space and maps it to the correct address in the PC ROM.
        if addr > 0xFFFFFF or addr < 0:
                        # FIXME: English
            raise AssertionError(f"Function convert_to_pc_address() called on {hex(addr)}, but this is outside SNES address space.")

        bank = addr // 0x10000
        offset = addr % 0x10000

        if self._type == RomType.LOROM:
            #This particular part of address space has something to do with MAD-1 or lack thereof
            if bank >= 0x40 and bank < 0x70 and offset < 0x8000:
                offset += 0x8000
            #Now check for the usual stuff
            if offset < 0x8000 or bank in [0x7E,0x7F]:
                                # FIXME: English
                raise AssertionError(f"Function convert_to_pc_address() called on {hex(addr)}, but this does not map to ROM.")
            pc_address = (bank % 0x80)*0x8000 + (offset - 0x8000)

        elif self._type == RomType.HIROM:
            if bank in [0x7E, 0x7F] or (bank < 0xC0 and offset < 0x8000):
                raise AssertionError(f"Function convert_to_pc_address() called on {hex(addr)}, but this does not map to ROM.")
            pc_address = (bank // 0x40)*0x10000 + offset

        elif self._type == RomType.EXLOROM:
            #This particular part of address space has something to do with MAD-1 or lack thereof
            if bank >= 0x40 and bank < 0x70 and offset < 0x8000:
                offset += 0x8000
            #Now check for the usual stuff
            if bank >= 0x80 and offset >= 0x8000:  #fastrom block
                pc_address = (bank-0x80)*0x8000 + (offset-0x8000)
            elif bank not in [0x7E, 0x7F] and offset >= 0x8000:    #slowrom block
                pc_address = (bank+0x80)*0x8000 + (offset-0x8000)
            elif bank in [0xD1,0xD2,0xD3,0xD4,0xD5,0xD6]:   #Quad Rando block
                pc_address = (bank-0xA5)*0x8000 + (offset-0x8000)
            else:
                                # FIXME: English
                raise AssertionError(f"Function convert_to_pc_address() called on address {hex(addr)}, but this does not map to ROM. Bank: ${bank} 0x{hex(bank).upper()[2:]}")

        elif self._type == RomType.EXHIROM:
            if bank >= 0xC0:              #the fastrom block
                pc_address = (bank - 0xC0)*0x10000 + offset
            elif bank >= 0x40 and bank < 0x7E:    #the slowrom block
                pc_address = bank*0x10000 + offset
            elif bank in [0x3E, 0x3F] and offset > 0x8000:    #the little bit of extra room at the end of the slowrom block
                pc_address = (bank + 0x40)*0x10000 + offset
            elif bank >= 0x80 and bank < 0xC0 and offset >= 0x8000:   #the fastrom mirror
                pc_address = (bank - 0x80)*0x10000 + offset
            elif bank < 0x3E and offset >= 0x8000:  #the slowrom mirror
                pc_address = (bank + 0x40)*0x10000 + offset
            else:
                                # FIXME: English
                raise AssertionError(f"Function convert_to_pc_address() called on {hex(addr)}, but this does not map to ROM.")
        else:
            raise NotImplementedError(f"Function convert_to_pc_address() called with not implemented type {self._type}")

        if pc_address > self._rom_size:
            #the rom is not large enough to actually contain the indexed address, so we need to consider mirrored addresses
            if self._type in [RomType.LOROM, RomType.EXLOROM]:
                masked_addr = addr & 0x7FFFFF
            else:
                masked_addr = addr & 0x3FFFFF

            most_significant_bit = masked_addr.bit_length() - 1
            new_addr = addr - (1 << most_significant_bit)
            pc_address = self.convert_to_pc_address(new_addr)    #recurse to get the corrected address

        return pc_address

    def equivalent_addresses(self, addr1, addr2):
        #see if two addresses map to the same point in PC ROM
        return self.convert_to_pc_address(addr1) == self.convert_to_pc_address(addr2)

    def expand(self,size):
        #expands the ROM upwards in size to the specified number of MBits.
        #In this implementation, does not work to expand ROMs any higher than 32 MBits.
        if size < 4 or size > 32 or size % 4 != 0:
                        # FIXME: English
            raise NotImplementedError(f"Not Implemented to expand ROM to {size} MBits.  Must be a multiple of 4 between 4 and 32.")
        current_size = self._rom_size/self._MEGABIT
        if size <= current_size:
            #raise AssertionError(f"Received request to expand() to size {size} MBits, but the ROM is already {self._rom_size/self._MEGABIT} MBits")
            return None     #For now I am convinced that it is ok to just do nothing in this case instead of throwing an error

        size_code = 0x07 + (size-1).bit_length()   #this is a code for the internal header which specifies the approximate ROM size.
        self._write_to_internal_header(0x17, size_code, 1)

        pad_byte_amount = size*self._MEGABIT-self._rom_size
        self._contents.extend([0]*pad_byte_amount)  #actually extend the ROM by padding with zeros

        self._rom_size = size*self._MEGABIT

        return self._rom_size

    def type(self):
        #to see if the rom is lorom, hirom, etc.
        return self._type.name

    def get_name(self):
        raw_name = bytes(self._read_from_internal_header(0, "1"*21))
        try:
            return raw_name.decode("ascii")
        except:
            return raw_name

    def get_extrahardware(self):
        rom_types = [
            "ROM",
            "ROM+RAM",
            "ROM+RAM+Battery",
            "ROM+CoProcessor",
            "ROM+CoProcessor+RAM",
            "ROM+CoProcessor+RAM+Battery",
            "ROM+CoProcessor+Battery",
        ]
        if self._extra_hardware:
            rom_type = rom_types[self._extra_hardware]
            if "CoProcessor" in rom_type:
                co_processor = self.get_coprocessor()
                rom_type = rom_type.replace("CoProcessor",co_processor)
            return rom_type
        else:
            return None

    def get_coprocessor(self):
        coprocessors = [
            "DSP 1-4",
            "GSU SuperFX",
            "OBC1",
            "SA-1",
            "S-DD1",
            "S-RTC",
            "Other SGB/BSX",
            "Custom"
        ]
        if self._co_processor:
            return coprocessors[self._co_processor]
        else:
            return None

    def add_header(self):
        self._rom_is_headered = True
        self._header = bytearray([0]*self._HEADER_SIZE)

    def remove_header(self):
        self._rom_is_headered = False

    def get_patch(self):
        patch = self._patch
        patch_keys = list(patch.keys())
        patch_keys.sort()
        new_patch = {}
        for patch_key in patch_keys:
            patch_val = patch[patch_key].replace("0x","").rjust(4,'0')
            byte_one = patch_val[:2]
            byte_two = patch_val[2:]
            new_patch[patch_key] = int(byte_one,16)
            new_patch[patch_key + 1] = int(byte_two,16)
        return json.dumps(new_patch)

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

    def _apply_single_fix_to_snes_address(self, snes_address, classic_values, fixed_values, encoding):
        #checks to see if, indeed, a value is still in the classic (bugged) value, and if so, fixes it
        #returns True if the fix was affected and False otherwise

        #first make sure the input makes sense -- either all integers or matching length lists
        if (not isinstance(encoding,int)) and len(classic_values) != len(fixed_values):
                        # FIXME: English
            raise AssertionError(f"function _apply_single_fix_to_snes_address() called with different length lists:\n{classic_values}\n{fixed_values}")

        if self.read_from_snes_address(snes_address, encoding) == classic_values:
            self.write_to_snes_address(snes_address, fixed_values, encoding)
            return True
        return False

    def _read_from_internal_header(self, offset, size):
        return self.read_from_snes_address(offset + 0xFFC0, size)

    def _write_to_internal_header(self, offset, value, size):
        return self.write_to_snes_address(offset+0xFFC0, value, size)

    def _fix_checksum(self):
        #first write zero to the old checksum (for convenience, in case it was broken before)
        self._write_to_internal_header(0x1C, [0xFFFF,0x0000], "22")
        checksum = self._get_checksum()
        self._write_to_internal_header(0x1C, [0xFFFF - checksum,checksum], "22")

    def _get_checksum(self):
        #collected from a hodgepodge of data around the internet.  Hopefully all are correct.
        mbit_size = self._rom_size//self._MEGABIT

        best_power_of_2 = 1 << mbit_size.bit_length()-1
        if best_power_of_2 == mbit_size:   #best case is that the MBits is a power of 2
            checksum = sum(self._contents)
        elif mbit_size == 28:              #special case that doesn't really fit well into the remaining formulas
            checksum = sum(self._contents) + sum(self._contents[-4*self._MEGABIT:])
        else:                              #basic idea: repeat the part that's over a power of 2 until you get to the next multiple of 2
            lower_power_of_2 = 1 << (mbit_size-best_power_of_2).bit_length()-1
            if best_power_of_2 + lower_power_of_2 == mbit_size:
                multiplier = best_power_of_2 // lower_power_of_2
                checksum = sum(self._contents[:best_power_of_2*self._MEGABIT]) + \
                                    multiplier*sum(self._contents[best_power_of_2*self._MEGABIT:])
            else: #some strange MBit size maybe
                                # FIXME: English
                raise AssertionError(f"Unable to process checksum for ROM of size {mbit_size} MBits")

        return checksum % 0x10000

def main():
    print(f"Called main() on utility library {__file__}")

if __name__ == "__main__":
    main()
