#functions that are utilities common to all GUI functionality were stored here
#do not merge them with common.py, because common.py is imported by some classes that have no GUI awareness

import io                	#for BytesIO() stream.  TODO: Could probably refactor this to use bytearray instead
import tkinter as tk     	#for GUI stuff
import base64            	#TODO: I don't know why we import this
from source import common

def get_tk_image(image):
	#needed because the tkImage.PhotoImage conversion is SO slow for big images.  Like, you don't even know.
	#LET THE SHENANIGANS BEGIN
	buffered = io.BytesIO()
	image.save(buffered, format="GIF")
	img_str = base64.b64encode(buffered.getvalue())
	return tk.PhotoImage(data=img_str)
