import tkinter as tk	#for GUI stuff
from tkinter import ttk, messagebox, filedialog	#for GUI stuff
import random									#for choosing random app titles
import json										#for reading JSON
import re											#for regexes in hyperlinks in about box
import traceback							#for error reporting
import os, sys								#for filesystem manipulation
import time										#for timekeeping
import webbrowser							#for launching browser from about box
from functools import partial	#for passing parameters to user-triggered function calls
from PIL import Image,ImageTk    #for converting PNG to formats that tk can use
from source import widgetlib
from source import ssDiagnostics as diagnostics
from source import ssTranslate as fish
from source import gamelib
from source import constants as CONST
from source.ssTranslate import BabelFish
from source.tkHyperlinkManager import HyperlinkManager
from source.tkSimpleStatusBar import StatusBar
from source import common, gui_common


def make_GUI(command_line_args):
	root = tk.Tk()

	try:
		root.iconbitmap(default=common.get_resource('app.ico')) #Windows
	except Exception:
		try:
			root.tk.call('wm','iconphoto',root._w,tk.PhotoImage(file='@'+common.get_resource('app.gif'))) #Linux?
		except Exception:
			try:
				root.tk.call('wm','iconphoto',root._w,tk.PhotoImage(file=common.get_resource('app.gif'))) #MacOSX?
			except Exception:
				pass #give up
	root.geometry("800x600")       #window size
	root.configure(bg='#f0f0f0')   #background color
	main_frame = SpriteSomethingMainFrame(root, command_line_args)
	root.protocol("WM_DELETE_WINDOW", main_frame.exit)           #intercept when the user clicks the X

	def show_error(self, exception, message, callstack):
		if exception.__name__.upper() == "NOTIMPLEMENTEDERROR":
			messagebox.showerror(   "Not Yet Implemented",
									"This function is not yet implemented\n\n" + str(message)  )
		else:
			messagebox.showerror(   "FATAL ERROR",
									f"While running, encountered fatal error:\n\n" +
									f"{exception.__name__.upper()}\n" +
									f"{str(message)}\n"+
									f"{traceback.format_exc()}"
									)
	tk.Tk.report_callback_exception = show_error     #tie this in so we see errors when they happen

	root.mainloop()

