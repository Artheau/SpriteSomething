#functions that are utilities common to all GUI functionality were stored here
#do not merge them with common.py, because common.py is imported by some classes that have no GUI awareness

try:
  from tkinter import ttk, messagebox, filedialog    #for GUI stuff
  import tkinter as tk         #for GUI stuff
except ModuleNotFoundError as e:
  print(e)

import base64                #TODO: I don't know why we import this
import io                    #for BytesIO() stream.  TODO: Could probably refactor this to use bytearray instead
import json
import random
import ssl
import sys
import urllib.request
from functools import partial    #for tk debugging
from json.decoder import JSONDecodeError
from source.meta.common.constants import DEBUG_MODE  #for tk debugging
from source.meta.common import common


if ("DEBUG_MODE" in vars() or "DEBUG_MODE" in globals()) and DEBUG_MODE:     #if DEBUG_MODE exists and is set to True
    import os                     #Needed to make the tk_photo_image_wrapper

    #added this function to stop the madness with MacOS errors
    #now there should be an error generated if a PNG is sent through tk.PhotoImage
    def tk_photoimage_wrapper(old_function, *args, **kwargs):
        if "file" in kwargs and kwargs["file"]:     #if a string was passed as the file argument
            file = kwargs["file"]
            _, file_extension = os.path.splitext(file)
            if file_extension.lower() == ".png":
                # FIXME: English
                raise AssertionError(f"tk.PhotoImage was sent a PNG file: {file}")
        return old_function(args,kwargs)

    #hook this into tk
    tk.PhotoImage = partial(tk_photoimage_wrapper, tk.PhotoImage)


def get_tk_image(image):
    #needed because the tkImage.PhotoImage conversion is SO slow for big images.    Like, you don't even know.
    #LET THE SHENANIGANS BEGIN
    buffered = io.BytesIO()
    image.save(buffered, format="GIF")
    img_str = base64.b64encode(buffered.getvalue())
    return tk.PhotoImage(data=img_str)

# create chooser for game files that have multiple sprite options for extraction
def create_extraction_chooser(console_name,game_names):
    def choose_game(game_name):
        game_selector.set(game_name)
        game_chooser.destroy()

    selected_game = None

    if len(game_names) > 1:
        game_chooser = tk.Toplevel()
        # FIXME: English
        game_chooser.title("Choose Sprite to Extract")
        game_chooser.geometry("320x100")
        game_selector = tk.StringVar(game_chooser)
        game_buttons = []
        row  = 0
        col  = 0
        cols = 2
        for game_name in game_names:
            sprite_name = ""
            #FIXME: Hack for Quad Rando
            if game_name in ["metroid1","zelda1"]:
                console_name = "nes"
            elif game_name in ["metroid3","zelda3"]:
                console_name = "snes"
            with open(common.get_resource([console_name,game_name,"manifests"],"manifest.json")) as f:
                manifest = {}
                try:
                    manifest = json.load(f)
                except JSONDecodeError as e:
                    raise ValueError("Game Manifest malformed: " + game_name)
                sprite_name = manifest["1"]["name"]
            game_button = tk.Button(
                game_chooser,
                width=16,
                height=1,
                text=game_name + "/" + sprite_name,
                command=partial(choose_game,game_name)
            )
            game_button.grid(row=row,column=col,sticky=tk.NSEW)
            game_buttons.append(game_button)
            if col % cols == 0:
                row += 1
                col = 0
            else:
                col += 1
        game_chooser.grid_rowconfigure(0,weight=1)
        game_chooser.grid_rowconfigure(2,weight=1)
        game_chooser.grid_columnconfigure(0,weight=1)
        game_chooser.grid_columnconfigure(col,weight=1)
        game_chooser.wait_window()
        selected_game = game_selector.get()
    else:
        selected_game = random.choice(game_names)
    return selected_game

