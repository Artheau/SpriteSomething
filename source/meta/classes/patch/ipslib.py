from textwrap import wrap

class IPSFile():
    def __init__(self):
        #                     | MB   | KB   | Bytes
        self._MAXBYTES = 2047 * 1024 * 1024 * 1
        self._HEADER = "PATCH"
        self._FOOTER = "EOF"
        self.records = []

    def add_record(self, offset=0, data=[], length=0):
        if length == 0:
            length = len(data)
        if not isinstance(offset, int):
            if "0x" in offset:
                offset = int(offset, 16)
        if offset + length > self._MAXBYTES:
            raise AssertionError(f"{offset}+{length} is out of bounds!")
        self.records.append(Record(offset, data, length))

    def get_record(self, record_id):
        if record_id < len(self.records):
            return self.records[record_id]
        else:
            raise AssertionError(f"{record_id} doesn't exist!")

    def get_records(self):
        return self.records

    def get_array(self):
        arr = {}
        for record in self.get_records():
            arr[int(record.get_pretty_offset(),16)] = record.data
        return arr

    def get_bytearray(self):
        arr = []
        for record in self.get_records():
            offset = [
                int(x,16) for x in wrap(
                    record.get_pretty_offset().replace("0x",""),
                    2
                )
            ]
            length = [
                int(x,16) for x in wrap(
                    record.get_pretty_length().replace("0x",""),
                    2
                )
            ]
            data = record.data
            arr = [*arr,*offset]
            arr = [*arr,*length]
            arr = [*arr,*data]
        return arr

    def get_dict(self):
        dct = {}
        for record in self.get_records():
            dct[record.get_pretty_offset()] = {
                "length": int(record.get_pretty_length(),16),
                "data": record.data
            }
        return dct

    def get_binary(self):
        arr = []
        for record in self.get_records():
            arr = [*arr,*record.data]
        return bytes(arr)

    def get_patch(self):
        return bytes(
            [
                *[ord(x) for x in self._HEADER],
                *self.get_bytearray(),
                *[ord(x) for x in self._FOOTER]
            ]
        )

    def apply_patch(self, rom_bytes):
        rom = list(rom_bytes)
        rom_length = len(rom)
        for record in self.get_records():
            offset = int("".join([x for x in record.offset]))
            length = int("".join([x for x in record.length]))
            data = record.data
            if offset+length <= rom_length:
                for i in range(0,length):
                    rom[offset+i] = data[i]
        rom = bytes(rom)
        return rom

    def print_summary(self):
        for record in self.get_records():
            print(record.get_summary())

    def save(self, filename=""):
        with open(filename, "wb") as file:
            file.write(self.get_patch())

    def save_bin(self, filename=""):
        with open(filename, "wb") as file:
            file.write(self.get_binary())

class Record():
    def __init__(self, offset, data, length):
        self.offset = [
            str(x) for x in wrap(
                str(offset).zfill(6),
                2
            )
        ]
        self.length = [
            str(x) for x in wrap(
                str(length).zfill(4),
                2
            )
        ]
        self.data = data

    def get_pretty_offset(self):
        offset = self.offset
        # print("Self:", offset)
        offset = "".join([str(x) for x in offset])
        # print("Join:", offset)
        offset = int(offset)
        # print("INT:", offset)
        offset = hex(offset)
        # print("HEX:", offset)
        if offset.startswith("0x"):
            offset = offset[2:]
        offset = offset.upper()
        offset = str(offset).zfill(6)
        # print("ZFILL(6):", offset)
        offset = "0x" + offset
        # print("Hexify:", offset)
        return offset
    def get_pretty_length(self):
        length = self.length
        # print("Self:", length)
        length = "".join([str(x) for x in length])
        # print("Join:", length)
        length = int(length)
        # print("INT:", length)
        length = hex(length)
        # print("HEX:", length)
        if length.startswith("0x"):
            length = length[2:]
        length = length.upper()
        length = str(length).zfill(4)
        # print("ZFILL(4):", length)
        length = "0x" + length
        # print("Hexify:", length)
        return length
    def get_summary(self):
        return f"{self.get_pretty_offset()}[{self.get_pretty_length()}]"

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        offset = self.get_pretty_offset()
        length = self.get_pretty_length()
        return f"{offset}[{length}]: {self.data}"

if __name__ == "__main__":
    exit(1)

    patch = IPSFile()
    for i in range(8):
        patch.add_record(i,[i,pow(2,i)])
    for i in range(8,18):
        patch.add_record(i,[2*i])
    patch.add_record("0x030000",[2])
    patch.add_record("0x0B0000",[4])
    patch.add_record("0x000002",[6])
    patch.add_record("0x000020",[6])
    patch.add_record("0x000200",[6])
    patch.add_record("0x002000",[6])
    patch.add_record("0x020000",[6])
    patch.add_record("0x200000",[6])
    patch.add_record("0x00000A",[6])
    patch.add_record("0x0000A0",[6])
    patch.add_record("0x000A00",[6])
    patch.add_record("0x00A000",[6])
    patch.add_record("0x0A0000",[6])
    patch.add_record("0xA00000",[6])
    # print(patch.get_patch())
    # print(patch.get_bytearray())
    # print(patch.get_array())
    # print(patch.get_dict())
    # print(patch.get_binary())
    # print(patch.get_records())
    patch.print_summary()

    patch.save("./patch.ips")
