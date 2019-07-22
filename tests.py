#unit testing framework
#I have no idea what I'm doing:  http://www.quickmeme.com/meme/3p0di5

import unittest     #for unit testing, har har
import json         #need to audit our json files
import os           #for path.join and similar, to find the files we want to audit

#example:
#
# class TestStuff(unittest.TestCase):
# 	#all tests must start with "test_"
#     def test_make_sure_it_is_not_nothing(self):
#     	self.assertFalse("it" == None)
#
#     def test_make_sure_it_is_something(self):
#     	self.assertTrue("it" != None)
#
#     def test_make_sure_it_is_what_it_is(self):
#     	my_metaphor = "it"
#     	self.assertEqual(my_metaphor, "it")


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



if __name__ == '__main__':
    unittest.main()