class SpriteSomethingMainFrame(tk.Frame):
	def __init__(self, master, command_line_args):
		super().__init__(master)   #make the frame itself

		#set default working dirs to same dir as script
		self.working_dirs = {
			"file.open": "./",
			"file.save": "./",
			"export.dest": "./",
			"export.source": "./",
			"export.sprite-as-rdc": "./",
			"export.frame-as-png": "./",
			"export.animation-as-gif": "./",
			"export.animation-as-hcollage": "./",
			"export.animation-as-vcollage": "./"
		}
		#read saved working dirs file if it exists and set these
		working_dir_path = os.path.join("resources","meta","working_dirs.json")
		if os.path.exists(working_dir_path):
			with open(working_dir_path) as json_file:
				data = json.load(json_file)
				for k,v in data.items():
					self.working_dirs[k] = v

		#create a fish
		self.fish = BabelFish()

		self.create_random_title()

		#build and add toolbar
		self.create_toolbar()

		self.pack(fill=tk.BOTH, expand=1)    #main frame should take up the whole window

		self.create_menu_bar()

		self.panes = tk.PanedWindow(self, orient=tk.HORIZONTAL, name="two_columns")
		self.panes.pack(fill=tk.BOTH, expand=1)

		self.load_sprite(command_line_args["sprite"])

		self.unsaved_changes = False   #used to determine if we need to badger the user when they change things and try to exit

	def create_random_title(self):
		# Generate a new epic random title for this application
		name_dict = {}
		for filename in common.get_all_resources("app_names.json"):
			with open(filename) as name_file:
				for key,item in json.load(name_file).items():
					if key in name_dict:
						name_dict[key].extend(item)
					else:
						name_dict[key] = item
		app_name = []
		if random.choice([True,False]):
			app_name.append(random.choice(name_dict["pre"]))
		app_name.append("Sprite")         #Need to have "Sprite" in the name
		app_name.append(random.choice(name_dict["noun"]))
		if random.choice([True,False]):
			app_name.append(random.choice(name_dict["post"]))
		self.app_title = " ".join(app_name)
		self.master.title(self.app_title)

	#create a toolbar
	def create_toolbar(self):
		toolbar = tk.Frame(self.master, bd=1, relief=tk.RAISED)
		#create a toolbar button
		# Inbound:
		#  fish_key: Main key for translation
		#  fish_subkey: Subkey for translation
		#  image_filename: Image to use, default to blank
		#  command: Command to associate with button, default to None
		def create_toolbar_button(fish_key, fish_subkey, image_filename=None, command=None):
			icon_path = common.get_resource(["meta","icons"],image_filename if not image_filename == None else "blank.png")
			img = ImageTk.PhotoImage(Image.open(icon_path)) if icon_path else None
			display_text = self.fish.translate("meta",fish_key,fish_subkey)
			button = tk.Button(toolbar,image=img,relief=tk.FLAT,width=16,height=16,command=command,state="disabled" if command == None else "normal")
			button.img = img
			widgetlib.ToolTip(button,display_text)
			button.pack(side=tk.LEFT,padx=2,pady=2)
			return button

		def create_toolbar_buttons(toolbar_buttons):
			for (fish_keys,image_filename,command) in toolbar_buttons:
				create_toolbar_button(fish_keys[0],fish_keys[1],image_filename,command)

		toolbar.pack(side=tk.TOP,fill=tk.X)
		toolbar_buttons = [
			(["menu","file.open"],"open.png",self.open_file), #File -> Open
			(["menu","file.save"],"save.png",self.save_file_as), #File -> Save
			(["menu","export.inject"],"inject.png",self.inject_into_ROM), #Export -> Inject
			(["menu","export.inject-new"],"inject-new.png",self.copy_into_ROM) #Export -> Inject Copy
		]
		create_toolbar_buttons(toolbar_buttons)

	def create_cascade(self, name, internal_name, options_list, parent_menu=None):
		#options_list must be a list of 3-tuples containing
		# Display Name
		# image name (without the .png extension)
		# function to call
		if parent_menu == None:
			parent_menu = self.menu
		cascade = tk.Menu(parent_menu, tearoff=0, name=internal_name)
		cascade.images = {}
		for display_name,image_name,function_to_call in options_list:
			if (display_name,image_name,function_to_call) == (None,None,None):
				cascade.add_separator()
			else:
				if image_name:
					image_filename = (f"{image_name}")
					image_filename += ".gif" if "gif" in image_filename else ".png"
					image_path = os.path.join("meta","icons")
					if "game_plugins" in internal_name:
						image_path = os.path.join(self.game.resource_subpath,"icons")
					if "sprite_plugins" in internal_name:
						image_path = os.path.join(self.sprite.resource_subpath,"icons")
					cascade.images[image_name] = ImageTk.PhotoImage(Image.open(common.get_resource(image_path,image_filename)))
				else:
					cascade.images[image_name] = None
				cascade.add_command(label=display_name, image=cascade.images[image_name], compound=tk.LEFT, command=function_to_call, state="disabled" if function_to_call == None else "normal")
		parent_menu.add_cascade(label=name, menu=cascade)
		return cascade

	def create_menu_bar(self):
		#create the menu bar
		self.menu = tk.Menu(self.master, name="menu_bar")
		self.master.configure(menu=self.menu)

		menu_options = []

		#create the file menu
		file_menu = self.create_cascade(self.fish.translate("meta","menu","file"), "file_menu",
											[
													(self.fish.translate("meta","menu","file.open"),"open",self.open_file),
													(self.fish.translate("meta","menu","file.save"),"save",self.save_file_as),
													(self.fish.translate("meta","menu","file.exit"),"exit",self.exit),
											])
		menu_options.append(file_menu)

		#create the import menu
		import_menu = self.create_cascade(self.fish.translate("meta","menu","export"),"export_menu",
											[
													(self.fish.translate("meta","menu","export.inject"),"inject",self.inject_into_ROM),
													(self.fish.translate("meta","menu","export.inject-new"),"inject-new",self.copy_into_ROM),
													(self.fish.translate("meta","menu","export.inject-bulk"),"inject-bulk",self.inject_into_ROM_bulk),
													(None,None,None),
													(self.fish.translate("meta","menu","export.frame-as-png"),"frame-as-png",self.export_frame_as_png),
													(self.fish.translate("meta","menu","export.animation-as-gif"),"animation-as-gif",None),#self.export_animation_as_gif),
													(self.fish.translate("meta","menu","export.animation-as-hcollage"),"animation-as-hcollage",partial(self.export_animation_as_collage,"horizontal")),
													(self.fish.translate("meta","menu","export.animation-as-vcollage"),"animation-as-vcollage",None),#partial(self.export_animation_as_collage,"vertical")),
											])
		menu_options.append(import_menu)

		#for future implementation
		plugins_menu = tk.Menu(self.menu, tearoff=0, name="plugins_menu")
		tools_menu = tk.Menu(self.menu, tearoff=0, name="tools_menu")
		tools_menu.add_command(label=self.fish.translate("meta","menu","tools.palette-editor"),command=None,state="disabled")
		tools_menu.add_cascade(label=self.fish.translate("meta","menu","plugins"), menu=plugins_menu)
		self.menu.add_cascade(label=self.fish.translate("meta","menu","tools"), menu=tools_menu)

		help_menu = self.create_cascade(self.fish.translate("meta","menu","help"),"help_menu",
											[
													(self.fish.translate("meta","menu","help.diagnostics"),"help-diagnostics",self.diagnostics),
													(self.fish.translate("meta","menu","help.about"),"app",self.about),
											])
		menu_options.append(help_menu)


	#load plugins
	def load_plugins(self):
		self.menu.children["plugins_menu"] = tk.Menu(self.menu, tearoff=0, name="plugins_menu")

		#if we've got Game plugins or Sprite plugins
		if False:#self.game.plugins or self.sprite.plugins:
			plugins_container = []
			#if we've got Game plugins, start the menu
			if self.game.plugins:
				#add the commands
				commands = []
				for label, icon, command in self.game.plugins:
					commands.append((label,icon,command))
				game_plugins_menu = self.create_cascade(self.fish.translate("meta","menu","plugins.game"),"game_plugins_menu",commands,self.menu.children["plugins_menu"])
				plugins_container.append(game_plugins_menu)

			#if we've got Sprite plugins
			if self.sprite.plugins:
				#add the commands
				commands = []
				for label, icon, command in self.sprite.plugins:
					commands.append((label,icon,command))
				sprite_plugins_menu = self.create_cascade(self.fish.translate("meta","menu","plugins.sprite"),"sprite_plugins_menu",commands,self.menu.children["plugins_menu"])
				plugins_container.append(sprite_plugins_menu)
		else:
			#if we got nothin', say as such
			self.menu.children["plugins_menu"].add_command(label=self.fish.translate("meta","meta","none"),state="disabled")

	#load sprite
	# Inbound:
	#  sprite_filename: Filename of sprite to load
	def load_sprite(self, sprite_filename):
		self.game, self.sprite, self.animation_assist = gamelib.autodetect(sprite_filename)
		self.fish.add_translation_file(self.sprite.resource_subpath)
		self.sprite_coord = (100,100)        #an arbitrary default
		self.attach_both_panels()            #remake the GUI panels
		self.load_plugins()
		self.initialize_sprite_animation()

	def attach_both_panels(self):
		#this same function can also be used to re-create the panels
		#have to make the canvas before the buttons so that the left panel buttons can manipulate it
		self.freeze_ray = True    #do not update the sprite while doing this
		if hasattr(self, "timer_callback"):
			self.master.after_cancel(self.timer_callback)
		if hasattr(self, "left_panel"):
			for widget in self.left_panel.winfo_children():
				#if we've got direction buttons
				if "direction_buttons" in widget.winfo_name():
					#get the main bindings file
					bindings = None
					bindings_filename = common.get_resource("meta","bindings.json")
					with open(bindings_filename,encoding="utf-8") as f:
						bindings = json.load(f)
					#cycle through all spiffy buttons
					for subwidget in widget.winfo_children():
						if "_button" in subwidget.winfo_name():
							button_name = subwidget.winfo_name().replace("_button","")
							button_section = button_name[:button_name.find("_")]
							button_name = button_name[button_name.find("_")+1:]
							keypresses = None
							keypresses_switcher = bindings[button_section] if button_section in bindings else {}
							keypresses = keypresses_switcher.get(button_name.lower(),None)
							if keypresses:
								#nuke all the bindings from orbit
								for keypress in keypresses:
									subwidget.unbind_all(keypress)
								#nuke this button from orbit
								subwidget.destroy()
		self.left_panel = tk.PanedWindow(self.panes, orient=tk.VERTICAL, name="left_panel",width=250,handlesize=0,sashwidth=0,sashpad=2)
		self.right_panel = ttk.Notebook(self.panes, name="right_pane")
		self.canvas = tk.Canvas(self.right_panel, name="main_canvas")
		self.overview_frame = tk.Frame(self.right_panel, name="overview_frame")
		self.overview_canvas = tk.Canvas(self.overview_frame, name="overview_canvas")
		self.attach_left_panel()
		self.attach_right_panel()
		self.create_status_bar()

	def attach_left_panel(self):
		#this same function can also be used to re-create the panel
		MINSIZE = 25
		vcr_controls = self.get_vcr_controls()  #have to do this early so that their values are available for other buttons
		self.left_panel.add(self.get_reload_button(),minsize=MINSIZE)
		self.attach_metadata_panel()
		self.game.attach_background_panel(self.left_panel,self.canvas,self.zoom_getter,self.frame_getter,self.fish)
		self.animation_assist.attach_animation_panel(self.left_panel,self.canvas,self.overview_canvas,self.zoom_getter,self.frame_getter,self.coord_getter,self.fish)
		self.left_panel.add(vcr_controls,minsize=MINSIZE)
		self.panes.add(self.left_panel)

	def attach_right_panel(self):
		#this same function can also be used to re-create the panel
		self.attach_canvas()
		self.attach_overview()
		self.panes.add(self.right_panel)

	def attach_metadata_panel(self):
		PANEL_HEIGHT = 64
		metadata_section = tk.Frame(self.left_panel, name="metadata_section")
		row = 0
		self.metadata_textbox_vars = {}
		for key in ["sprite.name","author.name","author.name-short"]:
			label = self.fish.translate("meta","meta",key)
			metadata_label = tk.Label(metadata_section, text=label, name=label.lower().replace(' ', '_'))
			metadata_label.grid(row=row,column=1)
			self.metadata_textbox_vars[key] = tk.StringVar()
			metadata_input = tk.Entry(metadata_section, textvariable=self.metadata_textbox_vars[key], name=label.lower().replace(' ', '_') + "_input")
			metadata_input.insert(0,self.sprite.metadata[key])

			def metadata_changed_trace(key, *args):
				#touch We Made Changes var
				self.sprite.metadata[key] = self.metadata_textbox_vars[key].get()   #retrieve the GUI StringVar value and place it in the true metadata
				self.unsaved_changes = True

			#trace method, fires when the field receives a change; may have more overhead than we'd like
			self.metadata_textbox_vars[key].trace_add("write",partial(metadata_changed_trace,key))

			#validation method, fires when the field loses focus; prone to not capturing changes if user exits before blurring the tk.Entry
			#metadata_input.configure(validate="focusout",validatecommand=partial(metadata_changed_trace,key))

			metadata_input.grid(row=row,column=2)
			row += 1
		self.left_panel.add(metadata_section,minsize=PANEL_HEIGHT)

	#make a status bar
	def create_status_bar(self):
		if not hasattr(self, "status_bar"):
			self.status_bar = StatusBar(self)
			self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
		self.status_bar.set(self.game.name + ': "' + self.sprite.classic_name + '"')

	def attach_canvas(self):
		def move_sprite(event):
			self.sprite_coord = [event.x/self.current_zoom, event.y/self.current_zoom]
			self.update_sprite_animation()
		self.canvas.bind("<Button-1>", move_sprite)   #hook this function to call when the canvas is left-clicked
		self.right_panel.add(self.canvas, text=self.fish.translate("meta","tab","animations"))

	def attach_overview(self):
		self.overview_frame.grid_rowconfigure(0, weight=1)
		self.overview_frame.grid_columnconfigure(0, weight=1)

		xscrollbar = tk.Scrollbar(self.overview_frame, orient=tk.HORIZONTAL)
		xscrollbar.grid(row=1, column=0, sticky=tk.EW)

		yscrollbar = tk.Scrollbar(self.overview_frame)
		yscrollbar.grid(row=0, column=1, sticky=tk.NS)

		self.overview_canvas.configure(scrollregion=self.overview_canvas.bbox(tk.ALL),xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
		self.overview_canvas.grid(row=0, column=0, sticky=tk.NSEW)

		xscrollbar.config(command=self.overview_canvas.xview)
		yscrollbar.config(command=self.overview_canvas.yview)

		self.right_panel.add(self.overview_frame, text=self.fish.translate("meta","tab","overview"))

	############################ ANIMATION FUNCTIONS HERE ################################

	def initialize_sprite_animation(self):
		self.frames_left_before_freeze = CONST.MAX_FRAMES
		self.freeze_ray = True
		self.frame_number = 0
		self.sprite_coord = (100,100)    #an arbitrary default
		self.start_global_frame_timer()

	def update_sprite_animation(self):
		pass#self.sprite.update_animation()

	def start_global_frame_timer(self):
		#called by play button
		if self.freeze_ray:     #if we were frozen before
			self.frames_left_before_freeze = CONST.MAX_FRAMES
			self.freeze_ray = False
			self.time_marches_forward()

	def advance_global_frame_timer(self):
		#move frame timer forward
		self.frame_number += 1
		self.frames_left_before_freeze = max(0, self.frames_left_before_freeze - 1)
		if self.frame_number >= CONST.MAX_FRAMES:   #just in case someone leaves this running for, say...forever
			self.reset_global_frame_timer()
		self.update_sprite_animation()

	def play_once(self):
		self.frames_left_before_freeze = self.sprite.frames_in_this_animation()
		if self.freeze_ray:   #if we were frozen before
			self.freeze_ray = False
			self.time_marches_forward()

	def reset_global_frame_timer(self):
		#called by radio reset button
		self.frame_number = 0
		self.pause_global_frame_timer()

	def pause_global_frame_timer(self):
		#called by pause button
		self.frames_left_before_freeze = 0
		self.freeze_ray = True
		self.update_sprite_animation()

	def rewind_global_frame_timer(self):
		#called by step radio button to pause and step backward
		self.frame_number = max(0,self.frame_number - 1)
		self.pause_global_frame_timer()

	def step_global_frame_timer(self):
		#called by step radio button to pause and step forward
		self.pause_global_frame_timer()
		self.advance_global_frame_timer()

	def go_to_previous_pose(self):
		self.frame_number = max(0,self.frame_number - self.sprite.frames_to_previous_pose())
		self.pause_global_frame_timer()

	def go_to_next_pose(self):
		self.frame_number = self.frame_number + self.sprite.frames_left_in_this_pose()
		self.pause_global_frame_timer()

	def time_marches_forward(self):
		start_time = time.perf_counter()
		MIN_WAIT = 5      #have to give the rest of the program time to work, and tkInter is not thread-safe
		FRAME_DELAY = 17  #equal to about ceiling(1000/60) in order to simulate 60 Hz (can't go faster without skipping frames due to PC monitor refresh rate)
		if self.frames_left_before_freeze > 0 and not self.freeze_ray:
			self.advance_global_frame_timer()
			end_time = time.perf_counter()
			lag = (end_time-start_time)*1000
			wait_time = int(FRAME_DELAY/self.current_speed - lag)
			self.timer_callback = self.master.after(max(wait_time,5), self.time_marches_forward)     #schedule next tick of the clock
		else:
			self.pause_global_frame_timer()

	def zoom_getter(self):
		return self.current_zoom

	def frame_getter(self):
		return self.frame_number

	def coord_getter(self):
		return self.sprite_coord

	########################### VCR CONTROLS HERE ######################################

	def get_vcr_controls(self):
		control_section = tk.Frame(self.left_panel, name="vcr_controls_section")
		widgetlib.right_align_grid_in_frame(control_section)

		def zoom_out(*args):
			self.current_zoom = max(0.5, self.current_zoom - 0.1)
			set_zoom_text()
			self.game.update_background_image()
			self.update_sprite_animation()
		def zoom_in(*args):
			self.current_zoom = min(4.0, self.current_zoom + 0.1)
			set_zoom_text()
			self.game.update_background_image()
			self.update_sprite_animation()
		def set_zoom_text():
			self.zoom_factor.set('x' + str(round(self.current_zoom, 1)) + ' ')

		def speed_down(*args):
			self.current_speed = max(0.1, self.current_speed - 0.1)
			set_speed_text()
		def speed_up(*args):
			self.current_speed = min(2.0, self.current_speed + 0.1)
			set_speed_text()
		def set_speed_text():
			self.speed_factor.set(str(round(self.current_speed * 100)) + '%')

		if not hasattr(self,"current_zoom"):
			self.current_zoom = 2              #starting zoom, if app is just started
		if not hasattr(self,"current_speed"):
			self.current_speed = 1             #starting speed, if app is just started
		if not hasattr(self,"frame_number"):
			self.frame_number = 0              #starting frame, if app is just started
		self.zoom_factor = tk.StringVar(control_section)
		self.speed_factor = tk.StringVar(control_section)

		set_zoom_text()
		set_speed_text()

		BUTTON_WIDTH = 60
		self.current_grid_cell = 0

		#make a vcr button label
		# Inbound
		#  textvariable: var to report back to
		#  icon_name: filename of icon to use
		def make_vcr_label(textvariable, icon_name=None):
			icon_path = common.get_resource(["meta","icons"],icon_name if not icon_name == None else "blank.png")
			image = ImageTk.PhotoImage(Image.open(icon_path)) if icon_path else None
			vcr_label = tk.Label(control_section, image=image, anchor='e', compound="left", width=BUTTON_WIDTH, textvariable=textvariable)
			vcr_label.grid(row = self.current_grid_cell//3,
						column = 1 + (self.current_grid_cell % 3),
						sticky=['nes'])
			self.current_grid_cell += 1
			return vcr_label

		#make a vcr button
		# Inbound
		#  text: text label
		#  icon_name: filename of icon to use
		#  command: command to execute when pressed
		#  side: alignment
		def make_vcr_button(text="", icon_name=None, command=None, side=""):
			side = side if not side == "" else "right"
			icon_path = common.get_resource(["meta","icons"],icon_name if not icon_name == None else "blank.png")
			image = ImageTk.PhotoImage(Image.open(icon_path)) if icon_path else None
			if side == "right":
				side = tk.RIGHT
			elif side == "left":
				side = tk.LEFT
			else:
				side = tk.NONE
			vcr_button = tk.Button(control_section, image=image, text=text, compound=side, width=BUTTON_WIDTH, command=command)
			vcr_button.image = image
			vcr_button.grid(row = self.current_grid_cell//3,
						column = 1 + (self.current_grid_cell % 3),
						sticky=['nesw','nesw','nesw'][self.current_grid_cell % 3])
			self.current_grid_cell += 1

		def make_vcr_buttons(vcr_buttons_in):
			vcr_buttons_out = []
			for (fish_subkey, icon_name, command, side) in vcr_buttons_in:
				vcr_buttons_out.append(make_vcr_button(self.fish.translate("meta","vcr-controls",fish_subkey), icon_name, command, side))

		#make a container for all the buttons
		vcr_buttons = []

		#zoom controls
		zoom_factor_label = make_vcr_label(self.zoom_factor, None)
		zoom_buttons = [
			("zoom-minus","zoom-out.png",zoom_out,"left"),
			("zoom-plus","zoom-in.png",zoom_in,"")
		]
		make_vcr_buttons(zoom_buttons)

		#speed controls
		speed_factor_label = make_vcr_label(self.speed_factor,None)
		speed_buttons = [
			("speed-minus","speed-down.png",speed_down,"left"),
			("speed-plus","speed-up.png",speed_up,"")
		]
		make_vcr_buttons(speed_buttons)

		#play controls
		play_buttons = [
			("play","play.png",self.start_global_frame_timer,""),
			("play-one","play-one.png",self.play_once,""),
			("reset","reset.png",self.reset_global_frame_timer,"")
		]
		make_vcr_buttons(play_buttons)

		#frame step controls
		frame_step_buttons = [
			("frame-backward","frame-backward.png",self.rewind_global_frame_timer,"left"),
			("pause","pause.png",self.pause_global_frame_timer,""),
			("frame-forward","frame-forward.png",self.step_global_frame_timer,"")
		]
		make_vcr_buttons(frame_step_buttons)

		#pose step controls
		make_vcr_buttons([("pose-backward","step-backward.png",self.go_to_previous_pose,"left")])
		null_label = make_vcr_label("", None)
		make_vcr_buttons([("pose-forward","step-forward.png",self.go_to_next_pose,"")])

		return control_section

	def get_reload_button(self):
		reload_section = tk.Frame(self.left_panel, name="reload_section")
		widgetlib.center_align_grid_in_frame(reload_section)
		reload_button = tk.Button(reload_section, text=self.fish.translate("meta","meta","reload"), padx=20, command=self.sprite.reload)
		reload_button.grid(row=0,column=1)
		return reload_section

	############################ MENU BAR FUNCTIONS HERE ################################

	#query user for file to open; ZSPR/PNG/SFC/SMC
	def open_file(self):
		#Give the user a chance to regret not saving their work
		if self.unsaved_changes:
			save_before_open = messagebox.askyesnocancel(self.app_title,self.fish.translate("meta","dialogue","open.save-before-open"))
			if save_before_open != None:    #didn't cancel
				if save_before_open:        #if they chose to save, present save dialogue
					saved = self.save_file_as()
					if not saved:
						messagebox.showerror(self.app_title,self.fish.translate("meta","dialogue","open.save-failed-during-open-attempt"))
						return False          #don't open a new sprite; something went wrong with the save
				else:      #chose not to save before opening
					self.unsaved_changes = False

		filename = filedialog.askopenfilename(initialdir=self.working_dirs["file.open"], title=self.fish.translate("meta","dialogue","file.open.title"), filetypes=((self.fish.translate("meta","dialogue","file.open.types.label"),"*.zspr *.png *.sfc *.smc"),))
		if filename:
			#if we've got a filename, set the working dir and load the sprite
			self.working_dirs["file.open"] = filename[:filename.rfind('/')]
			self.load_sprite(filename)
			return True        #report success to caller, if they care
		else:
			return False       #we didn't open anything

	#query user to export file; PNG/ZSPR/RDC
	def save_file_as(self):
		# Save in one of the valid formats.  TODO: When ZSPR export is implemented, switch this around so that ZSPR is the default
		filetypes = ((self.fish.translate("meta","dialogue","file.save.png"),"*.png"),(self.fish.translate("meta","dialogue","file.save.zspr"),"*.zspr"),(self.fish.translate("meta","dialogue","file.save.rdc"),"*.rdc"))
		filename = filedialog.asksaveasfilename(defaultextension=(".png",".zspr",".rdc"), initialdir=self.working_dirs["file.save"], title=self.fish.translate("meta","dialogue","file.save.title"), filetypes=filetypes)
		if filename:
			save_success_bool = self.sprite.save_as(filename)
			if save_success_bool:
				self.unsaved_changes = False
				self.working_dirs["file.save"] = os.path.dirname(filename)
				messagebox.showinfo("Save Complete", f"Saved as {filename}")
				self.save_working_dirs()
			else:
				messagebox.showerror("Not Yet Implemented",os.path.splitext(filename)[1][1:].upper() + " format not yet available for " + self.game.name + '/' + self.sprite.classic_name + " Sprites.")
			return save_success_bool
		else:    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
			return False

	#query user to inject sprite into game file
	# Inbound:
	#  inject: Are we injecting directly or making a copy?
	def copy_into_ROM(self, inject=False):
		dest_filename = None
		if inject:
			dest_filename = filedialog.asksaveasfilename(defaultextension=".sfc", initialdir=self.working_dirs["export.dest"], title=self.fish.translate("meta","dialogue","export.inject.title"), filetypes=((self.fish.translate("meta","dialogue","export.inject.types"),"*.sfc *.smc"),))
			source_filename = dest_filename
		else:
			source_filename = filedialog.askopenfilename(initialdir=self.working_dirs["export.source"], title=self.fish.translate("meta","dialogue","export.source.title"), filetypes=((self.fish.translate("meta","dialogue","export.source.types"),"*.sfc *.smc"),))
			if source_filename:
				_,file_extension = os.path.splitext(source_filename)
				if file_extension.lower() in ['.sfc','.smc']:
					default_extension = file_extension.lower()
				else:
					default_extension = ".sfc"
				dest_filename = filedialog.asksaveasfilename(defaultextension=default_extension, initialdir=self.working_dirs["export.dest"], title=self.fish.translate("meta","dialogue","export.inject-new.title"), filetypes=((self.fish.translate("meta","dialogue","export.inject-new.types"),"*.sfc *.smc"),))
		if dest_filename:
			rom = self.game.get_rom_from_filename(source_filename)
			modified_rom = self.sprite.inject_into_ROM(rom)
			modified_rom.save(dest_filename, overwrite=True)
			self.working_dirs["export.dest"] = dest_filename[:dest_filename.rfind('/')]
			self.working_dirs["export.source"] = source_filename[:source_filename.rfind('/')]
			messagebox.showinfo("Export success",f"Saved injected ROM as {dest_filename}")

	#query user for directory to inject sprite into
	def copy_into_ROM_bulk(self, inject=False):
		source_filepath = None
		if inject:
			source_filepath = filedialog.askdirectory()	#only injection is supported
		else:
			raise AssertionError("Unsure if making copies fits this purpose well")

		source_filenames = []	#walk through the game files and inject the loaded sprite
		for r,d,f in os.walk(source_filepath):
			for file in f:
				_,file_extension = os.path.splitext(file)
				if file_extension.lower() in ['.sfc','.smc']:
					source_filenames.append(os.path.join(r,file))
		for source_filename in source_filenames:
			dest_filename = source_filename
			rom = self.game.get_rom_from_filename(source_filename)	#read ROM data
			same_internal_name = self.game.internal_name == gamelib.autodetect_game_type_from_rom_filename(source_filename)[0]	#the game file matches
			is_zsm = "ZSM" in str(rom.get_name())	#this is a ZSM game file
			if same_internal_name or (is_zsm and self.sprite.classic_name in ["Link","Samus"]):	#if we've got a compatible game file, inject it!
				modified_rom = self.sprite.inject_into_ROM(rom)
				modified_rom.save(dest_filename, overwrite=True)

	#alias to inject into a game file
	def inject_into_ROM(self):
		self.copy_into_ROM(inject=True)

	#alias to inject into a directory of game filefs
	def inject_into_ROM_bulk(self):
		self.copy_into_ROM_bulk(inject=True)

	#export current frame as PNG
	def export_frame_as_png(self):
		filetypes = ((self.fish.translate("meta","dialogue","file.save.png"),"*.png"),)
		filename = filedialog.asksaveasfilename(defaultextension=(".png"), initialdir=self.working_dirs["export.frame-as-png"], title=self.fish.translate("meta","dialogue","export.frame-as-png"), filetypes=filetypes)
		if filename:
			returnvalue = self.sprite.export_frame_as_PNG(filename)
			if returnvalue:
				self.working_dirs["export.frame-as-png"] = filename[:filename.rfind('/')]
				messagebox.showinfo("Save Complete", f"Saved as {filename}")
			return returnvalue
		else:    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
			return False

	#export current animation as GIF
	def export_animation_as_gif(self):
		raise NotImplementedError()

	#export current animation as collage PNG
	def export_animation_as_collage(self,orientation="horizontal"):
		if orientation == "vertical":
			raise NotImplementedError()
		filetypes = ((self.fish.translate("meta","dialogue","file.save.png"),"*.png"),)
		filename = filedialog.asksaveasfilename(defaultextension=(".png"), initialdir=self.working_dirs["export.animation-as-" + orientation[:1] + "collage"], title=self.fish.translate("meta","dialogue","export.animation-as-" + orientation[:1] + "collage"), filetypes=filetypes)
		if filename:
			returnvalue = self.sprite.export_animation_as_collage(filename,orientation)
			if returnvalue:
				self.working_dirs["export.animation-as-collage"] = filename[:filename.rfind('/')]
				messagebox.showinfo("Save Complete", f"Saved as {filename}")
			return returnvalue
		else:    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
			return False

	def diagnostics(self):
		# Debugging purposes
		dims = {
			"window": {
				"width": 800,
				"height": 500
			},
			"textarea.characters": {
				"width": 120,
				"height": 50
			}
		}
		diag = tk.Tk()
		diag.title("SpriteSomething Diagnostics")
		diag.geometry(str(dims["window"]["width"]) + 'x' + str(dims["window"]["height"]))
		text = tk.Text(diag, width=dims["textarea.characters"]["width"], height=dims["textarea.characters"]["height"])
		text.pack()
		self.add_text_link_array(diagnostics.output(), text)

	def about(self):
		# Credit where credit's due
		dims = {
			"window": {
				"width": 300,
				"height": 200
			},
			"textarea.characters": {
				"width": 60,
				"height": 100
			}
		}
		def txtEvent(event):
			return "break"
		lines = [
				  "SpriteSomething v" + CONST.APP_VERSION,
				  "",
				  "Created by:",
				  "Artheau & Mike Trethewey",
				  "",
				  "Based on:",
				  "[SpriteAnimator](http://github.com/spannerisms/SpriteAnimator) by Spannerisms",
				  "[ZSpriteTools](http://github.com/sosuke3/ZSpriteTools) by Sosuke3",
				  # Assets from ZSpriteTools used with permission
		]
		about = tk.Tk()
		about.title(f"About {self.app_title}")
		about.geometry(str(dims["window"]["width"]) + 'x' + str(dims["window"]["height"]))
		about.resizable(tk.FALSE,tk.FALSE)
		#about.attributes("-toolwindow", 1)	#Linux doesn't like this
		text = tk.Text(about, bg='#f0f0f0', font='TkDefaultFont', width=dims["textarea.characters"]["width"], height=dims["textarea.characters"]["height"])
		text.pack()
		text.configure(cursor="arrow")
		self.add_text_link_array(lines, text)
		text.bind("<Button-1>", lambda e: txtEvent(e))

	#write working dirs to file
	def save_working_dirs(self):
		f = open("./resources/meta/working_dirs.json","w+")
		f.write(json.dumps(self.working_dirs,indent=2))

	#exit sequence
	def exit(self):
		if self.unsaved_changes:
			save_before_exit = messagebox.askyesnocancel(self.app_title,self.fish.translate("meta","dialogue","exit.save-before-exit"))
			if save_before_exit != None:        #didn't cancel
				if save_before_exit:
					saved = self.save_file_as()
					if not saved:
						exit_anyway = messagebox.askyesno(self.app_title, self.fish.translate("meta","dialogue","exit.save-failed-during-exit-attempt"))
						if not exit_anyway:
							#user bails because their file didn't save
							return
				else:
					messagebox.showwarning(self.app_title, self.fish.translate("meta","dialogue","exit.nosave-before-exit"))   #TODO: can we add this humor somehow without forcing the user to close another dialogue box?

		self.save_working_dirs()
		sys.exit(0)

	######################### HELPER FUNCTIONS ARE BELOW HERE ###############################

	def add_text_link_array(self,lines,textObject):
		# Gui.class
		# Add an array of text lines, linkifying as necessary
		#ins:
		# lines: Lines of text to add
		# textObject: Text object to add lines to
		hyperlink = HyperlinkManager(textObject)
		for line in lines:
			matches = re.search(r'(.*)\[(.*)\]\((.*)\)(.*)',line)
			if matches:
				def click1(url=matches.group(3)):
					webbrowser.open_new(url)
				textObject.insert(tk.INSERT, matches.group(1))
				textObject.insert(tk.INSERT, matches.group(2), hyperlink.add(click1))
				textObject.insert(tk.INSERT, matches.group(4))
				textObject.insert(tk.INSERT, "\n")
			else:
				textObject.insert(tk.INSERT, line + "\n")
