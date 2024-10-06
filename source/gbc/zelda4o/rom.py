#includes routines that load the rom and apply bugfixes
#inherits from the generic romhandler

from source.gbc import romhandler as gbc

class RomHandler(gbc.RomHandlerParent):
    def __init__(self, filename):
        super().__init__(filename)
