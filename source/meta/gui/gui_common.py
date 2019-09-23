#functions that are utilities common to all GUI functionality were stored here
#do not merge them with common.py, because common.py is imported by some classes that have no GUI awareness

import io                	#for BytesIO() stream.  TODO: Could probably refactor this to use bytearray instead
import tkinter as tk     	#for GUI stuff
from tkinter import ttk, messagebox, filedialog	#for GUI stuff
import base64            	#TODO: I don't know why we import this
import json
import random
import urllib
from functools import partial    #for tk debugging
from source.meta.common.constants import DEBUG_MODE  #for tk debugging
from source.meta.common import common


if ("DEBUG_MODE" in vars() or "DEBUG_MODE" in globals()) and DEBUG_MODE:   #if DEBUG_MODE exists and is set to True
	import os 					#Needed to make the tk_photo_image_wrapper

	#added this function to stop the madness with MacOS errors
	#now there should be an error generated if a PNG is sent through tk.PhotoImage
	def tk_photoimage_wrapper(old_function, *args, **kwargs):
		if "file" in kwargs and kwargs["file"]:   #if a string was passed as the file argument
			file = kwargs["file"]
			_, file_extension = os.path.splitext(file)
			if file_extension.lower() == ".png":
				#FIXME: English
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

def create_chooser(game_names):
	def choose_game(game_name):
		game_selector.set(game_name)
		game_chooser.destroy()

	selected_game = None

	if len(game_names) > 1:
		game_chooser = tk.Toplevel()
		#FIXME: English
		game_chooser.title("Choose Sprite to Extract")
		game_chooser.geometry("320x100")
		game_selector = tk.StringVar(game_chooser)
		game_buttons = []
		i = 1
		for game_name in game_names:
			sprite_name = ""
			with open(common.get_resource([game_name,"manifests"],"manifest.json")) as f:
				manifest = json.load(f)
				f.close()
				sprite_name = manifest["1"]["name"]
			game_button = tk.Button(
				game_chooser,
				width=16,
				height=1,
				text=sprite_name,
				command=partial(choose_game,game_name)
			)
			game_button.grid(row=1,column=i,sticky=tk.NSEW)
			game_buttons.append(game_button)
			i += 1
		game_chooser.grid_rowconfigure(0,weight=1)
		game_chooser.grid_rowconfigure(2,weight=1)
		game_chooser.grid_columnconfigure(0,weight=1)
		game_chooser.grid_columnconfigure(i,weight=1)
		game_chooser.wait_window()
		selected_game = game_selector.get()
	else:
		selected_game = random.choice(game_names)
	return selected_game

def get_sprites(self,title,dir,url):
	success = False	#report success
	filepath = os.path.join('.',"resources","user",dir)	#save to user_resources/<game_dir>/<sprite_dir>/sheets/<dir>/*.zspr
	if not os.path.exists(filepath):
		os.makedirs(filepath)	#make it if we don't have it

	#make the request!
	sprites_filename = url
	sprites_req = urllib.request.urlopen(sprites_filename)
	sprites = json.loads(sprites_req.read().decode("utf-8"))
	#get an iterator and a counter for a makeshift progress bar
	i = 0
	total = len(sprites)
	#FIXME: English
	print("   Downloading " + title + " Sprites")
	messagebox.showwarning("Downloading " + title + " Sprites","Wait a little bit, dude, there's " + str(total) + " sprites.")
	for sprite in sprites:
		sprite_filename = sprite["file"][sprite["file"].rfind('/')+1:]	#get the filename
		sprite_destination = os.path.join(filepath,sprite_filename)	#set the destination
		i += 1	#iterate iterator
		if not os.path.exists(sprite_destination):	#if we don't have it, download it
			with open(sprite_destination, "wb") as g:
				sprite_data_req = urllib.request.Request(
					sprite["file"],
					data=None,
					headers={
						"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
					}
				)
				sprite_data_req = urllib.request.urlopen(sprite_data_req)
				sprite_data = sprite_data_req.read()
				#FIXME: English
				print("    Writing " + str(i).rjust(len(str(total))) + '/' + str(total) + ": " + sprite_filename)
				g.write(sprite_data)
				g.close()
				success = True
		else:	#if we do have it, next!
			#FIXME: English
			print("    Skipping " + str(i).rjust(len(str(total))) + '/' + str(total) + ": " + sprite_filename)
	return success
