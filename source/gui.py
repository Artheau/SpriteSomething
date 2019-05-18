import tkinter as tk
from functools import partial
from tkinter import ttk, messagebox, filedialog
import random
import json
import re
import traceback
import os, sys
import time
from source import constants as CONST
from source import crxtooltip as crx
from source import gamelib
from source import ssDiagnostics as diagnostics
from source import widgetlib
from source.tkHyperlinkManager import HyperlinkManager
from source.tkSimpleStatusBar import StatusBar
from source import common

dims = {
	"button": {
		"width": 7
	}
}

def make_GUI(command_line_args):
	root = tk.Tk()
	root.iconbitmap(default=common.get_resource('app.ico'))
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

		self.create_random_title()

		self.pack(fill=tk.BOTH, expand=1)    #main frame should take up the whole window

		self.create_menu_bar()

		self.panes = tk.PanedWindow(self, orient=tk.HORIZONTAL, name="two_columns")
		self.panes.pack(fill=tk.BOTH, expand=1)

		self.load_sprite(command_line_args["sprite"])

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

	def create_menu_bar(self):
		#create the menu bar
		menu = tk.Menu(self.master, name="menu_bar")
		self.master.configure(menu=menu)

		def create_cascade(name, internal_name, options_list):
			#options_list must be a list of 3-tuples containing
			# Display Name
			# image name (without the .png extension)
			# function to call
			cascade = tk.Menu(menu, tearoff=0, name=internal_name)
			cascade.images = {}
			for display_name,image_name,function_to_call in options_list:
				if (display_name,image_name,function_to_call) == (None,None,None):
					cascade.add_separator()
				else:
					if image_name:
						cascade.images[image_name] = tk.PhotoImage(file=common.get_resource(f"{image_name}.png",os.path.join("meta","icons")))
					else:
						cascade.images[image_name] = None
					cascade.add_command(label=display_name, image=cascade.images[image_name], compound=tk.LEFT, command=function_to_call)
			menu.add_cascade(label=name, menu=cascade)

		#create the file menu
		file_menu = create_cascade("File", "file_menu",
											[
													("Open","open",self.open_file),
													("Save As...","save",self.save_file_as),
													("Exit","exit",self.exit),
											])

		#create the import menu
		import_menu = create_cascade("Export","export_menu",
											[
													("Inject into Game File","inject",self.inject_into_ROM),
													("Copy to new Game File",None,self.copy_into_ROM),
													(None,None,None),
													("Animation as GIF",None,self.export_animation_as_gif),
													("Animation as Collage",None,self.export_animation_as_collage),
													(None,None,None),
													("Tracker Images for this Pose",None,self.export_tracker_images_for_this_pose),
											])

		'''
		#for future implementation
		tools_menu = create_cascade("Tools","tools_menu",
											[
													#this part can match up with the game class, or maybe the sprite class?
													#have to update this cascade when the game/sprite changes though
													#waiting on this decision until we have plugins to add here
											])
		'''

		help_menu = create_cascade("Help","help_menu",
											[
													("Diagnostics",None,self.diagnostics),
													("About",None,self.about),
											])

	def load_sprite(self, sprite_filename):
		self.game, self.sprite = gamelib.autodetect(sprite_filename)
		self.sprite_coord = (100,100)        #an arbitrary default
		self.attach_both_panels()            #remake the GUI panels
		self.initialize_sprite_animation()

	def attach_both_panels(self):
		#this same function can also be used to re-create the panels
		#have to make the canvas before the buttons so that the left panel buttons can manipulate it
		self.freeze_ray = True    #do not update the sprite while doing this
		if hasattr(self, "timer_callback"):
			self.master.after_cancel(self.timer_callback)
		self.left_panel = tk.PanedWindow(self.panes, orient=tk.VERTICAL, name="left_panel",width=250,handlesize=0,sashwidth=0)
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
		spiffy_buttons = self.get_spiffy_buttons()
		self.left_panel.add(self.get_reload_button(),minsize=MINSIZE)
		self.sprite.attach_metadata_panel(self.left_panel)
		self.game.attach_background_panel(self.left_panel,self.canvas,self.zoom_getter,self.frame_getter)
		self.sprite.attach_animation_panel(self.left_panel,self.canvas,self.overview_canvas,self.zoom_getter,self.frame_getter,self.coord_getter)
		self.left_panel.add(spiffy_buttons)
		self.left_panel.add(vcr_controls,minsize=MINSIZE)
		self.panes.add(self.left_panel)

	def attach_right_panel(self):
		#this same function can also be used to re-create the panel
		self.attach_canvas()
		self.attach_overview()
		self.panes.add(self.right_panel)

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
		self.right_panel.add(self.canvas, text='Animations')

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

		self.right_panel.add(self.overview_frame, text='Overview')


	############################ ANIMATION FUNCTIONS HERE ################################

	def initialize_sprite_animation(self):
		self.frames_left_before_freeze = CONST.MAX_FRAMES
		self.freeze_ray = False
		self.frame_number = 0
		self.sprite_coord = (100,100)    #an arbitrary default
		self.update_sprite_animation()
		self.time_marches_forward()

	def update_sprite_animation(self):
		if not self.freeze_ray:
			self.sprite.update_animation()

	def start_global_frame_timer(self):
		#called by play button
		if self.frames_left_before_freeze <= 0:
			self.frames_left_before_freeze = CONST.MAX_FRAMES
		self.time_marches_forward()
		self.update_sprite_animation()

	def advance_global_frame_timer(self):
		#move frame timer forward
		self.frame_number += 1
		self.frames_left_before_freeze = max(0, self.frames_left_before_freeze - 1)
		if self.frame_number >= CONST.MAX_FRAMES:   #just in case someone leaves this running for, say...forever
			self.reset_global_frame_timer()
		self.update_sprite_animation()

	def play_once(self):
		self.frames_left_before_freeze = self.sprite.frames_in_this_animation()
		self.start_global_frame_timer()

	def reset_global_frame_timer(self):
		#called by radio reset button
		self.frame_number = 0
		self.pause_global_frame_timer()

	def pause_global_frame_timer(self):
		#called by pause button
		self.frames_left_before_freeze = 0
		self.update_sprite_animation()

	def rewind_global_frame_timer(self):
		#called by step radio button to pause and step backward
		self.frame_number = self.frame_number - 1
		self.pause_global_frame_timer()

	def step_global_frame_timer(self):
		#called by step radio button to pause and step forward
		self.pause_global_frame_timer()
		self.advance_global_frame_timer()

	def go_to_previous_pose(self):
		self.frame_number = self.frame_number - self.sprite.frames_to_previous_pose()
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


  ########################### SPIFFY BUTTONS HERE ####################################
	def get_spiffy_buttons(self):
		dims = {
			"button": {
				"width": 20,
				"height": 20,
				"color.active": "#78C0F8",
				"color.selected": "#C0E0C0"
			}
		}
		spiffy_buttons_section = tk.Frame(self.left_panel, name="spiffy_buttons")
		widgetlib.right_align_grid_in_frame(spiffy_buttons_section)
		row = 0
		for i in range(len(self.sprite.spiffy_buttons)):
			col = 0
			label = self.sprite.spiffy_buttons[i][0]
			levels = self.sprite.spiffy_buttons[i][1]
			prefix = self.sprite.spiffy_buttons[i][2]
			suffix = self.sprite.spiffy_buttons[i][3]
			section_label = tk.Label(spiffy_buttons_section, text=label + ':')
			section_label.grid(row=row, column=col, sticky='E')
			col += 1
			if prefix == "mail" or prefix == "suit":
				col += 1
			for tip,level in levels.items():
				icon_path = ""
				if level > 0 and tip != "Yes":
					icon_path = common.get_resource(prefix+'-'+str(level)+".png",os.path.join(self.game.internal_name,"icons"))
				elif tip.find("No") > -1 or tip == "Standard":
					icon_path = common.get_resource("no-thing.png",os.path.join("meta","icons"))
				elif tip.find("Yes") > -1:
					icon_path = common.get_resource("yes-thing.png",os.path.join("meta","icons"))
				img = tk.PhotoImage(file=icon_path)
				button = tk.Radiobutton(
					spiffy_buttons_section,
					image=img,
					name=prefix + str(level) + "_button",
					text=tip+suffix,
					variable=prefix,
					value=level,
					activebackground=dims["button"]["color.active"],
					selectcolor=dims["button"]["color.selected"],
					width=dims["button"]["width"],
					height=dims["button"]["height"],
					indicatoron=False,
					command=partial(self.sprite.press_spiffy_button,prefix,level)
				)
				if col == 1 or (prefix in ["mail","suit"] and level == 1):
					button.select()
					self.sprite.press_spiffy_button(prefix, level)
				crx.CreateToolTip(button,tip + suffix)
				button.image = img
				button.grid(row=row,column=col)
				col += 1
			row += 1
		return spiffy_buttons_section

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

		BUTTON_WIDTH = 10
		self.current_grid_cell = 0

		def make_vcr_label(textvariable, icon_name):
			icon_path = common.get_resource(icon_name,os.path.join("meta","icons"))
			image = tk.PhotoImage(file=icon_path) if icon_path else None
			vcr_label = tk.Label(control_section, image=image, anchor='e', width=dims["button"]["width"], textvariable=textvariable)
			vcr_label.grid(row = self.current_grid_cell//3,
						column = 1 + (self.current_grid_cell % 3),
						sticky='nes')
			self.current_grid_cell += 1
			return vcr_label

		def make_vcr_button(text, icon_name, command, side="right"):
			icon_path = common.get_resource(icon_name,os.path.join("meta","icons"))
			image = tk.PhotoImage(file=icon_path) if icon_path else None
			if side == "right":
				side = tk.RIGHT
			elif side == "left":
				side = tk.LEFT
			else:
				side = tk.NONE
			print(icon_path)
			vcr_button = tk.Button(control_section, image=image, text=text, compound=side, width=dims["button"]["width"], command=command)
			vcr_button.image = image
			vcr_button.grid(row = self.current_grid_cell//3,
						column = 1 + (self.current_grid_cell % 3),
						sticky=['nesw','nesw','nesw'][self.current_grid_cell % 3])
			self.current_grid_cell += 1
			return vcr_button

		zoom_factor_label = make_vcr_label(self.zoom_factor, None)
		zoom_out_button = make_vcr_button("Zoom -",None,zoom_out)
		zoom_in_button = make_vcr_button("Zoom +",None,zoom_in)

		speed_factor_label = make_vcr_label(self.speed_factor,None)
		speed_down_button = make_vcr_button("Speed -",None,speed_down)
		speed_up_button = make_vcr_button("Speed +",None,speed_up)

		play_button = make_vcr_button("Play", "play.png", self.start_global_frame_timer)
		play_one_button = make_vcr_button("Play 1", "play-one.png", self.play_once)
		reset_button = make_vcr_button("Reset", None, self.reset_global_frame_timer)

		frame_back_button = make_vcr_button("Frame", "frame-backward.png", self.rewind_global_frame_timer, "left")
		pause_button = make_vcr_button("Pause", "pause.png", self.pause_global_frame_timer)
		frame_forward_button = make_vcr_button("Frame", "frame-forward.png", self.step_global_frame_timer)

		step_back_button = make_vcr_button("Pose", "step-backward.png", self.go_to_previous_pose, "left")
		null_label = make_vcr_label("", None)
		step_forward_button = make_vcr_button("Pose", "step-forward.png", self.go_to_next_pose)

		return control_section


	def get_reload_button(self):
		reload_section = tk.Frame(self.left_panel, name="reload_section")
		widgetlib.center_align_grid_in_frame(reload_section)
		reload_button = tk.Button(reload_section, text="Reload", padx=20, command=self.sprite.reload)
		reload_button.grid(row=0,column=1)
		return reload_section



	############################ MENU BAR FUNCTIONS HERE ################################


	def open_file(self):
		#TODO: Give the user a chance to regret not saving their work
		filename = filedialog.askopenfilename(initialdir="./", title="Select Sprite", filetypes=(("Supported Types","*.zspr *.png *.sfc *.smc"),))
		if filename:
			self.load_sprite(filename)

	def save_file_as(self):
		# Save a ZSPR or PNG.  TODO: When ZSPR export is implemented, switch this around so that ZSPR is the default
		filetypes = (("PNG Files","*.png"),("ZSPR Files","*.zspr"))
		filename = filedialog.asksaveasfilename(defaultextension=(".png",".zspr"), initialdir="./", title="Save Sprite As...", filetypes=filetypes)
		if filename:
			returnvalue = self.sprite.save_as(filename)
			if returnvalue:
				messagebox.showinfo("Save Complete", f"Saved as {filename}")
			return returnvalue
		else:    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
			return False

	def copy_into_ROM(self, inject=False):
		if inject:
			dest_filename = filedialog.asksaveasfilename(defaultextension=".sfc", initialdir="./", title="Select ROM to Modify...", filetypes=(("Game Files","*.sfc *.smc"),))
			source_filename = dest_filename
		else:
			source_filename = filedialog.askopenfilename(initialdir="./", title="Select Source ROM", filetypes=(("Game Files","*.sfc *.smc"),))
			if source_filename:
				_,file_extension = os.path.splitext(source_filename)
				if file_extension.lower() in ['.sfc','.smc']:
					default_extension = file_extension.lower()
				else:
					default_extension = ".sfc"
				dest_filename = filedialog.asksaveasfilename(defaultextension=default_extension, initialdir="./", title="Save Modified ROM As...", filetypes=(("Game Files","*.sfc *.smc"),))
		if dest_filename:
			rom = self.game.get_rom_from_filename(source_filename)
			modified_rom = self.sprite.inject_into_ROM(rom)
			modified_rom.save(dest_filename, overwrite=True)
			messagebox.showinfo("Export success",f"Saved injected ROM as {dest_filename}")

	def inject_into_ROM(self):
		self.copy_into_ROM(inject=True)

	def export_animation_as_gif(self):
		raise NotImplementedError()

	def export_animation_as_collage(self):
		raise NotImplementedError()

	def export_tracker_images_for_this_pose(self):
		raise NotImplementedError()

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
		about.attributes("-toolwindow", 1)
		text = tk.Text(about, bg='#f0f0f0', font='TkDefaultFont', width=dims["textarea.characters"]["width"], height=dims["textarea.characters"]["height"])
		text.pack()
		text.configure(cursor="arrow")
		self.add_text_link_array(lines, text)
		text.bind("<Button-1>", lambda e: txtEvent(e))

	def exit(self):
		#Until some kind of useful change/edit feature is implemented, no need to ask if they want to save their changes
		save_before_exit = False #messagebox.askyesnocancel(self.app_title,"Do you want to save before exiting?")
		if save_before_exit != None:
			if save_before_exit:
				saved = self.save_file_as()
				if saved:
					sys.exit(0)
			else:
				#messagebox.showwarning(self.app_title, "Death in Super Metroid loses progress since last save." + "\n" + "You have been eaten by a grue.")
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
