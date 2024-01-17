#unit testing framework
#I have no idea what I'm doing:  http://www.quickmeme.com/meme/3p0di5
#
#
#The intention is that most unit tests will go here, excepting the ones that do not play well with the others,
# which at the time of writing this comment, are the tests for memory leaks and stray imports (test_gc.py and test_waterfalls.py)

from tests.legacy.common_vars import LINK_FILENAME,LINK_RESOURCE_PATH,LINK_RESOURCE_SUBPATH,SAMUS_FILENAME,SAMUS_RESOURCE_PATH,SAMUS_RESOURCE_SUBPATH  #contains utilities common to all tests.  Should come first before the other imports.

import unittest     #for unit testing, har har
import json         #need to audit our json files
import os           #for path.join and similar, to find the files we want to audit
import tkinter as tk   #testing tk wrappers
import tempfile   #for mock-saving files, in order to check the validity of the save
from PIL import ImageChops #for testing if images are same/different

from source.meta.gui import gui #need to import the GUI to test it
from source.snes.zelda3.link import sprite as link_sprite_library
from source.snes.metroid3.samus import sprite as samus_sprite_library

class ExportAudit(unittest.TestCase):
	def same(self, file1, file2):   #not a test, just a helper function
		return file1.read() == file2.read()

	def test_link_zspr_export(self):
		link_sprite = link_sprite_library.Sprite(LINK_FILENAME, {"name":"Link"}, LINK_RESOURCE_SUBPATH)
		_, temporary_zspr_filename = tempfile.mkstemp()
		self.assertTrue(link_sprite.save_as_ZSPR(temporary_zspr_filename))
		with open(LINK_FILENAME,"rb") as original_file_contents:
			with open(temporary_zspr_filename,"rb") as temp_zspr:
				self.assertTrue(self.same(original_file_contents,temp_zspr))

	def test_link_rdc_export(self):
		link_sprite = link_sprite_library.Sprite(LINK_FILENAME, {"name":"Link"}, LINK_RESOURCE_SUBPATH)
		_, temporary_rdc_filename = tempfile.mkstemp()
		self.assertTrue(link_sprite.save_as_RDC(temporary_rdc_filename))
		LINK_RDC_FILENAME = os.path.join(LINK_RESOURCE_PATH,"sheets","link.rdc")
		with open(LINK_RDC_FILENAME,"rb") as original_file_contents:
			with open(temporary_rdc_filename,"rb") as temp_rdc:
				self.assertTrue(self.same(original_file_contents,temp_rdc))

	def test_samus_rdc_export(self):
		return
		samus_sprite = samus_sprite_library.Sprite(SAMUS_FILENAME, {"name":"Samus"}, SAMUS_RESOURCE_SUBPATH)
		_, temporary_rdc_filename = tempfile.mkstemp()
		self.assertTrue(samus_sprite.save_as_RDC(temporary_rdc_filename))
		SAMUS_RDC_FILENAME = os.path.join(SAMUS_RESOURCE_PATH,"sheets","samus.rdc")
		with open(SAMUS_RDC_FILENAME,"rb") as original_file_contents:
			with open(temporary_rdc_filename,"rb") as temp_rdc:
				self.assertTrue(self.same(original_file_contents,temp_rdc))

class SamusAnimationAudit(unittest.TestCase):
	#TODO: these types of tests should be extended to all sprites
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		with open(os.path.join(SAMUS_RESOURCE_PATH,"manifests","animations.json")) as inFile:
			self.samus_animations = json.load(inFile)
			if "$schema" in self.samus_animations: #skip schema definition as it's not an animation
				del self.samus_animations["$schema"]
		with open(os.path.join(SAMUS_RESOURCE_PATH,"manifests","layout.json")) as inFile:
			self.samus_layout = json.load(inFile)

	def test_animations_use_valid_image_names(self):
		#if this fails, it is because there is an animation in animations.json that references an image from layout.json that doesn't exist
		referenced_images = set()
		for animation in self.samus_animations.values():
			for directed_animation in animation.values():
				for pose in directed_animation: #directed_animation is a list, not a dict
					for tile in pose["tiles"]:  #pose["tiles"] is a list, not a dict
						if not tile["image"].startswith("optional_"):
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

