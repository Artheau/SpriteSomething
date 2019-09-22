#common functions to all games
#handling backgrounds, etc.
#handles import of new sprites

import os							#for filesystem manipulation
import importlib			#for importing libraries dynamically
import json						#for reading JSON
import tkinter as tk	#for GUI stuff
import random					#for choosing background image to load on app startup
from PIL import Image, ImageFile
from functools import partial
from source import widgetlib
from source import romhandler
from source import common
from source import gui_common #TODO: Should not use GUI stuff in game class, need to move this elsewhere

def autodetect(sprite_filename):
	#need to autodetect which game, and which sprite
	#then return an instance of THAT game's class, and an instance of THAT sprite
	_,file_extension = os.path.splitext(sprite_filename)
	if file_extension.lower() in [".sfc",".smc"]:
		#If the file is a rom, then we can go into the internal header and get the name of the game
		game_names = autodetect_game_type_from_rom_filename(sprite_filename)
		selected_game = None

		#prompt user for input
		#FIXME: Ugh, more tk
		selected_game = gui_common.create_chooser(game_names)

		if not selected_game:
			selected_game = random.choice(game_names)

		game = get_game_class_of_type(selected_game)
		#And by default, we will grab the player sprite from this game
		sprite, animation_assist = game.make_player_sprite(sprite_filename)
	elif file_extension.lower() == ".png":
		#the following line prevents a "cannot identify image" error from PIL
		ImageFile.LOAD_TRUNCATED_IMAGES = True
		#I'm not sure what to do here yet in a completely scalable way, since PNG files have no applicable metadata
		loaded_image = Image.open(sprite_filename)
		game_found = False
		search_path = "app_resources"
		for item in os.listdir(search_path):
			if os.path.isdir(os.path.join(search_path,item)) and not item == "meta":
				game_name = item
				sprite_manifest_filename = os.path.join(search_path,game_name,"manifests","manifest.json")
				with open(sprite_manifest_filename) as f:
					sprite_manifest = json.load(f)
					f.close()
					for sprite_id in sprite_manifest:
						if "input" in sprite_manifest[sprite_id] and "png" in sprite_manifest[sprite_id]["input"] and "dims" in sprite_manifest[sprite_id]["input"]["png"]:
							check_size = sprite_manifest[sprite_id]["input"]["png"]["dims"]
							if loaded_image.size == tuple(check_size):
								game = get_game_class_of_type(game_name)
								sprite, animation_assist = game.make_player_sprite(sprite_filename)
								game_found = True
		if not game_found:
			#FIXME: English
			raise AssertionError(f"Cannot recognize the type of file {sprite_filename} from its size: {loaded_image.size}")
	elif file_extension.lower() == ".zspr":
		with open(sprite_filename,"rb") as file:
			zspr_data = bytearray(file.read())
			file.close()
		game = get_game_class_of_type(get_game_type_from_zspr_data(zspr_data))
		sprite, animation_assist = game.make_sprite_by_number(get_sprite_number_from_zspr_data(zspr_data),sprite_filename)
	else:
		#FIXME: English
		raise AssertionError(f"Cannot recognize the type of file {sprite_filename} from its filename")

	return game, sprite, animation_assist

def autodetect_game_type_from_rom_filename(filename):
	return autodetect_game_type_from_rom(romhandler.RomHandlerParent(filename))

