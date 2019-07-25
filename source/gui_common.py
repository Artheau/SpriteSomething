#functions that are utilities common to all GUI functionality were stored here
#do not merge them with common.py, because common.py is imported by some classes that have no GUI awareness

import io                	#for BytesIO() stream.  TODO: Could probably refactor this to use bytearray instead
import tkinter as tk     	#for GUI stuff
from tkinter import ttk, messagebox, filedialog	#for GUI stuff
import base64            	#TODO: I don't know why we import this
from functools import partial    #for tk debugging
from source.constants import DEBUG_MODE  #for tk debugging
from source import common


if ("DEBUG_MODE" in vars() or "DEBUG_MODE" in globals()) and DEBUG_MODE:   #if DEBUG_MODE exists and is set to True
	import os 					#Needed to make the tk_photo_image_wrapper

	#added this function to stop the madness with MacOS errors
	#now there should be an error generated if a PNG is sent through tk.PhotoImage
	def tk_photoimage_wrapper(old_function, *args, **kwargs):
		if "file" in kwargs and kwargs["file"]:   #if a string was passed as the file argument
			file = kwargs["file"]
			_, file_extension = os.path.splitext(file)
			if file_extension.lower() == ".png":
				raise AssertionError(f"tk.PhotoImage was sent a PNG file: {file}")
		return old_function(args,kwargs)

	#hook this into tk
	tk.PhotoImage = partial(tk_photoimage_wrapper, tk.PhotoImage)
	

def get_tk_image(image):
	#needed because the tkImage.PhotoImage conversion is SO slow for big images.  Like, you don't even know.
	#LET THE SHENANIGANS BEGIN
	buffered = io.BytesIO()
	image.save(buffered, format="GIF")
	img_str = base64.b64encode(buffered.getvalue())
	return tk.PhotoImage(data=img_str)
