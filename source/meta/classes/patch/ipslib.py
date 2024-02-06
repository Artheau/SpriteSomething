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
        arr = [ord(x) for x in self._HEADER]
        for record in self.get_records():
            arr = [*arr,*record.offset]
            arr = [*arr,*record.length]
            arr = [*arr,*record.data]
        arr = [*arr,*[ord(x) for x in self._FOOTER]]
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
        return bytes(self.get_bytearray())

    def print_summary(self):
        for record in self.get_records():
            print(record.get_summary())

    def save(self, filename=""):
        with open(filename, "wb") as file:
            file.write(self.get_binary())

class Record():
    def __init__(self, offset, data, length):
        self.offset = [
            int(x) for x in wrap(
                str(offset).zfill(6),
                2
            )
        ]
        self.length = [
            int(x) for x in wrap(
                str(length).zfill(4),
                2
            )
        ]
        self.data = data

    def get_pretty_offset(self):
        offset = self.offset
        offset = "0x" + "".join([str(x).zfill(2) for x in offset])
        return offset
    def get_pretty_length(self):
        length = self.length
        length = "0x" + "".join([str(x).zfill(2) for x in length])
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
    patch = IPSFile()
    patch.add_record(0,[64])
    patch.add_record(1,[128])
    patch.add_record(2,[2,4])
    print(patch.get_bytearray())
    print(patch.get_array())
    print(patch.get_dict())
    print(patch.get_binary())
    print(patch.get_records())

    patch.save("./patch.ips")
