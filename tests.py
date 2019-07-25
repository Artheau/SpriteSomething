#unit testing framework
#I have no idea what I'm doing:  http://www.quickmeme.com/meme/3p0di5

import unittest     #for unit testing, har har
import json         #need to audit our json files
import os           #for path.join and similar, to find the files we want to audit
import sys			#so that we can check to see which modules are imported at any given time

class SamusAnimationAudit(unittest.TestCase):
	#TODO: these types of tests should be extended to all sprites
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		with open(os.path.join("resources","metroid3","samus","animations.json")) as inFile:
			self.samus_animations = json.load(inFile)
		with open(os.path.join("resources","metroid3","samus","layout.json")) as inFile:
			self.samus_layout = json.load(inFile)

	def test_animations_use_valid_image_names(self):
		#if this fails, it is because there is an animation in animations.json that references an image from layout.json that doesn't exist
		referenced_images = set()
		for animation in self.samus_animations.values():
			for directed_animation in animation.values():
				for pose in directed_animation: #directed_animation is a list, not a dict
					for tile in pose["tiles"]:  #pose["tiles"] is a list, not a dict
						referenced_images.add(tile["image"])

		supplied_images = set(self.samus_layout["images"].keys())
		bad_image_references = referenced_images.difference(supplied_images)
		self.assertEqual(0,len(set(bad_image_references)))

	def test_no_duplicate_image_definitions_in_layout(self):
		#if this fails, it is because there are two images in the layout with the same name
		supplied_images = self.samus_layout["images"].keys()
		self.assertEqual(len(set(supplied_images)),len(supplied_images))

	#TODO: write this so that it properly handles images like cannons that aren't specifically in the main DMA block
	# def test_dma_sequence_includes_all_images_from_layout(self):
	# 	#if this fails, it is because there is a DMA sequence specified in the layout, but it doesn't include all of the images
	# 	supplied_images = self.samus_layout["images"].keys()
	# 	dma_sequence_images = self.samus_layout["dma_sequence"]
	# 	self.assertEqual(dma_sequence_images, supplied_images)


class DontGoChasingWaterfalls(unittest.TestCase):
	#these tests are to make sure that we are are using class dependencies correctly,
	# and that all information flows downwards.

	#TODO: extend this test to all sprites
	def test_no_tk_in_sprite_class(self):
		#there should be no references to tkinter in the sprite class, because it is supposed to work from the CLI also.
		from source.metroid3.samus import sprite
		self.assertFalse('tkinter' in sys.modules)

#this next class is inspired by a suggestion from Fry: https://www.youtube.com/watch?v=1Isjgc0oX0s
class NoMemoryLeaks(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	#TODO: extend this test to a more general case
	def test_sprites_and_games_are_destroyed(self):
		import tkinter as tk
		import weakref       #we weakref something to see if it was garbage collected
		from source import gui

		
		#make the GUI in skeleton form (no looping)
		pseudo_command_line_args = {"sprite": os.path.join("resources","zelda3","link","link.zspr")}
		pseudo_root = tk.Tk()   #make a pseudo GUI environment
		pseudo_root.withdraw()  #make the pseudo GUI invisible
		GUI_skeleton = gui.SpriteSomethingMainFrame(pseudo_root, pseudo_command_line_args)

		#make sure the photoimage wrapper is not bypassed #TODO: move to its own test
		try:
			tk.PhotoImage(file=os.path.join("resources","meta","icons","blank.png"))
			self.assertFalse("The wrapper in gui_common.py to prevent PNG files from going to PhotoImage has been disabled, maybe by a tk import?")
		except AssertionError:
			self.assertTrue(True)

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