class SpiffyButtonAudit(unittest.TestCase):
	#checks to make sure that sprites respond to the commands from things like spiffy buttons
	#added this test because our spiffy buttons kept breaking every tiem there was a typoe
	def image_is_same(self, image1, image2):  #not a test; don't name this "test"
		diff = ImageChops.difference(image1, image2)
		image1_colors = {color:count for (count,color) in image1.getcolors()}
		image2_colors = {color:count for (count,color) in image2.getcolors()}
		#no bbox if they are the same
		return (diff.getbbox() is None) and \
			(image1_colors == image2_colors) #AND they are drawing from the same palette (Pillow 7.0 made this line necessary)

	def test_link_palette_audit(self):
		PALETTES_TO_CHECK = [	[],
								["power_gloves"],
								["titan_gloves"],
								["blue_mail", "titan_gloves"],
								["blue_mail", "power_gloves"],
								["blue_mail"],
								["red_mail"],
								["red_mail", "power_gloves"],
								["red_mail", "titan_gloves"],
								["titan_gloves"],
							]
		link_sprite = link_sprite_library.Sprite(LINK_FILENAME, {"name":"Link"}, LINK_RESOURCE_SUBPATH)

		old_image = None
		for i,_ in enumerate(PALETTES_TO_CHECK):
			new_image = link_sprite.get_image("Stand", "right", 0, PALETTES_TO_CHECK[i], 0)[0]
			if old_image is not None:
				with self.subTest(new_palette = PALETTES_TO_CHECK[i], old_palette = PALETTES_TO_CHECK[i-1]):
					self.assertFalse(self.image_is_same(old_image,new_image))
			old_image = new_image

	def test_samus_palette_audit(self):
		#TODO: Need to audit the timed palettes also
		PALETTES_TO_CHECK = [	[],
								["varia_suit"],
								["varia_suit","xray_variant"],
								["gravity_suit","xray_variant"],
								["gravity_suit"],
								[],
								["hyper_variant"],
								["xray_variant"],
								[],
								["sepia_variant"],
								["door_variant"],
								[],
							]
		samus_sprite = samus_sprite_library.Sprite(SAMUS_FILENAME, {"name":"Samus"}, SAMUS_RESOURCE_SUBPATH)

		old_image = None
		for i,_ in enumerate(PALETTES_TO_CHECK):
			new_image = samus_sprite.get_image("Stand", "right", 0, PALETTES_TO_CHECK[i], 0)[0]
			if old_image is not None:
				with self.subTest(new_palette = PALETTES_TO_CHECK[i], old_palette = PALETTES_TO_CHECK[i-1]):
					self.assertFalse(self.image_is_same(old_image,new_image))
			old_image = new_image


class GUIRunTimeTests(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		#make the GUI in skeleton form (no looping)
		pseudo_command_line_args = {"sprite": LINK_FILENAME}
		print("Emulated DISPLAY: %s" % os.getenv("DISPLAY","None"))
		pseudo_root = tk.Tk()   #make a pseudo GUI environment
		pseudo_root.withdraw()  #make the pseudo GUI invisible
		self.GUI_skeleton = gui.SpriteSomethingMainFrame(pseudo_root, pseudo_command_line_args)

	def minitest_photoimage_does_not_accept_png_files(self):
		#make sure the photoimage wrapper is not bypassed #TODO: move to its own test
		try:
			temp = tk.PhotoImage(file=os.path.join("resources","app","meta","icons","blank.png"))   #any PNG file can be used here
			self.assertFalse("The wrapper in gui_common.py to prevent PNG files from going to PhotoImage has been disabled, maybe by a tk import?")
		except AssertionError:
			try:
				temp = tk.PhotoImage(file=os.path.join("resources","app","meta","icons","app.gif"))   #any GIF file can be used here
				self.assertTrue(True)
			except AssertionError:
				self.assertFalse("tk.PhotoImage is not accepting GIF files.  Has it been rerouted?")

	def minitest_zoom_function_does_not_crash_app(self):
		#TODO: tie this test to the button press hooks directly
		self.GUI_skeleton.current_zoom = 1.7
		self.GUI_skeleton.game.update_background_image()
		self.GUI_skeleton.update_sprite_animation()

	def test_runtime(self):
		self.minitest_photoimage_does_not_accept_png_files()
		self.minitest_zoom_function_does_not_crash_app()

if __name__ == '__main__':
	unittest.main()