def autodetect_game_type_from_rom(rom):
	rom_name = rom.get_name()
	with open(common.get_resource(["meta","manifests"],"game_header_info.json")) as file:
		game_header_info = json.load(file)
		file.close()

	game_names = []
	for game_name, header_name_list in game_header_info.items():
		for header_name in header_name_list:
			if rom_name[:len(header_name)] == header_name:
				game_names.append(game_name)

	if len(game_names) == 0:
		game_names = None
		#raise AssertionError(f"Could not identify the type of ROM from its header name: {rom_name}")
		#FIXME: English
		print(f"Could not identify the type of ROM from its header name: {rom_name}")

	return game_names

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
		self.plugins = None
		self.has_plugins = None
		self.console = "snes" #to be replaced by the console that the game is native to, assuming SNES for now

	############################# END ABSTRACT CODE ##############################

	#the functions below here are special to the parent class and do not need to be overwritten, unless you see a reason

	def load_plugins(self):
		try:
			plugins_module = importlib.import_module(f"source.{self.internal_name}.plugins")
			self.plugins = plugins_module.Plugins()
			self.has_plugins = True
		except ModuleNotFoundError as err:
			pass #not terribly interested right now

	def attach_background_panel(self, parent, canvas, zoom_getter, frame_getter, fish):
		#for now, accepting frame_getter as an argument because maybe the child class has animated backgrounds or something
		BACKGROUND_DROPDOWN_WIDTH = 25
		PANEL_HEIGHT = 25
		self.canvas = canvas
		self.zoom_getter = zoom_getter
		self.frame_getter = frame_getter
		self.background_datas = {"filename":{},"title":{}}
		self.current_background_title = None
		self.last_known_zoom = None

		background_panel = tk.Frame(parent, name="background_panel")
		widgetlib.right_align_grid_in_frame(background_panel)
		background_label = tk.Label(background_panel, text=fish.translate("meta","meta","background") + ':')
		background_label.grid(row=0, column=1)
		self.background_selection = tk.StringVar(background_panel)

		background_manifests = common.get_all_resources([self.internal_name,"backgrounds"],"backgrounds.json")
		for background_manifest in background_manifests:
			with open(background_manifest) as f:
				background_data = json.load(f)
				f.close()
				for background in background_data["backgrounds"]:
					self.background_datas["filename"][background["filename"]] = background["title"]
					self.background_datas["title"][background["title"]] = background["filename"]
		background_prettynames = list(self.background_datas["title"].keys())
		self.background_selection.set(random.choice(background_prettynames))

		background_dropdown = tk.ttk.Combobox(background_panel, state="readonly", values=background_prettynames, name="background_dropdown")
		background_dropdown.configure(width=BACKGROUND_DROPDOWN_WIDTH, exportselection=0, textvariable=self.background_selection)
		background_dropdown.grid(row=0, column=2)

		widgetlib.leakless_dropdown_trace(self, "background_selection", "set_background")

		parent.add(background_panel,minsize=PANEL_HEIGHT)
		return background_panel

	def set_background(self, image_title):
		if self.current_background_title == image_title:
			if self.last_known_zoom == self.zoom_getter():
				return   #there is nothing to do here, because nothing has changed
		else:     #image name is different, so need to load a new image
			image_filename = self.background_datas["title"][image_title]
			self.raw_background = Image.open(common.get_resource([self.internal_name,"backgrounds"],image_filename))

		#now re-zoom the image
		new_size = tuple(int(dim*self.zoom_getter()) for dim in self.raw_background.size)
		self.background_image = gui_common.get_tk_image(self.raw_background.resize(new_size,resample=Image.NEAREST))
		if self.current_background_title is None:
			self.background_ID = self.canvas.create_image(0, 0, image=self.background_image, anchor=tk.NW)    #so that we can manipulate the object later
		else:
			self.canvas.itemconfig(self.background_ID, image=self.background_image)
		self.last_known_zoom = self.zoom_getter()
		self.current_background_title = image_title

	def update_background_image(self):
		self.set_background(self.current_background_title)

	def make_player_sprite(self, sprite_filename):
		return self.make_sprite_by_number(0x01, sprite_filename)

	def make_sprite_by_number(self, sprite_number, sprite_filename):
		#go into the manifest and get the actual name of the sprite
		with open(common.get_resource([self.internal_name,"manifests"],"manifest.json")) as file:
			manifest = json.load(file)
			file.close()
		if str(sprite_number) in manifest:
			folder_name = manifest[str(sprite_number)]["folder name"]
			#dynamic imports to follow
			source_subpath = f"source.{self.internal_name}.{folder_name}"
			sprite_module = importlib.import_module(f"{source_subpath}.sprite")
			resource_subpath = os.path.join(self.internal_name,folder_name)
			sprite = sprite_module.Sprite(sprite_filename,manifest[str(sprite_number)],resource_subpath)

			try:
				animationlib = importlib.import_module(f"{source_subpath}.animation")
				animation_assist = animationlib.AnimationEngine(resource_subpath, sprite)
			except ImportError:    #there was no sprite-specific animation library, so import the parent
				animationlib = importlib.import_module(f"source.animationlib")
				animation_assist = animationlib.AnimationEngineParent(resource_subpath, sprite)

			return sprite, animation_assist
		else:
			#FIXME: English
			raise AssertionError(f"make_sprite_by_number() called for non-implemented sprite_number {sprite_number}")

	def get_rom_from_filename(self, filename):
		#dynamic import
		rom_module = importlib.import_module(f"source.{self.internal_name}.rom")
		return rom_module.RomHandler(filename)
