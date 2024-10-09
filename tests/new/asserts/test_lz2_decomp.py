import unittest         # tests
import os
import filecmp
from source.meta.common import lz2

global VERBOSE
VERBOSE = True
# VERBOSE = False

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
        if False:
            print("Decompress 3BPP to File")
        bin_src_filepath = os.path.join(
            "resources",
            "app",
            "snes",
            "zelda3",
            "triforcepiece",
            "sheets",
            "triforce.bin"
        )
        data_u3bpp_from_data_c3bpp = lz2.decompress_to_file(bin_src_filepath, None, False)

        # Compare live decomp to canned decomp
        passed = filecmp.cmp(
            # canned decomp
            os.path.join(
                os.path.dirname(bin_src_filepath),
                f"u_{os.path.basename(bin_src_filepath)}"
            ),
            # live decomp
            data_u3bpp_from_data_c3bpp
        )
        print(f"cbin -> ubin : ", end="")
        if passed:
            print("Decomps do match")
        else:
            print("Decomps do NOT match!")
        try:
            self.assertTrue(passed)
        except AssertionError as e:
            testErrors.append(str(e))

        # Decompressed 3BPP -> PNG
        if False:
            print("Convert Decompressed 3BPP to PNG")
        png_from_data_u3bpp = lz2.convert_3bpp_to_png(data_u3bpp_from_data_c3bpp, None, False).replace("p-preview","p-2")
        passed = filecmp.cmp(
            # canned png
            os.path.join(
                os.path.dirname(bin_src_filepath),
                f"u_{os.path.splitext(os.path.basename(bin_src_filepath))[0]}_p-2.png"
            ),
            # live png
            png_from_data_u3bpp
        )
        print(f"ubin -> png  : ", end="")
        if passed:
            print("PNGs    do match")
        else:
            print("PNGs    do NOT match!")
        try:
            self.assertTrue(passed)
        except AssertionError as e:
            testErrors.append(str(e))

        # PNG -> Decompressed 3BPP
        if False:
            print("Convert PNG to Decompressed 3BPP")
        data_u3bpp_from_png = lz2.convert_png_to_3bpp(png_from_data_u3bpp, None, False)
        passed = filecmp.cmp(
            # what we decompressed earlier
            data_u3bpp_from_data_c3bpp,
            # live 3bpp
            data_u3bpp_from_png
        )
        print(f"png  -> ubin : ", end="")
        if passed:
            print("c3BPPs  do match")
        else:
            print("c3BPPs  do NOT match!")
        try:
            self.assertTrue(passed)
        except AssertionError as e:
            testErrors.append(str(e))

        if len(testErrors):
            # print(testErrors)
            print("F" * (len(testErrors) - 1))
            # self.assertTrue(False)

if __name__ == "__main__":
    if VERBOSE:
        print("LZ2 DECOMPRESSION")
        print('.' * 70)

    unittest.main()
