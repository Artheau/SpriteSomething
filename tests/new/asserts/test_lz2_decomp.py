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

class LZ2DecompressionAudit(unittest.TestCase):
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
            1) Compressed   3BPP -> Decompressed 3BPP
            2) Decompressed 3BPP -> PNG
            3) PNG               -> Decompressed 3BPP
        """

        # Compressed 3BPP -> Decompressed 3BPP
        if VERBOSE:
            print("Decompress 3BPP (.BIN) to .GFX")
        bin_src_filepath = os.path.join(
            "resources",
            "app",
            "snes",
            "zelda3",
            "triforcepiece",
            "sheets",
            "triforce.bin"
        )
        data_gfx_from_data_bin = lz2.decompress_to_file(bin_src_filepath, None, CHILD_VERBOSE)

        # Compare live decomp to canned decomp
        passed = filecmp.cmp(
            # canned decomp
            os.path.splitext(bin_src_filepath)[0] + ".gfx",
            # live decomp
            data_gfx_from_data_bin
        )
        print(f"gfx   -> bin  : ", end="")
        if passed:
            print("BINs  do match")
        else:
            print("BINs  do NOT match!")
        try:
            self.assertTrue(passed)
        except AssertionError as e:
            testErrors.append(str(e))

        # Decompressed 3BPP -> PNG
        if VERBOSE:
            print("Convert GFX to PNG")
        png_from_data_gfx = lz2.convert_3bpp_to_png(data_gfx_from_data_bin, None, CHILD_VERBOSE).replace("p-preview","p-2")
        passed = filecmp.cmp(
            # canned png
            os.path.join(
                os.path.dirname(bin_src_filepath),
                f"{os.path.splitext(os.path.basename(bin_src_filepath))[0]}_p-2.png"
            ),
            # live png
            png_from_data_gfx
        )
        print(f"gfx   -> png  : ", end="")
        if passed:
            print("PNGs  do match")
        else:
            print("PNGs  do NOT match!")
        try:
            self.assertTrue(passed)
        except AssertionError as e:
            testErrors.append(str(e))

        # PNG -> Decompressed 3BPP
        if VERBOSE:
            print("Convert PNG to GFX")
        data_gfx_from_png = lz2.convert_png_to_3bpp(png_from_data_gfx, None, CHILD_VERBOSE)
        passed = filecmp.cmp(
            # what we decompressed earlier
            data_gfx_from_data_bin,
            # live 3bpp
            data_gfx_from_png
        )
        print(f"png   -> gfx  : ", end="")
        if passed:
            print("GFXs  do match")
        else:
            print("GFXs  do NOT match!")
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
        print("LZ2 DECOMPRESSION")
        print('.' * 70)

    unittest.main()
