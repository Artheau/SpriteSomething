#common widgets, so as to easily populate the parts of the GUI that are delegated to other classes

import weakref    #because memory leaks are stupid
import tkinter as tk
import tkinter.colorchooser as colorchooser
import json
import os
import re
import locale
from functools import partial
from source import common
from source import ssTranslate as fish

def center_align_grid_in_frame(frame):
	frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
	frame.grid_columnconfigure(1000, weight=1)    #so I guess technically this just needs to be larger than the number of columns

def right_align_grid_in_frame(frame):
	frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
	frame.grid_columnconfigure(1000, weight=0)    #so I guess technically this just needs to be larger than the number of columns

def left_align_grid_in_frame(frame):
	raise AssertionError("Alinging left in frame is not yet implemented")

def leakless_dropdown_trace(object, var_to_trace, fun_to_call):
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
	getattr(object,var_to_trace).trace('w', dropdown_wrapper(weakref.ref(object)))  #when the dropdown is changed, run this function
	dropdown_wrapper(weakref.ref(object))()      #trigger this now to initialize


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
		id = self.id
		self.id = None
		if id:
			self.widget.after_cancel(id)

	def showtip(self, event=None):
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert") #FIXME: cx,cy unused variables
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
	def __init__(self, sprite_object, parent_frame, frame_name="spiffy_buttons", align="right"):
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
		self.sprite_object = sprite_object
		self.spiffy_buttons_section = tk.Frame(parent_frame, name=frame_name)
		if align[0].lower() == 'r':   #align right
			right_align_grid_in_frame(self.spiffy_buttons_section)
		elif align[0].lower() == 'l':  #align left
			left_align_grid_in_frame(self.spiffy_buttons_section)
		else:
			center_align_grid_in_frame(self.spiffy_buttons_section)
		self.max_row = 0

	def make_new_group(self, label, independent=False):
		#make a new variable in the sprite object called "<label>_var"
		var_name = "_".join([label.lower(), "var"])
		setattr(self.sprite_object, var_name, tk.StringVar())
		new_group = SpiffyGroup(self, self.max_row, label, getattr(self.sprite_object, var_name), independent)
		self.max_row += 1
		return new_group

	def get_panel(self):
		section_height = self.max_row*self.DIMENSIONS["panel"]["height_per_button"]
		return self.spiffy_buttons_section, section_height

class SpiffyGroup():
	#not meant to be used on its own, instead use class SpiffyButtons()
	def __init__(self, parent, row, label, var, independent=False):
		label = fish.translate("section",label,os.path.join(parent.sprite_object.resource_subpath))
		self.label = label
		self.default_exists = False
		self.parent = parent
		self.independent = independent
		self.palette_labels = common.get_resource("palette-buttons.json",os.path.join(self.parent.sprite_object.resource_subpath))
		self.palette_buttons = []
		self.var = var
		self.col = 0
		self.row = row

		if self.palette_labels:
			self.palette_labels = json.load(open(self.palette_labels))

		if label and not label == "_":
			section_label = tk.Label(self.parent.spiffy_buttons_section, text=label + ':')
			section_label.grid(row=self.row, column=self.col, sticky='E')

		self.col += 1

	def add(self, internal_value_name, image_filename="blank.png", default = False):
		icon_path = common.get_resource(image_filename, os.path.join(self.parent.sprite_object.resource_subpath,"icons"))
		if icon_path is None:
			icon_path = common.get_resource(image_filename, os.path.join("meta","icons"))
		if icon_path is None:
			raise AssertionError(f"No image resource found with name {image_filename}")

		img = tk.PhotoImage(file=icon_path)

		display_text = fish.translate(self.label, internal_value_name, self.parent.sprite_object.resource_subpath)

		if self.independent and self.palette_labels:
			bgcolor = self.palette_labels[internal_value_name]["color"]
			display_text = self.palette_labels[internal_value_name]["name"]
			button = tk.Button(
				self.parent.spiffy_buttons_section,
				image=img,
				name="_".join([self.label.lower(), internal_value_name, "button"]),
				text=display_text,
				activebackground=bgcolor,
				bg=bgcolor,
				width=self.parent.DIMENSIONS["button"]["width"],
				height=self.parent.DIMENSIONS["button"]["height"],
				command=partial(self.press_color_button,(self.row * 8) + self.col)
			)
			ToolTip(button,"_".join([self.label.lower(), internal_value_name, "button"]))
			self.palette_buttons.append(button)
		else:
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
		bindings = None
		keypresses = None
		bindings_filename = common.get_resource("bindings.json","meta")
		with open(bindings_filename,encoding="utf-8") as f:
			bindings = json.load(f)
		keypresses_switcher = bindings[self.label.lower()] if self.label.lower() in bindings else {}
		keypresses = keypresses_switcher.get(internal_value_name.lower(),None)
		if keypresses:
			for keypress in keypresses:
				button.bind_all(keypress,partial(self.invoke_spiffy_button,button))

		ToolTip(button, display_text)
		button.image = img
		button.grid(row=self.row, column=self.col)

		if not self.independent:
			if not self.default_exists or default:
				button.select()
				self.press_spiffy_button()
				self.default_exists = True

		self.col += 1

	def add_blank_space(self, amount_of_space=1):
		self.col += amount_of_space

	def add_newline(self, amount_of_space=1):
		self.col = 1
		self.row += amount_of_space
		self.parent.max_row += amount_of_space
		return amount_of_space

	def press_spiffy_button(self):
		self.parent.sprite_object.update_animation()

	def press_color_button(self,index):
		color = str(colorchooser.askcolor())
		matches = re.search(r'\(([^\)]*)\)([,\s\']*)([^\']*)(.*)',color)
		if matches:
			color = matches[3]
			r = ("%x" % (int(int(color[1:3],16) / 8) * 8)).zfill(2)
			g = ("%x" % (int(int(color[3:5],16) / 8) * 8)).zfill(2)
			b = ("%x" % (int(int(color[5:7],16) / 8) * 8)).zfill(2)
			color = '#' + r + g + b
			self.palette_buttons[index-1].configure(bg=color)

	def invoke_spiffy_button(self, button, event=None):
		button.config(relief = tk.SUNKEN)
		button.invoke()