# create chooser for game files that have multiple sprite options for extraction
def create_sheet_chooser(console_name,game_name,sheets):
    def choose_sheet(sheet_name):
        sheet_selector.set(sheet_name)
        sheet_chooser.destroy()

    selected_sheet = None

    if len(sheets) > 1:
        sheet_chooser = tk.Toplevel()
        #FIXME: English
        sheet_chooser.title("Choose Sheet to Open")
        sheet_chooser.geometry("640x140")
        sheet_selector = tk.StringVar(sheet_chooser)
        sheet_buttons = []
        i = 1
        j = 1
        cols = 5
        for sheet_name in sheets:
            label = os.path.basename(sheet_name)
            sheet_button = tk.Button(
                sheet_chooser,
                width=16,
                height=1,
                text=label,
                command=partial(choose_sheet,sheet_name)
            )
            sheet_button.grid(row=i,column=j,sticky=tk.NSEW)
            sheet_buttons.append(sheet_button)
            if j == cols:
                i += 1
                j    = 1
            else:
                j += 1
        sheet_chooser.grid_rowconfigure(0,weight=1)
        sheet_chooser.grid_rowconfigure(cols + 2,weight=1)
        sheet_chooser.grid_columnconfigure(0,weight=1)
        sheet_chooser.grid_columnconfigure(i + 1,weight=1)
        sheet_chooser.wait_window()
        selected_sheet = sheet_selector.get()
    else:
        selected_sheet = random.choice(sheets)
    return selected_sheet

# download sprites for specified sprite manifest URL
def get_sprites(self,title,destdir,url,gui=True):
    success = False    #report success
    filepath = os.path.join('.',"resources","user",destdir)    #save to user_resources/<console_dir>/<game_dir>/<sprite_dir>/sheets/<dir>/*.zspr
    if not os.path.exists(filepath):
        os.makedirs(filepath)    #make it if we don't have it

    #make the request!
    sprites_filename = url
    context = ssl._create_unverified_context()
    sprites_req = urllib.request.urlopen(sprites_filename, context=context)
    sprites = {}
    try:
        sprites = json.loads(sprites_req.read().decode("utf-8"))
    except JSONDecodeError as e:
        raise ValueError("Downloadable sprites manifest malformed: " + sprites_filename)
    #get an iterator and a counter for a makeshift progress bar
    total = len(sprites)
    if "file" not in sprites[0]:
        total -= 1
    # FIXME: English
    print("   Downloading " + title + " Sprites")
    wintitle = "Downloading " + title + " Sprites"
    winbody = "Wait a little bit, dude, there's " + str(total) + " sprites."
    winquestion = "Are you a bad enough dude to get that many?"
    dodownload = (gui == False) or messagebox.askyesno(wintitle,winbody + "\n\n" + winquestion)
#    downloader = tk.Tk()
#    downloader.title("Downloading " + title + " Sprites")
#    dims = {
#        "window": {
#            "width": 300,
#            "height": 200
#        }
#    }
#    downloader.geometry(str(dims["window"]["width"]) + 'x' + str(dims["window"]["height"]))
#    self.progressbar = ttk.Progressbar(downloader,orient=tk.HORIZONTAL,length=100,mode="determinate")
#    self.progressbar.pack(side=tk.TOP,pady=10)
#    self.progressbar["maximum"] = total

    if dodownload:
        i = 0
        for _,sprite in enumerate(sprites):
            if "file" not in sprite:
                continue
            sprite_filename = sprite["file"][sprite["file"].rfind('/')+1:]    #get the filename
            sprite_destination = os.path.join(filepath,sprite_filename)    #set the destination
            if not os.path.exists(sprite_destination):    #if we don't have it, download it
                sprite_data_req = urllib.request.Request(
                    sprite["file"],
                    data=None,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
                    }
                )
                try:
                    sprite_data_req = urllib.request.urlopen(sprite_data_req, context=context)
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        # print("Sprite not found!")
                        pass
                    elif e.code == 403:
                        # print("Sprite not authorized!")
                        pass
                    # FIXME: English
                    print("    [%s] %s/%d: %s" % (str(e.code).ljust(len("Skipping") - 2), str(i+1).rjust(len(str(total))), total, sprite_filename))
                    i += 1
                    continue
                with open(sprite_destination, "wb") as g:
                    sprite_data = sprite_data_req.read()
                    # FIXME: English
                    print("    Writing  %s/%d: %s" % (str(i+1).rjust(len(str(total))), total, sprite_filename))
                    g.write(sprite_data)
                    success = True
            else:    #if we do have it, next!
                # FIXME: English
                print("    Skipping %s/%d: %s" % (str(i+1).rjust(len(str(total))), total, sprite_filename))
            i += 1
    #        self.progressbar["value"] = (((i+1)/total)*100)
    #    downloader.destroy()
    return success


def main():
    print(f"Called main() on utility library {__file__}")

if __name__ == "__main__":
    main()
