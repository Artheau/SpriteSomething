#GARBAGE COLLECTION TESTS
#this file should contain tests that probe for memory leaks and any other mismanagement of RAM

import test_common   #contains utilities common to all tests.  Should come first before the other imports.

import unittest     #for unit testing, har har
import os           #for path.join and similar, to find the files we want to audit

#this next class is inspired by a suggestion from Fry: https://www.youtube.com/watch?v=1Isjgc0oX0s
class NoMemoryLeaks(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def test_sprites_and_games_are_destroyed(self):
		import tkinter as tk
		import weakref       #we weakref something to see if it was garbage collected
		from source import gui

		
		#make the GUI in skeleton form (no looping)
		pseudo_command_line_args = {"sprite": os.path.join("resources","zelda3","link","link.zspr")}
		pseudo_root = tk.Tk()   #make a pseudo GUI environment
		pseudo_root.withdraw()  #make the pseudo GUI invisible
		GUI_skeleton = gui.SpriteSomethingMainFrame(pseudo_root, pseudo_command_line_args)

		#save a weakref to the old sprite
		old_sprite_ref = weakref.ref(GUI_skeleton.sprite)
		old_game_ref = weakref.ref(GUI_skeleton.game)

		#try to load a new sprite
		GUI_skeleton.load_sprite(os.path.join("resources","metroid3","samus","samus.png"))

		#see if the old classes were garbage collected
		self.assertTrue(old_sprite_ref() is None)
		self.assertTrue(old_game_ref() is None)

		#now go the other way around and test going to Zelda3 from Metroid3
		old_sprite_ref = weakref.ref(GUI_skeleton.sprite)
		old_game_ref = weakref.ref(GUI_skeleton.game)
		GUI_skeleton.load_sprite(os.path.join("resources","zelda3","link","link.zspr"))
		self.assertTrue(old_sprite_ref() is None)
		self.assertTrue(old_game_ref() is None)


if __name__ == '__main__':
	unittest.main()
