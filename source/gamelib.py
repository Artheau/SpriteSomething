#common functions to all games
#handling backgrounds, etc.
#handles import of new sprites

import os
import importlib
import json
import tkinter as tk
import random
import weakref    #because memory leaks are stupid
from PIL import Image, ImageTk
from source import widgetlib
from source import romhandler
from source import common

def autodetect(sprite_filename):
	#need to autodetect which game, and which sprite
	#then return an instance of THAT game's class, and an instance of THAT sprite
	_,file_extension = os.path.splitext(sprite_filename)
	if file_extension.lower() in [".sfc",".smc"]:
		#If the file is a rom, then we can go into the internal header and get the name of the game
		game = get_game_class_of_type(autodetect_game_type_from_rom_filename(sprite_filename))
		#And by default, we will grab the player sprite from this game
		sprite = game.make_player_sprite(sprite_filename)
	elif file_extension.lower() == ".png":
		#I'm not sure what to do here yet in a completely scalable way, since PNG files have no applicable metadata
		loaded_image = Image.open(sprite_filename) 
		if loaded_image.size == (128,448):      #This is the size of Z3Link's sheet
			game = get_game_class_of_type("zelda3")
			sprite = game.make_player_sprite(sprite_filename)
		elif loaded_image.size == (876,2543):   #This is the size of M3Samus's sheet
			game = get_game_class_of_type("metroid3")
			sprite = game.make_player_sprite(sprite_filename)
		else:
			raise AssertionError(f"Cannot recognize the type of file {sprite_filename} from its size: {loaded_image.size}")
	elif file_extension.lower() == ".zspr":
		with open(sprite_filename,"rb") as file:
			zspr_data = bytearray(file.read())
		game = get_game_class_of_type(get_game_type_from_zspr_data(zspr_data))
		sprite = game.make_sprite_by_number(get_sprite_number_from_zspr_data(zspr_data),sprite_filename)
	else:
		raise AssertionError(f"Cannot recognize the type of file {sprite_filename} from its filename")
	return game, sprite

def autodetect_game_type_from_rom_filename(filename):
	return autodetect_game_type_from_rom(romhandler.RomHandlerParent(filename))

def autodetect_game_type_from_rom(rom):
	rom_name = rom.get_name()
	with open(common.get_resource("game_header_info.json",subdir="meta")) as file:
		game_header_info = json.load(file)
	for game_name, header_name_list in game_header_info.items():
		for header_name in header_name_list:
			if rom_name[:len(header_name)] == header_name:
				return game_name
	else:
		raise AssertionError(f"Could not identify the type of ROM {filename} from its header name: {rom_name}")

def get_game_type_from_zspr_data(zspr_data):
	#for now, until other types of ZSPR files exist, we will just assume that all ZSPR files are Zelda3 Link files
	return "zelda3"

def get_sprite_number_from_zspr_data(zspr_data):
	return int.from_bytes(zspr_data[21:23], byteorder='little')

def get_game_class_of_type(game_name):
	#dynamic import
	game_module = importlib.import_module(f"source.{game_name}.game")
	return game_module.Game()

class GameParent():
	#parent class for games to inherit
	
	#to make a new game class, you must write code for all of the functions in this section below.
	############################# BEGIN ABSTRACT CODE ##############################

	def __init__(self):
		self.name = "Game Parent Class"    #to be replaced by a name like "Super Metroid"
		self.internal_name = "meta"        #to be replaced by the specific folder name that this app uses, e.g. "metroid3"

	############################# END ABSTRACT CODE ##############################

	#the functions below here are special to the parent class and do not need to be overwritten, unless you see a reason

	def attach_background_panel(self, parent, canvas, zoom_getter, frame_getter):
		#for now, accepting frame_getter as an argument because maybe the child class has animated backgrounds or something
		BACKGROUND_DROPDOWN_WIDTH = 25
		PANEL_HEIGHT = 25
		self.canvas = canvas
		self.zoom_getter = zoom_getter
		self.frame_getter = frame_getter
		self.current_background_filename = None
		self.last_known_zoom = None

		background_panel = tk.Frame(parent, name="background_panel")
		widgetlib.right_align_grid_in_frame(background_panel)
		background_label = tk.Label(background_panel, text="Background:")
		background_label.grid(row=0, column=1)
		self.background_selection = tk.StringVar(background_panel)

		background_filenames = common.gather_all_from_resource_subdirectory(os.path.join(self.internal_name,"backgrounds"))
		self.background_selection.set(random.choice(background_filenames))
		
		background_dropdown = tk.ttk.Combobox(background_panel, state="readonly", values=background_filenames, name="background_dropdown")
		background_dropdown.configure(width=BACKGROUND_DROPDOWN_WIDTH, exportselection=0, textvariable=self.background_selection)
		background_dropdown.grid(row=0, column=2)

		def dropdown_wrapper(this_object):
			def change_background_dropdown(*args):
				this_object().set_background(this_object().background_selection.get())
			return change_background_dropdown
		self.background_selection.trace('w', dropdown_wrapper(weakref.ref(self)))  #when the dropdown is changed, run this function
		dropdown_wrapper(weakref.ref(self))()      #trigger this now to load the first background

		parent.add(background_panel,minsize=PANEL_HEIGHT)
		return background_panel

	def set_background(self, image_filename):
		if self.current_background_filename == image_filename:
			if self.last_known_zoom == self.zoom_getter():
				return   #there is nothing to do here, because nothing has changed
		else:     #image name is different, so need to load a new image
			self.raw_background = Image.open(common.get_resource(image_filename,subdir=os.path.join(self.internal_name,"backgrounds")))
		
		#now re-zoom the image
		new_size = tuple(int(dim*self.zoom_getter()) for dim in self.raw_background.size)
		self.background_image = common.get_tk_image(self.raw_background.resize(new_size,resample=Image.NEAREST))
		if self.current_background_filename is None:
			self.background_ID = self.canvas.create_image(0, 0, image=self.background_image, anchor=tk.NW)    #so that we can manipulate the object later
		else:
			self.canvas.itemconfig(self.background_ID, image=self.background_image)
		self.last_known_zoom = self.zoom_getter()
		self.current_background_filename = image_filename

	def update_background_image(self):
		self.set_background(self.current_background_filename)

	def make_player_sprite(self, sprite_filename):
		return self.make_sprite_by_number(0x01, sprite_filename)

	def make_sprite_by_number(self, sprite_number, sprite_filename):
		#go into the manifest and get the actual name of the sprite
		with open(common.get_resource("manifest.json",self.internal_name)) as file:
			manifest = json.load(file)
		if str(sprite_number) in manifest:
			folder_name = manifest[str(sprite_number)]["folder name"]
			#dynamic import
			sprite_module = importlib.import_module(f"source.{self.internal_name}.{folder_name}.sprite")
			return sprite_module.Sprite(sprite_filename,manifest[str(sprite_number)],os.path.join(self.internal_name,folder_name))
		else:
			raise AssertionError(f"make_sprite_by_number() called for non-implemented sprite_number {sprite_number}")

	def get_rom_from_filename(self, filename):
		#dynamic import
		rom_module = importlib.import_module(f"source.{self.internal_name}.rom")
		return rom_module.RomHandler(filename)
