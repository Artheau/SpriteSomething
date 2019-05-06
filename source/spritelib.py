#common functions for all entities (i.e. "Sprites")
#sprites are responsible for maintaining their widgets
#they have to contain PIL images of all of their data, and the offset info, and how to assemble it
#and they have to interpret the global frame timer, and communicate back when to next check in

import tkinter as tk
import random
import os
import json
import itertools
import importlib
import weakref
from PIL import Image, ImageTk
from source import widgetlib
from source import layoutlib
from source import common

#TODO: this file needs to contain all the metadata for the sprites

class SpriteParent():
	#parent class for sprites to inherit
	def __init__(self, filename, manifest_dict, my_subpath):
		self.classic_name = manifest_dict["name"]    #e.g. "Samus" or "Link"
		self.resource_subpath = my_subpath           #the path to this sprite's subfolder in resources
		self.filename = filename
		self.layout = layoutlib.Layout(common.get_resource("layout.json",subdir=self.resource_subpath))
		with open(common.get_resource("animations.json",subdir=self.resource_subpath)) as file:
			self.animations = json.load(file)
		self.import_from_filename()

		self.overview_scale_factor = 2               #when the overview is made, it is scaled up by this amount

	#to make a new sprite class, you must write code for all of the functions in this section below.
	############################# BEGIN ABSTRACT CODE ##############################

	def import_from_ZSPR(self):
		#use self.filename as the filename
		#self.images, self.master_palette = ?, ?
		raise AssertionError("called import_from_ZSPR() on Sprite base class")

	def import_from_ROM(self, rom):
		#self.images, self.master_palette = ?, ?
		raise AssertionError("called import_from_ROM() on Sprite base class")

	def save_as_ZSPR(self, filename):
		#return True if the save was a success
		raise AssertionError("called save_as_ZSPR() on Sprite base class")

	def inject_into_ROM(self, rom):
		#return True if the export was a success
		raise AssertionError("called export_to_ROM() on Sprite base class")

	def get_timed_palette(self, overall_type="base", variant_type="standard"):
		#return the requested palette
		#with no arguments, this returns the base type (e.g. green mail/power suit)
		#you can specify overall_type to be other suits (e.g. blue mail/varia suit)
		# and variant_type refers to changes on that palette, usually flashy things (e.g. zap/shinespark)
		#or you can also specify overall_type to be other palettes related to the character (e.g. gold sword)
		# in which case variant_type refers to variants of that type (e.g. tempered vs. gold)
		#IMPORTANT: This function returns a list of tuples, not just the palette
		# and so the output format should be [(num_frames, [rgb_color ...]) ...]
		# where num_frames is the number of frames to hold these colors (0 means to hold permanently)
		# thus for static palettes (i.e. most palettes), this will be of the form [(0, [(r,g,b) ...])]
		#Do not include the transparency color
		raise AssertionError("called get_timed_palette() on Sprite base class")

	############################# END ABSTRACT CODE ##############################

	#the functions below here are special to the parent class and do not need to be overwritten, unless you see a reason

	def import_from_filename(self):
		_,file_extension = os.path.splitext(self.filename)
		if file_extension.lower() == '.png':
			self.import_from_PNG()
		elif file_extension.lower() == '.zspr':
			self.import_from_ZSPR()
		elif file_extension.lower() in ['.sfc','.smc']:
			#dynamic import
			rom_path,_ = os.path.split(self.resource_subpath)
			_,rom_dir = os.path.split(rom_path)
			rom_module = importlib.import_module(f"source.{rom_dir}.rom")
			self.import_from_ROM(rom_module.RomHandler(self.filename))

	def import_from_PNG(self):
		self.images, self.master_palette = self.layout.extract_all_images_from_master(Image.open(self.filename))

	def attach_metadata_panel(self,parent):
		parent.add(tk.Label(parent, text="Sprite Metadata\nGoes\nHere"))

	def attach_animation_panel(self, parent, canvas, overview_canvas, zoom_getter, frame_getter, coord_getter):
		ANIMATION_DROPDOWN_WIDTH = 25
		PANEL_HEIGHT = 25
		self.canvas = canvas
		self.overview_canvas = overview_canvas
		self.zoom_getter = zoom_getter
		self.frame_getter = frame_getter
		self.coord_getter = coord_getter
		self.last_known_zoom = None
		self.last_known_coord = None
		self.current_animation = None
		self.pose_number = None
		self.palette_number = None

		animation_panel = tk.Frame(parent, name="animation_panel")
		widgetlib.right_align_grid_in_frame(animation_panel)
		animation_label = tk.Label(animation_panel, text="Animation:")
		animation_label.grid(row=0, column=1)
		self.animation_selection = tk.StringVar(animation_panel)

		self.animation_selection.set(random.choice(list(self.animations.keys())))
		
		animation_dropdown = tk.ttk.Combobox(animation_panel, state="readonly", values=list(self.animations.keys()), name="animation_dropdown")
		animation_dropdown.configure(width=ANIMATION_DROPDOWN_WIDTH, exportselection=0, textvariable=self.animation_selection)
		animation_dropdown.grid(row=0, column=2)
		self.set_animation(self.animation_selection.get())
		
		def dropdown_wrapper(this_object):
			def change_animation_dropdown(*args):
				#This tomfoolery is necessary to avoid a memory leak
				this_object().set_animation(this_object().animation_selection.get())
			return change_animation_dropdown
		self.animation_selection.trace('w', dropdown_wrapper(weakref.ref(self)))  #when the dropdown is changed, run this function
		dropdown_wrapper(weakref.ref(self))()      #trigger this now to load the first animation

		parent.add(animation_panel,minsize=PANEL_HEIGHT)

		self.update_overview_panel()

		return animation_panel

	def reload(self):
		#activated when the reload button is pressed.  Should reload the sprite from the file but not manipulate the buttons
		self.import_from_filename()
		self.update_overview_panel()
		self.last_known_zoom = None    #this will force a reload from update_animation()
		self.last_known_coord = None
		self.update_animation()

	def set_animation(self, animation_name):
		self.current_animation = animation_name
		self.last_known_zoom = None
		self.last_known_coord = None
		self.update_animation()

	def update_pose_and_palette_numbers(self):
		#also returns true if the pose or the palette was updated

		if not hasattr(self, "frame_progression_table"):    #the table hasn't been set up, so signal for a change
			return True
		
		old_pose_number, old_palette_number = self.pose_number, self.palette_number

		mod_frames = self.frame_getter() % self.frame_progression_table[-1]
		self.pose_number = self.frame_progression_table.index(min([x for x in self.frame_progression_table if x > mod_frames]))

		palette_mod_frames = self.frame_getter() % self.palette_progression_table[-1]
		self.palette_number = self.palette_progression_table.index(min([x for x in self.palette_progression_table if x > palette_mod_frames]))
		
		return (old_pose_number != self.pose_number) or (old_palette_number != self.palette_number)
		
	def get_tiles_for_current_pose(self):
		self.update_pose_and_palette_numbers()
		pose_list = self.get_current_pose_list()
		full_tile_list = []
		for tile_info in pose_list[self.pose_number]["tiles"][::-1]:
			base_image = self.images[tile_info["image"]]
			if "crop" in tile_info:
				base_image = base_image.crop(tuple(tile_info["crop"]))
			if "flip" in tile_info:
				hflip = "h" in tile_info["flip"].lower()
				vflip = "v" in tile_info["flip"].lower()
				if hflip and vflip:
					base_image = base_image.transpose(Image.ROTATE_180)
				elif hflip:
					base_image = base_image.transpose(Image.FLIP_LEFT_RIGHT)
				elif vflip:
					base_image = base_image.transpose(Image.FLIP_TOP_BOTTOM)

			palette_lookup = self.layout.get_property("import palette interval", tile_info["image"])        #TODO: get correct palette based upon buttons

			base_image = common.apply_palette(base_image, self.master_palette[palette_lookup[0]:palette_lookup[1]])
			
			full_tile_list.append((base_image,tile_info["pos"]))
		
		return full_tile_list

	def get_current_pose_list(self):
		return next(iter(self.animations[self.current_animation].values()))   #TODO: base upon direction widgets

	def frames_in_this_animation(self):
		return self.frame_progression_table[-1]

	def frames_left_in_this_pose(self):
		mod_frames = self.frame_getter() % self.frame_progression_table[-1]
		next_pose_at = min(x for x in self.frame_progression_table if x > mod_frames)
		return next_pose_at - mod_frames
		
	def frames_to_previous_pose(self):
		mod_frames = self.frame_getter() % self.frame_progression_table[-1]
		prev_pose_at = max((x for x in self.frame_progression_table if x <= mod_frames), default=0)
		return mod_frames - prev_pose_at + 1

	def update_animation(self):
		#see if there's anything to do
		if not self.update_pose_and_palette_numbers():   #the pose and palette numbers didn't change
			if self.last_known_zoom == self.zoom_getter():
				if self.last_known_coord == self.coord_getter():
					return #there's nothing you can do here. go home, you're drunk

		#ok, there's something to do here, so sober up
		pose_list = self.get_current_pose_list()
		if "frames" not in pose_list[0]:      #might not be a frame entry for static poses
			self.frame_progression_table = [1]
		else:
			self.frame_progression_table = list(itertools.accumulate([pose["frames"] for pose in pose_list]))

		self.palette_progression_table = [1]   #TODO

		if hasattr(self,"sprite_IDs"):
			for ID in self.sprite_IDs:
				self.canvas.delete(ID)       #remove the old tiles
		if hasattr(self,"active_tiles"):
			for tile in self.active_tiles:
				del tile                     #why this is not auto-destroyed is beyond me (memory leak otherwise)
		self.sprite_IDs = []
		self.active_tiles = []
		
		for tile,offset in self.get_tiles_for_current_pose():
			new_size = tuple(int(dim*self.zoom_getter()) for dim in tile.size)
			scaled_tile = ImageTk.PhotoImage(tile.resize(new_size,resample=Image.NEAREST))
			coord_on_canvas = tuple(int(self.zoom_getter()*(pos+x)) for pos,x in zip(self.coord_getter(),offset))
			self.sprite_IDs.append(self.canvas.create_image(*coord_on_canvas, image=scaled_tile, anchor = tk.NW))
			self.active_tiles.append(scaled_tile)     #if you skip this part, then the auto-destructor will get rid of your picture!
		self.last_known_coord = self.coord_getter()
		self.last_known_zoom = self.zoom_getter()	

	def save_as(self, filename):
		_,file_extension = os.path.splitext(filename)
		if file_extension.lower() == ".png":
			return self.save_as_PNG(filename)
		elif file_extension.lower() == ".zspr":
			return self.save_as_ZSPR(filename)
		else:
			messagebox.showerror("ERROR", f"Did not recognize file type \"{file_extension}\"")
			return False

	def save_as_PNG(self, filename):
		master_image = self.get_master_PNG_image()
		master_image.save(filename)
		return True

	def get_master_PNG_image(self):
		return self.layout.export_all_images_to_PNG(self.images,self.master_palette)

	def update_overview_panel(self):
		image = self.get_master_PNG_image()
		scaled_image = image.resize(tuple(int(x*self.overview_scale_factor) for x in image.size))

		if hasattr(self,"overview_ID") and self.overview_ID is not None:
			del self.overview_image
			self.overview_image = common.get_tk_image(scaled_image)
			self.overview_canvas.itemconfig(self.overview_ID, image=self.overview_image)
		else:
			import time
			scaled_image = scaled_image.copy()
			self.overview_image = common.get_tk_image(scaled_image)
			self.overview_ID = self.overview_canvas.create_image(0, 0, image=self.overview_image, anchor=tk.NW)
	
