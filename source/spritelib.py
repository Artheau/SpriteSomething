#common functions for all entities (i.e. "Sprites")
#sprites are responsible for maintaining their widgets
#they have to contain PIL images of all of their data, and the offset info, and how to assemble it
#and they have to interpret the global frame timer, and communicate back when to next check in

import tkinter as tk
import random
import os
from PIL import Image, ImageTk
from source import widgetlib
from source import layout
from source import common

#TODO: this file needs to contain all the metadata for the sprites

class SpriteParent():
	#parent class for sprites to inherit
	def __init__(self, filename, manifest_dict, my_subpath):
		self.classic_name = manifest_dict["name"]    #e.g. "Samus" or "Link"
		self.resource_subpath = my_subpath           #the path to this sprite's subfolder in resources
		self.filename = filename
		self.layout = layout.Layout(common.get_resource("layout.json",subdir=self.resource_subpath))
		self.import_from_filename()

	#to make a new sprite class, you must write code for all of the functions in this section below.
	############################# BEGIN ABSTRACT CODE ##############################

	def import_from_ZSPR():
		raise AssertionError("called import_from_ZSPR() on Sprite base class")

	def import_from_ROM():
		raise AssertionError("called import_from_ROM() on Sprite base class")
	
	def get_all_animation_names(self):
		return ["stand","don't stand"]   #TODO

	def get_tiles_for_current_pose(self):  #TODO
		return [(Image.new("RGB",(100,100),0x70),(0,0)),(Image.new("RGB",(100,100),0x30),(50,50))]

	############################# END ABSTRACT CODE ##############################

	#the functions below here are special to the parent class and do not need to be overwritten, unless you see a reason

	def import_from_filename(self):
		_,file_extension = os.path.splitext(self.filename)
		if file_extension.lower() == '.png':
			self.import_from_PNG()
		elif file_extension.lower() == '.zspr':
			self.import_from_ZSPR()
		elif file_extension.lower() in ['.sfc','.smc']:
			self.import_from_ROM()

	def import_from_PNG(self):
		self.images, self.master_palette = self.layout.extract_all_images_from_master(Image.open(self.filename))

	def attach_metadata_panel(self,parent):
		parent.add(tk.Label(parent, text="Sprite Metadata\nGoes\nHere"))

	def attach_animation_panel(self, parent, canvas, zoom_getter, frame_getter, coord_getter):
		#for now, accepting frame_getter as an argument because maybe the child class has animated backgrounds or something
		ANIMATION_DROPDOWN_WIDTH = 25
		PANEL_HEIGHT = 25
		self.canvas = canvas
		self.zoom_getter = zoom_getter
		self.frame_getter = frame_getter
		self.coord_getter = coord_getter
		self.last_known_zoom = None
		self.last_known_frame = None
		self.last_known_coord = None
		self.current_animation = None
		self.time_left_in_this_pose = 0
		self.time_left_in_this_palette = 0

		animation_panel = tk.Frame(parent, name="animation_panel")
		widgetlib.right_align_grid_in_frame(animation_panel)
		animation_label = tk.Label(animation_panel, text="Animation:")
		animation_label.grid(row=0, column=1)
		self.animation_selection = tk.StringVar(animation_panel)

		animation_names = self.get_all_animation_names()
		self.animation_selection.set(random.choice(animation_names))
		
		animation_dropdown = tk.ttk.Combobox(animation_panel, state="readonly", values=animation_names, name="animation_dropdown")
		animation_dropdown.configure(width=ANIMATION_DROPDOWN_WIDTH, exportselection=0, textvariable=self.animation_selection)
		animation_dropdown.grid(row=0, column=2)
		def change_animation_dropdown(*args):
			self.set_animation(self.animation_selection.get())
		self.animation_selection.trace('w', change_animation_dropdown)  #when the dropdown is changed, run this function
		change_animation_dropdown()      #trigger this now to load the first animation
		parent.add(animation_panel,minsize=PANEL_HEIGHT)
		return animation_panel

	def reload(self):
		#activated when the reload button is pressed.  Should reload the sprite from the file but not manipulate the buttons
		self.import_from_filename()
		self.last_known_frame = None
		self.update_animation()

	def set_animation(self, animation_name):
		#see if anything needs to be done first
		if self.current_animation == animation_name and self.last_known_zoom == self.zoom_getter():
			if self.last_known_frame is not None and \
						self.frame_getter()-self.last_known_frame <= min(self.time_left_in_this_pose,self.time_left_in_this_palette):   #or it doesn't matter
				#update the coordinates
				delta = tuple(new-prev for new,prev in zip(self.coord_getter(),self.last_known_coord))
				if delta != (0,0):
					for ID in self.sprite_IDs:
						self.canvas.move(ID, *delta)
				frame_delta = self.frame_getter()-self.last_known_frame
				self.time_left_in_this_pose -= frame_delta
				self.time_left_in_this_palette -= frame_delta
				self.last_known_coord = self.coord_getter()
				#we're done here
				return
		
		#at this point, something needs to be done
		if hasattr(self,"sprite_IDs"):
			for ID in self.sprite_IDs:
				self.canvas.delete(ID)       #remove the old tiles
		self.sprite_IDs = []
		self.active_tiles = []
		#TODO: get the right palettes
		for tile,origin in self.get_tiles_for_current_pose():
			new_size = tuple(int(dim*self.zoom_getter()) for dim in tile.size)
			scaled_tile = ImageTk.PhotoImage(tile.resize(new_size,resample=Image.BICUBIC))
			coord_on_canvas = tuple(int(self.zoom_getter()*(pos-x)) for pos,x in zip(self.coord_getter(),origin))
			self.sprite_IDs.append(self.canvas.create_image(*coord_on_canvas, image=scaled_tile, anchor = tk.NW))
			self.active_tiles.append(scaled_tile)     #if you skip this part, then the auto-destructor will get rid of your picture!
			
	def update_animation(self):
		self.set_animation(self.current_animation)			

	def frames_left_in_this_animation():
		return self.time_left_in_this_pose
				