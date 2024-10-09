import unittest         # tests
import os
import filecmp
from source.meta.common import lz2

global VERBOSE
VERBOSE = True
# VERBOSE = False

class LZ2CompressionAudit(unittest.TestCase):
    def set_Up(self, *args):
        pass

    def same(self, file1, file2):
        '''
        Are these the same?
        '''
        return file1.read() == file2.read()

    def test_lz2(self):
        testErrors = []
        """
            1) Decompressed 3BPP -> Compressed   3BPP
            2) Compressed   3BPP -> Decompressed 3BPP
            3) Decompressed 3BPP -> PNG
        """

        # Compress 3BPP
        if False:
            print("Compress 3BPP to File")
        ubin_src_filepath = os.path.join(
            ".",
            "resources",
            "app",
            "snes",
            "zelda3",
            "triforcepiece",
            "sheets",
            "u_triforce.bin"
        )
        cbin_src_filepath = lz2.compress_to_file(ubin_src_filepath, None, False)

        # Compare live comp to canned comp
        passed = filecmp.cmp(
            # canned comp
            ubin_src_filepath,
            # live comp
            cbin_src_filepath
        )
        print("ubin  -> ucbin : ", end="")
        if passed:
            print("Comps do match")
        else:
            print("Comps do NOT match!")
        try:
            self.assertTrue(passed)
        except AssertionError as e:
            testErrors.append(str(e))

        # Decompress what we compressed
        if False:
            print("Decompress what we compressed")
        ucbin_src_filepath = lz2.decompress_to_file(cbin_src_filepath, None, False)

        # Decompressed 3BPP -> PNG
        if False:
            print(" Convert that to PNG")
        ucbin_png_filepath = lz2.convert_3bpp_to_png(ucbin_src_filepath, None, False).replace("p-preview","p-2")

        passed = filecmp.cmp(
            # canned png
            ucbin_png_filepath.replace(
                os.path.join("","user",""),
                os.path.join("","app","")
            ).replace(
                "u_c_","u_"
            ),
            # live png
            ucbin_png_filepath
        )
        print("ucbin -> png   : ", end="")
        if passed:
            print("PNGs  do match")
        else:
            print("PNGs  do NOT match!")
        try:
            self.assertTrue(passed)
        except AssertionError as e:
            testErrors.append(str(e))

        if len(testErrors):
            # print(testErrors)
            print("F" * (len(testErrors) - 1))
            self.assertTrue(False)

if __name__ == "__main__":
    if VERBOSE:
        print("LZ2 COMPRESSION")
        print('.' * 70)

    unittest.main()
