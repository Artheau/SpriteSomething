#includes routines that load the rom and apply bugfixes
#inherits from the generic romhandler

from source.romhandler import RomHandlerParent

class RomHandler(RomHandlerParent):
	def __init__(self, filename):
		super().__init__(filename)      #do the usual stuff

		self._apply_bugfixes()
		self._apply_improvements()

	def _apply_improvements(self):
		#these are not mandatory for the animation viewer to work, but they are general quality of life improvements
		# that I recommend to make.
		return True

	def _apply_bugfixes(self):
		#these are significant typos that reference bad palettes or similar, and would raise assertion errors in any clean code
		return True
