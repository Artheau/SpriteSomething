#common widgets, so as to easily populate the parts of the GUI that are delegated to other classes

import weakref    #because memory leaks are stupid
import tkinter as tk
import os
from source import common

def center_align_grid_in_frame(frame):
	frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
	frame.grid_columnconfigure(1000, weight=1)    #so I guess technically this just needs to be larger than the number of columns


def right_align_grid_in_frame(frame):
	frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
	frame.grid_columnconfigure(1000, weight=0)    #so I guess technically this just needs to be larger than the number of columns


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
		x, y, cx, cy = self.widget.bbox("insert")
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
