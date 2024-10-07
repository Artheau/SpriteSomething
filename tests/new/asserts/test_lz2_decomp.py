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
        # Compressed 3BPP -> Decompressed 3BPP
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
        lz2.decompress_to_file(bin_src_filepath)

        # Compare live decomp to canned decomp
        ubin_src_filepath = os.path.join(
            os.path.dirname(bin_src_filepath).replace(
                os.path.join("","app",""),
                os.path.join("","user","")
            ),
            f"u_{os.path.basename(bin_src_filepath)}"
        )

        passed = filecmp.cmp(
            # canned decomp
            os.path.join(
                os.path.dirname(bin_src_filepath),
                f"u_{os.path.basename(bin_src_filepath)}"
            ),
            # live decomp
            ubin_src_filepath
        )
        if passed:
            print(" Decomps DO match!")
        else:
            print(" Decomps do NOT match!")

        # Decompressed 3BPP -> PNG
        print("Convert Decompressed 3BPP to PNG")
        lz2.convert_3bpp_to_png(ubin_src_filepath)
        passed = filecmp.cmp(
            # canned png
            os.path.join(
                os.path.dirname(bin_src_filepath),
                f"u_{os.path.splitext(os.path.basename(bin_src_filepath))[0]}_p-preview.png"
            ),
            # live png
            os.path.join(
                os.path.dirname(ubin_src_filepath),
                f"{os.path.splitext(os.path.basename(ubin_src_filepath))[0]}_p-preview.png"
            )
        )
        if passed:
            print(" PNGs DO match!")
        else:
            print(" PNGs do NOT match!")

if __name__ == "__main__":
    if VERBOSE:
        print("LZ2 DECOMPRESSION")
        print('.' * 70)

    unittest.main()
