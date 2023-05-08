import unittest
import os

from source.meta.classes.spritelib import SpriteParent


class SpriteParentTestVersion(SpriteParent):
	#the unit test should not depend on the layout class
	def load_layout(self, sprite_name):
		#TODO: Make a fake interface to test this
		return None

	#the unit test should not depend on the particular sprite data files
	def load_animations(self, sprite_name):
		#TODO: Make a fake interface to test this
		return None

	#the unit test should not depend on external files
	def import_from_filename(self):
		#TODO: Make a fake interface to test this
		return None

	def import_from_PNG(self):
		#TODO: Make a fake interface to test this
		return None

	def import_from_ZSPR(self):
		#TODO: Make a fake interface to test this
		return None

	#don't import other modules for unit test
	def import_module(self, module_name):
		self.latest_attempted_import = module_name

		class fake_module():
			@staticmethod
			def Plugins():
				return module_name

		return fake_module()

	def get_tiles_for_pose(self, animation, direction, pose_number, palettes, frame_number):
		#TODO
		return None

	def get_palette_loop_timer(self, animation, direction, palettes):
		#TODO
		return None

	def get_pose_list(self, animation, direction):
		#TODO
		return None

	def assemble_tiles_to_completed_image(self, tile_list):
		#TODO
		return None

	def get_image(self, animation, direction, pose, palettes, frame_number):
		#TODO
		return None

	def get_representative_images(self,style="default"):
		#TODO
		return None

	def save_as(self, filename, game_name):
		#TODO
		return None

	def save_as_PNG(self, filename):
		#TODO
		return None

	def save_as_ZSPR(self, filename):
		#TODO
		return None

	def save_as_RDC(self, filename):
		#TODO
		return None

	def get_master_PNG_image(self):
		#TODO
		return None



class TestSpriteParent(unittest.TestCase):
	__TEST_NAME = "Test_Sprite"
	__SUBPATH = "."
	__FILENAME = "test.zspr"

	###############################
	# testing SpriteParent.__init()
	###############################

	def setUp(self):
		filename = self.__FILENAME
		manifest_dict = {"name": self.__TEST_NAME}
		my_subpath = self.__SUBPATH
		self.sprite = SpriteParentTestVersion(filename, manifest_dict, my_subpath, "")

	def test_name_assigned(self):
		self.assertEqual(self.sprite.classic_name, self.__TEST_NAME)

	def test_subpath_assigned(self):
		self.assertEqual(self.sprite.resource_subpath, self.__SUBPATH)

	def test_metadata_initialized_to_blank(self):
		for value in self.sprite.metadata.values():
			self.assertEqual(value, "")

	def test_filename_assigned(self):
		self.assertEqual(self.sprite.filename, self.__FILENAME)

	def test_default_scale_is_set(self):
		self.assertTrue(self.sprite.overview_scale_factor > 0.0)

	def test_default_scale_can_be_overriden(self):
		custom_scale = 3.14159
		filename = self.__FILENAME
		custom_scale_manifest_dict = {
			"name": self.__TEST_NAME,
			"input": {
				"png": {
					"overview-scale-factor": custom_scale
				}
			}
		}
		my_subpath = self.__SUBPATH
		custom_scale_sprite = SpriteParentTestVersion(filename, custom_scale_manifest_dict, my_subpath)
		self.assertTrue(custom_scale_sprite.overview_scale_factor != self.sprite.overview_scale_factor)
		self.assertEqual(custom_scale_sprite.overview_scale_factor, custom_scale)

	def test_no_default_plugins(self):
		self.assertTrue(self.sprite.plugins is None)
		self.assertFalse(self.sprite.has_plugins)

	###############################
	# testing SpriteParent.load_plugins()
	###############################

	def test_tries_to_load_correct_plugin_module(self):
		fake_path_elements = ["you", "must", "construct_additional_pylons"]
		intended_import = f"source.{'.'.join(fake_path_elements)}.plugins"
		self.sprite.resource_subpath = os.path.join(*fake_path_elements)
		self.sprite.load_plugins()
		self.assertEqual(self.sprite.latest_attempted_import, intended_import)
		self.assertEqual(self.sprite.plugins, intended_import)
		self.assertTrue(self.sprite.has_plugins)

	###############################
	# testing SpriteParent.get_palette()
	###############################

	def test_default_get_palette(self):
		self.sprite.master_palette = [x**2 for x in range(10)]
		interval = (3,5)
		intended_returnvalue = self.sprite.master_palette[interval[0]:interval[1]]
		returnvalue = self.sprite.get_palette(None, interval, None)
		self.assertEqual(returnvalue, intended_returnvalue)

	###############################
	# testing SpriteParent.get_palette_duration()
	###############################

	def test_default_get_palette_duration(self):
		self.assertEqual(1, self.sprite.get_palette_duration(None))

	###############################
	# testing SpriteParent.get_supplemental_tiles()
	###############################

	def test_get_supplemental_tiles(self):
		tiles = self.sprite.get_supplemental_tiles(None,None,None,None,None)
		self.assertEqual(tiles, [])

	###############################
	# testing SpriteParent.import_cleanup()
	###############################

	def test_import_cleanup(self):
		#at this time, this function has no whitebox functionality
		self.sprite.import_cleanup()

	###############################
	# testing SpriteParent.get_alternative_direction()
	###############################

	def test_get_alternative_direction(self):
		dummy_animation = "DUMMY_KEY"
		dummy_direction = "south by southwest"
		self.sprite.animations = {dummy_animation: {dummy_direction: None}}
		direction = self.sprite.get_alternative_direction(dummy_animation, None)
		self.assertEqual(direction, dummy_direction)

	###############################
	# testing SpriteParent.get_alternate_tile()
	###############################

	def test_get_alternate_tile(self):
		with self.assertRaises(AssertionError):
			self.sprite.get_alternate_tile("", None)

	###############################
	# testing SpriteParent.get_rdc_meta_data_block()
	###############################

	def test_get_rdc_meta_data_block(self):
		#regression test.	I don't understand RDC format.
		self.sprite.metadata = {
			"sprite.name": "Baby Got Back",
			"author.name": "Sir Mix-A-Lot",
		}
		intended_output = [(0, bytearray(b'2\x00\x00\x00{"title":"Baby Got Back","author":"Sir Mix-A-Lot"}'))]
		self.assertEqual(intended_output, self.sprite.get_rdc_meta_data_block())
