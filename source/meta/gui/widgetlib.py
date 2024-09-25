#common widgets, so as to easily populate the parts of the GUI that are delegated to other classes

import weakref    #because memory leaks are stupid
import tkinter as tk
import json
import os
import traceback
import locale
from PIL import Image, ImageTk
from functools import partial
from json.decoder import JSONDecodeError
from source.meta.common import common
from source.meta.gui import gui_common
from source.meta import ssTranslate as fish

def center_align_grid_in_frame(frame):
	frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
	frame.grid_columnconfigure(1000, weight=1)    #so I guess technically this just needs to be larger than the number of columns

def right_align_grid_in_frame(frame):
	frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
	frame.grid_columnconfigure(1000, weight=0)    #so I guess technically this just needs to be larger than the number of columns

def left_align_grid_in_frame(frame):
	# FIXME: English
	raise AssertionError("Aligning left in frame is not yet implemented")

def leakless_dropdown_trace(obj, var_to_trace, fun_to_call):
	#this function will add a "trace" to a particular variable, that is, to allow that variable when changed to call a particular function
	#normally this is not needed except for when things like sprite or game have widgets that they place into the main GUI
	#if this process is not done delicately, then there will be a memory leak
	#so this function handles all the weak references and whatnot in order to make sure that the destructor is correctly applied
	#
	#example: widgetlib.leakless_dropdown_trace(self, "background_selection", "set_background")
	#
	def dropdown_wrapper(this_object):
		def call_desired_function(*args):
			getattr(this_object(),fun_to_call)(getattr(this_object(),var_to_trace).get())
		return call_desired_function
	getattr(obj,var_to_trace).trace('w', dropdown_wrapper(weakref.ref(obj)))  #when the dropdown is changed, run this function
	dropdown_wrapper(weakref.ref(obj))()      #trigger this now to initialize


#this tooltip class modified from
#www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter
class ToolTip(object):
	def __init__(self, widget, text='widget info'):
		self.waittime = 500     #miliseconds
		self.wraplength = 180   #pixels
		self.widget = widget
		self.text = text
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		self.widget.bind("<ButtonPress>", self.leave)
		self.id = None
		self.tw = None

	def enter(self, event=None):
		self.schedule()

	def leave(self, event=None):
		self.unschedule()
		self.hidetip()

	def schedule(self):
		self.unschedule()
		self.id = self.widget.after(self.waittime, self.showtip)

	def unschedule(self):
		thisID = self.id
		self.id = None
		if thisID:
			self.widget.after_cancel(thisID)

	def showtip(self, event=None):
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert") # FIXME: cx,cy unused variables
		x += self.widget.winfo_rootx() + 25
		y += self.widget.winfo_rooty() + 20
		# creates a toplevel window
		self.tw = tk.Toplevel(self.widget)
		# Leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d" % (x, y))
		label = tk.Label(self.tw, text=self.text, justify='left',
					   background="#ffffff", relief='solid', borderwidth=1,
					   wraplength = self.wraplength)
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tw
		self.tw= None
		if tw:
			tw.destroy()

class SpiffyButtons():
	#They are like buttons, except spiffy
	def __init__(self, parent_frame, sprite_resource_subpath, animation_engine, frame_name="spiffy_buttons", align="right"):
		self.DIMENSIONS = {
			"button": {
				"width": 20,
				"height": 20,
				"color.active": "#78C0F8",
				"color.selected": "#C0E0C0"
			},
			"panel": {
				"height_per_button": 30
			}
		}
		self.get_animation_engine = weakref.ref(animation_engine)   #TODO: check if this is needed via unit tests.  being very careful not to make a hard link to this, to avoid circular references
		self.sprite_resource_subpath = sprite_resource_subpath
		self.spiffy_buttons_section = tk.Frame(parent_frame, name=frame_name)
		if align[0].lower() == 'r':   #align right
			right_align_grid_in_frame(self.spiffy_buttons_section)
		elif align[0].lower() == 'l':  #align left
			left_align_grid_in_frame(self.spiffy_buttons_section)
		else:
			center_align_grid_in_frame(self.spiffy_buttons_section)
		self.max_row = 0
		self.spiffy_dict = {}

	def make_new_group(self, label, fish):
		#make a new variable in the sprite object called "<label>_var"
		var_name = "_".join([label.lower(), "var"])
		self.spiffy_dict[var_name] = tk.StringVar()
		new_group = SpiffyGroup(self, self.max_row, label, self.spiffy_dict[var_name], self.sprite_resource_subpath, self.get_animation_engine, fish)
		self.max_row += 1
		return new_group

	def get_panel(self):
		section_height = self.max_row*self.DIMENSIONS["panel"]["height_per_button"]
		returnvalue = (self.spiffy_buttons_section, section_height, self.spiffy_dict)
		#chance now to get rid of anything that might make circular references.  Use commands like "del self.<var>"
		return returnvalue

