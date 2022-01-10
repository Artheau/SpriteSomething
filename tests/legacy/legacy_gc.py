#GARBAGE COLLECTION TESTS
#this file should contain tests that probe for memory leaks and any other mismanagement of RAM

from tests.legacy.common_vars import *  #contains utilities common to all tests.  Should come first before the other imports.

import unittest     #for unit testing, har har
import os           #for path.join and similar, to find the files we want to audit
import weakref      #we weakref something to see if it was garbage collected

#this next class is inspired by a suggestion from Fry: https://www.youtube.com/watch?v=1Isjgc0oX0s
class NoMemoryLeaks(unittest.TestCase):
    def setUp(self):
        import tkinter as tk

        self.pseudo_root = tk.Tk()   #make a pseudo GUI environment

    def test_sprites_and_games_are_destroyed(self):
        from source.meta.gui import gui
        #make the GUI in skeleton form (no looping)
        pseudo_command_line_args = {"sprite": LINK_FILENAME}

        self.pseudo_root.withdraw()  #make the pseudo GUI invisible
        GUI_skeleton = gui.SpriteSomethingMainFrame(self.pseudo_root, pseudo_command_line_args)

        #save a weakref to the old sprite
        old_sprite_ref = weakref.ref(GUI_skeleton.sprite)
        old_game_ref = weakref.ref(GUI_skeleton.game)
        old_animation_engine_ref = weakref.ref(GUI_skeleton.animation_engine)

        #try to load a new sprite
        GUI_skeleton.load_sprite(SAMUS_FILENAME)

        #see if the old classes were garbage collected
        self.assertTrue(old_sprite_ref() is None)
        self.assertTrue(old_game_ref() is None)
        self.assertTrue(old_animation_engine_ref() is None)

        #now go the other way around and test going to Zelda3 from Metroid3
        old_sprite_ref = weakref.ref(GUI_skeleton.sprite)
        old_game_ref = weakref.ref(GUI_skeleton.game)
        old_animation_engine_ref = weakref.ref(GUI_skeleton.animation_engine)
        GUI_skeleton.load_sprite(LINK_FILENAME)
        self.assertTrue(old_sprite_ref() is None)
        self.assertTrue(old_game_ref() is None)
        self.assertTrue(old_animation_engine_ref() is None)


if __name__ == '__main__':
    unittest.main()
