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
        # Compress 3BPP
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
        lz2.compress_to_file(ubin_src_filepath)

        # Compare live comp to canned comp
        #FIXME: Fails for now
        bin_src_filepath = os.path.join(
            os.path.dirname(ubin_src_filepath).replace(
                os.path.join("","app",""),
                os.path.join("","user","")
            ),
            f"{os.path.basename(ubin_src_filepath)}".replace("u_","c_")
        )

        passed = filecmp.cmp(
            # canned comp
            os.path.join(
                os.path.dirname(bin_src_filepath),
                os.path.basename(bin_src_filepath)
            ),
            # live comp
            bin_src_filepath
        )
        if passed:
            print(" Comps DO match!")
        else:
            print(" Comps do NOT match!")

        # Decompress what we compressed
        print("Decompress what we compressed")
        ucbin_src_filepath = os.path.join(
            os.path.dirname(bin_src_filepath),
            f"u{os.path.basename(bin_src_filepath)}"
        )
        lz2.decompress_to_file(
            bin_src_filepath,
            ucbin_src_filepath
        )

        # Decompressed 3BPP -> PNG
        print(" Convert that to PNG")
        lz2.convert_3bpp_to_png(ucbin_src_filepath)

        passed = filecmp.cmp(
            # canned png
            os.path.join(
                os.path.dirname(bin_src_filepath),
                f"u{os.path.splitext(os.path.basename(bin_src_filepath))[0]}_p-preview.png"
            ),
            # live png
            os.path.join(
                os.path.dirname(ucbin_src_filepath),
                f"{os.path.splitext(os.path.basename(ucbin_src_filepath))[0]}_p-preview.png"
            )
        )
        if passed:
            print("  PNGs DO match!")
        else:
            print("  PNGs do NOT match!")

if __name__ == "__main__":
    if VERBOSE:
        print("LZ2 COMPRESSION")
        print('.' * 70)

    unittest.main()
