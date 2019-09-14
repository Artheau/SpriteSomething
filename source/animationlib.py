#this class acts as a go-between between the GUI and the sprite class
#in particular, keeps track of information like which palette the sprite is using, etc.

import tkinter as tk
import random
import json
import itertools
from PIL import Image, ImageTk
from source import common, gui_common, widgetlib

class AnimationEngineParent():
	def __init__(self, my_subpath, sprite):
		self.sprite = sprite
		self.resource_subpath = my_subpath           #the path to this sprite's subfolder in resources
		self.spiffy_dict = {}						 #the variables created by the spiffy buttons will go here
		self.overhead = True                         #by default, this will create NESW direction buttons.  If false, only left/right buttons
		self.overview_scale_factor = sprite.overview_scale_factor #when the overview is made, it is scaled up by this amount
		self.step_number_label = tk.Label()
		self.step_total_label = tk.Label()
		self.tiles_list_label = tk.Label()

		self.plugins = []
		self.prev_palette_info = []

		with open(common.get_resource([self.resource_subpath,"manifests"],"animations.json")) as file:
			self.animations = json.load(file)
			file.close()
		if "$schema" in self.animations:
			del self.animations["$schema"]

		self.current_animation = next(iter(self.animations.keys()))   #using a default value until the animation_panel attachment overrides this

	def attach_animation_panel(self, parent, canvas, overview_canvas, zoom_getter, frame_getter, coord_getter, fish):
		ANIMATION_DROPDOWN_WIDTH = 25
		PANEL_HEIGHT = 25
		self.canvas = canvas
		self.overview_canvas = overview_canvas
		self.zoom_getter = zoom_getter
		self.frame_getter = frame_getter
		self.coord_getter = coord_getter
		self.current_animation = None
		self.pose_number = None
		self.palette_number = None

		animation_panel = tk.Frame(parent, name="animation_panel")
		widgetlib.right_align_grid_in_frame(animation_panel)
		animation_label = tk.Label(animation_panel, text=fish.translate("meta","meta","animations") + ':')
		animation_label.grid(row=0, column=1)
		self.animation_selection = tk.StringVar(animation_panel)

		self.animation_selection.set(random.choice(list(self.animations.keys())))

		animation_dropdown = tk.ttk.Combobox(animation_panel, state="readonly", values=list(self.animations.keys()), name="animation_dropdown")
		animation_dropdown.configure(width=ANIMATION_DROPDOWN_WIDTH, exportselection=0, textvariable=self.animation_selection)
		animation_dropdown.grid(row=0, column=2)
		self.set_animation(self.animation_selection.get())

		widgetlib.leakless_dropdown_trace(self, "animation_selection", "set_animation")

		parent.add(animation_panel,minsize=PANEL_HEIGHT)

		direction_panel, height, new_spiffy_dict = self.get_direction_buttons(parent,fish).get_panel()
		self.spiffy_dict = {**self.spiffy_dict, **new_spiffy_dict}   #merge all the stringvars into this dict


		parent.add(direction_panel, minsize=height)

		spiffy_panel, height, new_spiffy_dict = self.get_spiffy_buttons(parent,fish).get_panel()
		self.spiffy_dict = {**self.spiffy_dict, **new_spiffy_dict}   #merge all the stringvars into this dict

		parent.add(spiffy_panel,minsize=height)

		self.update_overview_panel()

		return animation_panel

	def attach_tile_details_panel(self, parent, fish):
		tile_details_panel = tk.Frame(parent, name="tile_details_panel")
		widgetlib.right_align_grid_in_frame(tile_details_panel)

		# Step: <step_number_label> / <step_total_label>
		# Tiles: <tile_list>
		LABEL_HEIGHT = 16
		step_panel = tk.Frame(parent, name="step_panel", height=LABEL_HEIGHT)
		widgetlib.right_align_grid_in_frame(step_panel)
		step_label = tk.Label(step_panel, text=fish.translate("meta","meta","step") + ':')
		step_label.grid(row=0, column=1)

		self.step_number_label = tk.Label(step_panel, text='0')
		self.step_number_label.grid(row=0, column=2)

		step_sep = tk.Label(step_panel, text='/')
		step_sep.grid(row=0, column=3)

		self.step_total_label = tk.Label(step_panel, text='0')
		self.step_total_label.grid(row=0, column=4)

		parent.add(step_panel)

		tiles_list_panel = tk.Frame(parent, name="tiles_list_panel")
		widgetlib.right_align_grid_in_frame(tiles_list_panel)
		self.tiles_list_label = tk.Label(tiles_list_panel, text='', justify=tk.RIGHT)
		self.tiles_list_label.grid(row=1, column=2)

		parent.add(tiles_list_panel)

		return tile_details_panel

	def set_animation(self, animation_name):
		self.current_animation = animation_name
		self.update_animation()

	def update_animation(self):
		if hasattr(self,"sprite_IDs"):
			for ID in self.sprite_IDs:
				self.canvas.delete(ID)       #remove the old images
		if hasattr(self,"active_images"):
			for tile in self.active_images:
				del tile                     #why this is not auto-destroyed is beyond me (memory leak otherwise)
		self.sprite_IDs = []
		self.active_images = []

		pose_image, offset = self.get_current_image()

		if pose_image:
			new_size = tuple(int(dim*self.zoom_getter()) for dim in pose_image.size)
			scaled_image = ImageTk.PhotoImage(pose_image.resize(new_size,resample=Image.NEAREST))
			coord_on_canvas = tuple(int(self.zoom_getter()*(pos+x)) for pos,x in zip(self.coord_getter(),offset))
			self.sprite_IDs.append(self.canvas.create_image(*coord_on_canvas, image=scaled_image, anchor = tk.NW))
			self.active_images.append(scaled_image)     #if you skip this part, then the auto-destructor will get rid of your picture!

	def get_current_image(self):
		displayed_direction = self.get_current_direction()
		pose_list = self.get_current_pose_list(displayed_direction)
		tile_list = []
		if not pose_list:
			displayed_direction = self.sprite.get_alternative_direction(self.current_animation, displayed_direction)
			pose_list = self.get_current_pose_list(displayed_direction)

		if pose_list:
			if "frames" not in pose_list[0]:      #might not be a frame entry for static poses
				self.frame_progression_table = [1]
			else:
				self.frame_progression_table = list(itertools.accumulate([pose["frames"] for pose in pose_list]))

			palette_info = ['_'.join([value.get(), var_name.replace("_var","")]) for var_name, value in self.spiffy_dict.items()]  #I'm not convinced that this is the best way to do this

			mod_frames = self.frame_getter() % self.frame_progression_table[-1]
			frame_number_pose_started_at = max((x for x in self.frame_progression_table if x <= mod_frames),default=None)
			if frame_number_pose_started_at is not None:
				self.pose_number = 1+self.frame_progression_table.index(frame_number_pose_started_at)
			else:
				self.pose_number = 0

			current_frame = self.frame_getter()
			
			if "palette_reference_frame" in pose_list[self.pose_number]:  #for animations that switch palettes in the middle
				self.palette_last_transition_frame = \
					current_frame - (
						(current_frame % self.frame_progression_table[-1])   #modular progress
						- self.frame_progression_table[self.pose_number-1]   #modular pose start
						+ pose_list[self.pose_number]["palette_reference_frame"]  #modular reference number
					)
			elif current_frame > 0:    #for when the user switches palettes by pushing buttons mid-animation
				if palette_info != self.prev_palette_info:
					self.palette_last_transition_frame = current_frame
			else:   #catch to make sure the user has not been abusing the backstep buttons to go backwards before a palette switch
				self.palette_last_transition_frame = 0
			self.prev_palette_info = palette_info.copy()
			current_frame -= self.palette_last_transition_frame

			pose_image,offset = self.sprite.get_image(self.current_animation, displayed_direction, self.pose_number, palette_info, current_frame)
			tile_list = self.sprite.get_tiles_for_pose(self.current_animation, displayed_direction, self.pose_number, palette_info, current_frame)
		else:
			pose_image,offset = None,(0,0)

		if self.pose_number is not None:
			self.step_number_label.config(text=str(self.pose_number+1))
		if pose_list:
			self.step_total_label.config(text=str(len(pose_list)))
			tile_list_text = ""
		if self.pose_number is not None and pose_list:
			pose = pose_list[self.pose_number]
			for tile in pose["tiles"]:
				tile_list_text += tile["image"]
				if "flip" in tile:
					flip_switcher = {
						"h": "X-flip",
						"v": "Y-flip",
						"both": "180-rotation",
						"hv": "180-rotation",
						"vh": "180-rotation"
					}
					flip = flip_switcher.get(tile["flip"]) if tile["flip"] in flip_switcher else ""
					tile_list_text += ' ' + flip
				tile_list_text += "\n"
			self.tiles_list_label.config(text=tile_list_text)

		return pose_image, offset


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

	def get_current_pose_list(self, direction):
		if self.spiffy_dict:     #see if we have any spiffy variables, which will indicate if the direction buttons exist
			return self.sprite.get_pose_list(self.current_animation, direction)
		#if there is no spiffy dict to determine directions, just don't do anything
		return []

	def get_current_direction(self):
		if self.spiffy_dict:
			direction = self.spiffy_dict["facing_var"].get().lower()   #grabbed from the direction buttons, which are named "facing"
			if "aiming_var" in self.spiffy_dict:
				direction = "_aim_".join([direction, self.spiffy_dict["aiming_var"].get().lower()])
			return direction
		else:
			return "right"   #TODO: figure out a better way to handle the error case

	#Mike likes spiffy buttons
	def get_spiffy_buttons(self, parent, fish):
		spiffy_buttons = widgetlib.SpiffyButtons(parent, self.resource_subpath, self)

		spiffy_manifest = common.get_resource([self.resource_subpath,"manifests"],"spiffy-buttons.json")
		if spiffy_manifest:
			with open(spiffy_manifest) as f:
				spiffy_list = json.load(f)
				f.close()

				for group in spiffy_list["button-groups"]:
					group_key = group["group-fish-key"]
					button_group = spiffy_buttons.make_new_group(group_key,fish)
					button_list = []
					for button in group["buttons"]:
						if "meta" in button and button["meta"] == "newline":
							button_list.append((None,None,None,None))
						elif "meta" in button and button["meta"] == "blank": #a blank space, baby
							button_list.append((None,"",None,None))
						else:
							default = button["default"] if "default" in button else False
							disabled = group["disabled"] if "disabled" in group else False
							button_list.append((button["fish-subkey"],button["img"],default,disabled))
					button_group.adds(button_list,fish)

		return spiffy_buttons

	#Art likes direction buttons
	def get_direction_buttons(self, parent, fish):
		#if this is not overriden by the child (sprite-specific) class, then it will default to WASD layout for overhead, or just left/right if sideview (not overhead).
		direction_buttons = widgetlib.SpiffyButtons(parent, self.resource_subpath, self, frame_name="direction_buttons", align="center")

		direction_manifest = common.get_resource([self.resource_subpath,"manifests"],"direction-buttons.json")
		if direction_manifest:
			with open(direction_manifest) as f:
				direction_list = json.load(f)
				f.close()

				for group in direction_list["button-groups"]:
					group_key = group["group-fish-key"]
					button_group = direction_buttons.make_new_group(group_key,fish)
					button_list = []
					for button in group["buttons"]:
						if "meta" in button and button["meta"] == "newline":
							button_list.append((None,None,None,None))
						elif "meta" in button and button["meta"] == "blank": #a blank space, baby
							button_list.append((None,"",None,None))
						else:
							default = button["default"] if "default" in button else False
							disabled = group["disabled"] if "disabled" in group else False
							button_list.append((button["fish-subkey"],button["img"],default,disabled))
					button_group.adds(button_list,fish)
		else:
			facing_group = direction_buttons.make_new_group("facing", fish)
			if self.overhead:
				facing_group.adds([
					(None,"",None,None), #a blank space, baby
					("up","arrow-up.png",False,False),
					(None,"",None,None), #a blank space, baby
					(None,None,None,None)
				],fish)
			facing_group.add("left", "arrow-left.png", fish)
			if self.overhead:
				facing_group.add("down", "arrow-down.png", fish)
			facing_group.add("right", "arrow-right.png", fish, default=True)

		return direction_buttons

	def update_overview_panel(self):
		image = self.sprite.get_master_PNG_image()
		scaled_image = image.resize(tuple(int(x*self.overview_scale_factor) for x in image.size))

		if hasattr(self,"overview_ID") and self.overview_ID is not None:
			del self.overview_image
			self.overview_image = gui_common.get_tk_image(scaled_image)
			self.overview_canvas.itemconfig(self.overview_ID, image=self.overview_image)
		else:
			import time
			scaled_image = scaled_image.copy()
			self.overview_image = gui_common.get_tk_image(scaled_image)
			self.overview_ID = self.overview_canvas.create_image(0, 0, image=self.overview_image, anchor=tk.NW)

	def export_frame_as_PNG(self, filename):
		#TODO: should this be factored out to the sprite class as some kind of export_as_PNG(animation, direction, ..., filename) call?
		current_image, _ = self.get_current_image()
		new_size = tuple(int(dim*self.zoom_getter()) for dim in current_image.size)
		img_to_save = current_image.resize(new_size,resample=Image.NEAREST)
		img_to_save.save(filename)

	def export_animation_as_collage(self, filename, orientation="horizontal"):
		#TODO: use the displayed palette
		image_list = []

		displayed_direction = self.get_current_direction()
		pose_list = self.get_current_pose_list(displayed_direction)
		if not pose_list:
			displayed_direction = self.sprite.get_alternative_direction(self.current_animation, displayed_direction)
			pose_list = self.get_current_pose_list(displayed_direction)

		for pose_number in range(len(pose_list)):
			image_list.append(self.sprite.get_image(self.current_animation, displayed_direction, pose_number, [], 0)) #TODO: incorporate palettes from spiffy buttons/animations.json, and meaningfully apply a palette number

		collage = None
		if orientation == "horizontal":
			#TODO: Factor this and the corresponding code in layoutlib.py out to common.py
			y_min = min([-origin[1] for image,origin in image_list])
			y_max = max([image.size[1]-origin[1] for image,origin in image_list])

			collage_width = sum([image.size[0] for image,_ in image_list])
			collage_y_size = y_max-y_min

			collage = Image.new("RGBA",(collage_width,collage_y_size),0)

			current_x_position = 0
			for image, origin in image_list:
				collage.paste(image, (current_x_position,-origin[1]-y_min))
				current_x_position += image.size[0]

		elif orientation == "vertical":
			# VERTICAL
			raise NotImplementedError()
		collage.save(filename)

	def export_animation_as_gif(self, filename):
		#TODO: This is not fully implemented -- need to get it to play nicely with timed poses and timed palettes
		#TODO: Fix timing
		#TODO: Use the displayed palette
		#TODO: factor out common code with the collage function
		GIF_MAX_FRAMERATE = 50.0  #GIF format cannot handle any faster than 50FPS
		ACTUAL_FRAMERATE = 60.0

		image_list = []

		displayed_direction = self.get_current_direction()
		pose_list = self.get_current_pose_list(displayed_direction)
		if not pose_list:
			displayed_direction = self.sprite.get_alternative_direction(self.current_animation, displayed_direction)
			pose_list = self.get_current_pose_list(displayed_direction)

		for pose_number in range(len(pose_list)):
			image_list.append(self.sprite.get_image(self.current_animation, displayed_direction, pose_number, [], 0))

		#TODO: Factor this and the corresponding code in layoutlib.py out to common.py
		x_min = min([origin[0] for image,origin in image_list])
		x_max = max([image.size[0]+origin[0] for image,origin in image_list])
		y_min = min([origin[1] for image,origin in image_list])
		y_max = max([image.size[1]+origin[1] for image,origin in image_list])

		gif_x_size = x_max-x_min
		gif_y_size = y_max-y_min

		frames = []
		for image, origin in image_list:
			this_frame = Image.new("RGB", (gif_x_size,gif_y_size))
			this_frame.paste(image, (origin[0]-x_min, origin[1]-y_min))
			frames.append(this_frame)

		durations = [
			1000.0 *   #millisecond conversion
			max(
				1.0/GIF_MAX_FRAMERATE,
				round(pose["frames"]/ACTUAL_FRAMERATE, 2)
			)
			for pose in pose_list
		]

		if frames:
			frames[0].save(filename, format='GIF', append_images=frames[1:],
				save_all=True, transparency=0, disposal=2, duration=durations, loop=0)
			return True
		else:
			return False
