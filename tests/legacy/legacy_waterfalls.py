#these tests are to make sure that we are are using class dependencies correctly,
# and that all information flows downwards.
#
#in general, these tests should be testing the import framework

from tests.legacy.common_vars import *	 #contains utilities common to all tests.	Should come first before the other imports.

import unittest		 #for unit testing, har har
import sys			#so that we can check to see which modules are imported at any given time

class DontGoChasingWaterfalls(unittest.TestCase):
	def test_no_tk_in_sprite_class(self):
		#there should be no references to tkinter in the sprite class, because sprites are supposed to work from the CLI also.
		from source.snes.metroid3.samus import sprite as samus_sprite
		from source.snes.zelda3.link import sprite as link_sprite
		self.assertFalse('tkinter' in sys.modules)

if __name__ == '__main__':
	unittest.main()
