#unit testing framework
#I have no idea what I'm doing:  http://www.quickmeme.com/meme/3p0di5
#
#
#The intention is that most unit tests will go here, excepting the ones that do not play well with the others,
# which at the time of writing this comment, are the tests for memory leaks and stray imports (test_gc.py and test_waterfalls.py)

import test_common   #contains utilities common to all tests.  Should come first before the other imports.

import unittest     #for unit testing, har har
import json         #need to audit our json files
import os           #for path.join and similar, to find the files we want to audit
import tkinter as tk   #testing tk wrappers

from source import gui #need to import the GUI to test it

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


class GUIRunTimeTests(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		#make the GUI in skeleton form (no looping)
		pseudo_command_line_args = {"sprite": os.path.join("resources","zelda3","link","link.zspr")}
		pseudo_root = tk.Tk()   #make a pseudo GUI environment
		pseudo_root.withdraw()  #make the pseudo GUI invisible
		self.GUI_skeleton = gui.SpriteSomethingMainFrame(pseudo_root, pseudo_command_line_args)

	def test_photoimage_does_not_accept_png_files(self):
		#make sure the photoimage wrapper is not bypassed #TODO: move to its own test
		try:
			tk.PhotoImage(file=os.path.join("resources","meta","icons","blank.png"))   #any PNG file can be used here
			self.assertFalse("The wrapper in gui_common.py to prevent PNG files from going to PhotoImage has been disabled, maybe by a tk import?")
		except AssertionError:
			try:
				tk.PhotoImage(file=os.path.join("resources","app.gif"))   #any GIF file can be used here
				self.assertTrue(True)
			except AssertionError:
				self.assertFalse("tk.PhotoImage is not accepting GIF files.  Has it been rerouted?")

if __name__ == '__main__':
	unittest.main()
