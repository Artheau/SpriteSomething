import tkinter as tk
import os
import base64
from io import BytesIO    #for shenanigans


def get_all_resources(desired_filename, subdir=None):
	#gets the file from overrides AND resources (returns a list of filenames)
	file_list = []
	for directory in ["overrides","resources"]:
		if subdir: directory = os.path.join(directory,subdir)
		if os.path.isdir(directory):
			for filename in os.listdir(directory):
				if filename == desired_filename:
					file_list.append(os.path.join(directory,filename))
	return file_list

def get_resource(desired_filename, subdir=None):
	#gets the file from overrides.  If not there, then from resources.
	file_list = get_all_resources(desired_filename,subdir=subdir)
	return file_list[0] if file_list else None

def gather_all_from_resource_subdirectory(subdir):
	#gathers all the filenames from a subdirectory in resources,
	# and then also throws in all the filenames from the same subdirectory in overrides
	#does not recurse
	file_list = []
	for directory in ["resources","overrides"]:
		directory = os.path.join(directory,subdir)
		if os.path.isdir(directory):
			for filename in os.listdir(directory):
				if os.path.isfile(os.path.join(directory,filename)):
					file_list.append(filename)    #just the filename, not the path, so that this overrrides correctly
	return file_list

def apply_palette(image, palette):
	if image.mode == "P":
		flat_palette = [0 for _ in range(3*256)]
		flat_palette[3:3*len(palette)+3] = [x for color in palette for x in color]
		alpha_mask = image.point(lambda x: 0 if x==0 else 255,mode="1")
		image = image.convert('RGBA')
		image.putalpha(alpha_mask)
	return image

def get_tk_image(image):
	#needed because the tkImage.PhotoImage conversion is SO slow for big images.  Like, you don't even know.
	#LET THE SHENANIGANS BEGIN
	buffered = BytesIO()
	image.save(buffered, format="GIF")
	img_str = base64.b64encode(buffered.getvalue())
	return tk.PhotoImage(data=img_str)