class SpiffyGroup():
	#not meant to be used on its own, instead use class SpiffyButtons()
	def __init__(self, parent, row, label, var, sprite_resource_subpath, animation_engine_getter, fish):
		#disable sprite object in widgetlib
		self.sprite_resource_subpath = sprite_resource_subpath
		fish_key = self.sprite_resource_subpath.replace(os.sep,'.')
		label = fish.translate(fish_key,"section",label) #fish.translate(parent.animation_engine.resource_subpath,"section",label)
		self.label = label
		self.default_exists = False
		self.parent = parent
		self.var = var
		self.col = 0
		self.row = row

		self.get_animation_engine = animation_engine_getter

		section_label = tk.Label(self.parent.spiffy_buttons_section, text=label + ':')
		section_label.grid(row=self.row, column=self.col, sticky='E')

		self.col += 1

	def add(self, internal_value_name, image_filename, fish, default=False, disabled=False):
		if image_filename is None:
			image_filename = "blank.png"
		#disable sprite object in widgetlib
		icon_path = common.get_resource([self.sprite_resource_subpath,"icons"],image_filename) #common.get_resource([self.parent.animation_engine.resource_subpath,"icons"],image_filename)
		if icon_path is None:
			icon_path = common.get_resource(["meta","icons"],image_filename)
			if icon_path is None:
				# FIXME: English
				raise AssertionError(f"No image resource found with name {image_filename}")
		img = ImageTk.PhotoImage(Image.open(icon_path))

		#disable sprite object in widgetlib
		fish_key = self.sprite_resource_subpath.replace(os.sep,'.')
		display_text = fish.translate(fish_key, self.label, internal_value_name) #fish.translate(self.parent.animation_engine.resource_subpath, self.label, internal_value_name)

		button = tk.Radiobutton(
		 		self.parent.spiffy_buttons_section,
		 		image=img,
		 		name="_".join([self.label.lower(), internal_value_name, "button"]),
		 		text=display_text,
		 		variable=self.var,
		 		value=internal_value_name,
		 		activebackground=self.parent.DIMENSIONS["button"]["color.active"],
		 		selectcolor=self.parent.DIMENSIONS["button"]["color.selected"],
		 		width=self.parent.DIMENSIONS["button"]["width"],
		 		height=self.parent.DIMENSIONS["button"]["height"],
		 		indicatoron=False,
		 		command=self.press_spiffy_button
		)
		if disabled:
			button.configure(state="disabled")
		bindings = None
		keypresses = None
		bindings_filename = common.get_resource(["meta","manifests"],"bindings.json")
		with open(bindings_filename,encoding="utf-8") as f:
			bindings = {}
			try:
				bindings = json.load(f)
			except JSONDecodeError as e:
				raise ValueError("Bindings Manifest malformed!")
		keypresses_switcher = bindings[self.label.lower()] if self.label.lower() in bindings else {}
		keypresses = keypresses_switcher.get(internal_value_name.lower(),None)
		if keypresses:
			for keypress in keypresses:
				button.bind_all(keypress,partial(self.invoke_spiffy_button,button))

		ToolTip(button, display_text)
		button.image = img
		button.grid(row=self.row, column=self.col)

		if not self.default_exists or default:
			button.select()
			self.press_spiffy_button()
			self.default_exists = True

		self.col += 1

	def adds(self, buttons, fish):
		for (internal_value_name, image_filename, default, disabled) in buttons:
			if internal_value_name is None and image_filename is None and default is None:
				self.add_newline()
			elif internal_value_name is None:
				self.add_blank_space()
			else:
				self.add(internal_value_name, image_filename, fish, default, disabled)

	def add_blank_space(self, amount_of_space=1):
		self.col += amount_of_space

	def add_newline(self, amount_of_space=1):
		self.col = 1
		self.row += amount_of_space
		self.parent.max_row += amount_of_space
		return amount_of_space

	def press_spiffy_button(self):
		self.get_animation_engine().update_animation()

	def invoke_spiffy_button(self, button, event=None):
		button.config(relief = tk.SUNKEN)
		button.invoke()


def main():
    print(f"Called main() on utility library {__file__}")

if __name__ == "__main__":
    main()
