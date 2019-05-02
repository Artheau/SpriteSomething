import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import json
import re
import traceback
import os, sys
import source.ssDiagnostics as diagnostics
from source import game
from source import constants as CONST
from source.tkHyperlinkManager import HyperlinkManager
from source.tkSimpleStatusBar import StatusBar
from source import common


def make_GUI(command_line_args):
	root = tk.Tk()
	root.iconbitmap(default=common.get_resource('app.ico'))
	root.geometry("800x600")       #window size
	root.configure(bg='#f0f0f0')   #background color
	main_frame = SpriteSomethingMainFrame(root, command_line_args)
	root.protocol("WM_DELETE_WINDOW", main_frame.exit)           #intercept when the user clicks the X

	def show_error(self, exception, message, callstack):
		if exception.__name__.upper() == "NOTIMPLEMENTEDERROR":
			messagebox.showerror(   "Not Yet Implemented", "This function is not yet implemented")
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
													("Inject into ROM","inject",self.inject_into_ROM),
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
		#TODO: auto detect game name...somehow.  Otherwise there has to be a dialogue box
		game_name = "metroid3"
		#TODO: auto detect sprite identity...somehow.  Otherwise there has to be a dialogue box
		self.sprite = M3Samus(sprite_filename)

		self.attach_both_panels()
		
	def attach_both_panels(self):
		#this same function can also be used to re-create the panels
		self.create_status_bar()
		self.attach_left_panel()
		self.attach_right_panel()

	def attach_left_panel(self):
		#this same function can also be used to re-create the panel
		self.left_panel = tk.PanedWindow(self, orient=tk.VERTICAL, name="left_panel",width=300)
		self.left_panel.add(tk.Label(self.left_panel, text="Reload Button"))
		self.left_panel.add(tk.Label(self.left_panel, text="Sprite Metadata (outsourced to Entity parent class"))
		self.left_panel.add(tk.Label(self.left_panel, text="Choose Background (outsourced to Game child class)"))
		self.left_panel.add(tk.Label(self.left_panel, text="Animation Choices (outsourced to Entity child class, with default in Entity parent"))
		self.left_panel.add(tk.Label(self.left_panel, text="Sprite-relevant buttons and bars (outsourced to Entity child class)"))
		self.left_panel.add(tk.Label(self.left_panel, text="Colors?  Outsource to Entity child?"))
		self.left_panel.add(tk.Label(self.left_panel, text="GUI buttons: play et al"))
		self.panes.add(self.left_panel)

	def attach_right_panel(self):
		#this same function can also be used to re-create the panel
		self.right_panel = ttk.Notebook(self.panes, name="right_pane")
		self.canvas = tk.Canvas(self.right_panel, name="main_canvas")
		page2 = ttk.Frame(self.right_panel)
		self.right_panel.add(self.canvas, text='Animations')
		self.right_panel.add(page2, text='Overview')
		self.panes.add(self.right_panel)

	def create_status_bar(self):
		# Gui.class
		self.status_bar = StatusBar(self)
		self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
		self.status_bar.set("Status")



	############################ MENU BAR FUNCTIONS HERE ################################




	def open_file(self):
		filename = filedialog.askopenfile(initialdir="./", title="Select Sprite", filetypes=(("Supported Types","*.zspr *.png *.sfc *.smc"),))
		if filename:
			load_sprite(self, sprite_filename)

	def save_file_as(self):
		# Save a ZSPR or PNG.  TODO: When ZSPR export is implemented, switch this around so that ZSPR is the default
		filetypes = (("PNG Files","*.png"),("ZSPR Files","*.zspr"))
		filename = filedialog.asksaveasfile(defaultextension=(".png",".zspr"), initialdir="./", title="Save Sprite As...", filetypes=filetypes)
		if filename:
			raise NotImplementedError()
			return True
		else:    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
			return False
	
	def inject_into_ROM(self):
		raise NotImplementedError()

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
		save_before_exit = messagebox.askyesnocancel(self.app_title,"Do you want to save before exiting?")
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
