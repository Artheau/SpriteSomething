#includes routines that load the rom and apply bugfixes
#inherits from the generic romhandler

from source.snes import romhandler as snes

class RomHandler(snes.RomHandlerParent):
	def __init__(self, filename):
		super().__init__(filename)	#do the usual stuff
