import unittest         # tests
from source.meta import ssDiagnostics as diags

global VERBOSE
VERBOSE = True
# VERBOSE = False

class DiagnosticsAudit(unittest.TestCase):
    def set_Up(self, *args):
        pass

    def test_diagnostics(self):
        print("\n".join(diags.output()))

if __name__ == "__main__":
    if VERBOSE:
        print("DIAGNOSTICS")
        print('.' * 70)

    unittest.main()
