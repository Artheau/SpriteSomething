import unittest         # tests
import os
import filecmp
from source.meta.common import lz2

global SOLID_ALGO
SOLID_ALGO = False

global LABEL
LABEL = True
# LABEL = False

global VERBOSE
# VERBOSE = True
VERBOSE = False

global CHILD_VERBOSE
# CHILD_VERBOSE = True
CHILD_VERBOSE = False

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
        if VERBOSE:
            print("Compress 3BPP to File")
        gfx_src_filepath = os.path.join(
            ".",
            "resources",
            "app",
            "snes",
            "zelda3",
            "triforcepiece",
            "sheets",
            "triforce.gfx"
        )
        cgfx_src_filepath = lz2.compress_to_file(gfx_src_filepath, None, CHILD_VERBOSE)

        # Compare live comp to canned comp
        passed = filecmp.cmp(
            # canned comp
            gfx_src_filepath,
            # live comp
            cgfx_src_filepath
        )
        print("gfx   -> cgfx : ", end="")
        if passed:
            print("Comps do match")
        else:
            print("Comps do NOT match!")
        try:
            self.assertTrue(passed)
        except AssertionError as e:
            testErrors.append(str(e))

        # Decompress what we compressed
        if VERBOSE:
            print("Decompress what we compressed")
        ucgfx_src_filepath = lz2.decompress_to_file(cgfx_src_filepath, None, CHILD_VERBOSE)

        # Decompressed 3BPP -> PNG
        if VERBOSE:
            print(" Convert that to PNG")
        ucgfx_png_filepath = lz2.convert_3bpp_to_png(ucgfx_src_filepath, None, CHILD_VERBOSE).replace("p-preview","p-2")

        passed = filecmp.cmp(
            # canned png
            ucgfx_png_filepath.replace(
                os.path.join("","user",""),
                os.path.join("","app","")
            ).replace(
                "c_",""
            ),
            # live png
            ucgfx_png_filepath
        )
        print("ucgfx -> png  : ", end="")
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
            if SOLID_ALGO:
                self.assertTrue(False)
            else:
                print("F" * (max(1, len(testErrors) - 1)))

if __name__ == "__main__":
    if LABEL:
        print("LZ2 COMPRESSION")
        print('.' * 70)

    unittest.main()
