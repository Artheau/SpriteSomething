#common functions to all games
#handling backgrounds, etc.
#contains a manifest of all the sprites
#handles import of new sprites

import os
import importlib
import json
from PIL import Image
from source import romhandler
#from .metroid3 import game,rom
#from .zelda3 import game,rom

def autodetect(sprite_filename):
	#need to autodetect which game, and which sprite
	#then return an instance of THAT game's class, and an instance of THAT sprite
	_,file_extension = os.path.splitext(sprite_filename)
	if file_extension.lower() in [".sfc","smc"]:
		#If the file is a rom, then we can go into the internal header and get the name of the game
		game = get_game_class_of_type(get_game_type_from_rom(sprite_filename))
		#And by default, we will grab the player sprite from this game
		sprite = game.make_player_sprite(sprite_filename)
	elif file_extension.lower() == ".png":
		#I'm not sure what to do here yet.  For right now I am going to assume that if it is a big file, it is Samus, else Link
		loaded_image = Image.open(sprite_filename) 
		if loaded_image.size == (128,488):      #This is the size of Z3Link's sheet
			game = get_game_class_of_type("zelda3")
			sprite = game.make_player_sprite(sprite_filename)
		elif loaded_image.size[0] > 800 and loaded_image.size[1] > 2000:
			game = get_game_class_of_type("metroid3")
			sprite = game.make_player_sprite(sprite_filename)
		else:
			raise AssertionError(f"Cannot recognize the type of file {sprite_filename} from its size")
	elif file_extension.lower() == ".zspr":
		game = get_game_class_of_type(get_game_type_from_zspr(sprite_filename))
		sprite = game.make_sprite_by_number(get_sprite_number_from_zspr(sprite_filename),sprite_filename)
	else:
		raise AssertionError(f"Cannot recognize the type of file {sprite_filename} from its filename")
	return game, sprite

def get_game_class_of_type(game_name):
	#dynamic import
	game_module = importlib.import_module(f"source.{game_name}.game")
	return game_module.Game()



class GameParent():
	#parent class for games to inherit
	def __init__(self):
		self.name = "Game Parent Class"    #to be replaced by a name like "Super Metroid"
		self.internal_name = "meta"        #to be replaced by the specific folder name that this app uses, e.g. "metroid3"

	#to make a new game class, you must write code for all of the functions in this section below.
	############################# BEGIN ABSTRACT CODE ##############################



	############################# END ABSTRACT CODE ##############################

	#the functions below here are special to the parent class and do not need to be duplicated

	def make_player_sprite(self, sprite_filename):
		return self.make_sprite_by_number(0x01, sprite_filename)

	def make_sprite_by_number(self, sprite_number, sprite_filename):
		#go into the manifest and get the actual name of the sprite
		with open(os.path.join("source",self.internal_name,"manifest.json")) as file:
			manifest = json.load(file)
		if str(sprite_number) in manifest:
			folder_name = manifest[str(sprite_number)]["folder name"]
			#dynamic import
			sprite_module = importlib.import_module(f"source.{self.internal_name}.{folder_name}.sprite")
			return sprite_module.Sprite(manifest[str(sprite_number)],os.path.join(self.internal_name,folder_name))
		else:
			raise AssertionError(f"make_sprite_by_number() called for non-implemented sprite_number {sprite_number}")

