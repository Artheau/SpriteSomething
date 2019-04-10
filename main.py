#originally written by Artheau
#while suffering from delusions of grandeur
#in April 2019

import os
import importlib
import json
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def main():
	root = tk.Tk()
	#window size
	root.geometry("600x480")
	app = SpriteSomethingMainFrame(root)
	root.mainloop()

class SpriteSomethingMainFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        
        #set the title
        self.create_random_title()
        
        #main frame should take up the whole window
        self.pack(fill=tk.BOTH, expand=1)

        self.create_menu_bar()

        panes = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=1)

        self._canvas = tk.Canvas(panes)

        self._sprites = {}
        self._background_ID = None

        #for now, just to prove that at least some of the features work
        self.load_game(random.choice(["zelda3","metroid3"]))

        
        #self._sprite_ID = self.attach_sprite(self._canvas, Image.open(os.path.join("resources","zelda3","backgrounds","throne.png"), (100,100))

        left_pane = tk.Frame(panes)
        panes.add(left_pane, minsize=200)
        panes.add(self._canvas)


        left_pane.grid_rowconfigure(0, minsize=32)   #give a little space between the menu and the control panel
        current_grid_row = 1

        #########   Background Dropdown   #############
        background_label = tk.Label(left_pane, text="Background:")
        background_label.grid(row=current_grid_row,column=0)
        self.background_selection = tk.StringVar(left_pane)
        self.background_selection.set(self.background_name)
        background_dropdown = tk.OptionMenu(left_pane, self.background_selection, *self.game.background_images)
        background_dropdown.configure(width=16)
        background_dropdown.grid(row=current_grid_row,column=1)
        def change_background_dropdown(*args):
            self.load_background(self.background_selection.get())
        self.background_selection.trace('w', change_background_dropdown)  #when the dropdown is changed, run this function
        current_grid_row += 1
        ###############################################


        ##########   Animation Dropdown   #############
        animation_label = tk.Label(left_pane, text="Animation:")
        animation_label.grid(row=current_grid_row, column=0)
        self.animation_selection = tk.StringVar(left_pane)
        self.animation_selection.set("Watch me Nae Nae")
        animation_dropdown = tk.OptionMenu(left_pane, self.animation_selection, *["Watch me Nae Nae", "Watch me Whip"])
        animation_dropdown.configure(width=16)
        animation_dropdown.grid(row=current_grid_row, column=1)
        def change_animation_dropdown(*args):
            print(f"Received instruction to change animation to {self.animation_selection.get()}")
        self.animation_selection.trace('w', change_animation_dropdown)  #when the dropdown is changed, run this function
        current_grid_row += 1
        ###############################################



        ########### Sprite Specific Stuff #############
        for _,text in enumerate(["Sprite specific stuff", "over several", "rows"]):
            sprite_temp_label = tk.Label(left_pane, text=text)
            sprite_temp_label.grid(row=current_grid_row, column=0, columnspan=2)
            current_grid_row += 1
        for j,text in enumerate(["With", "Buttons"]):
            temp_button = tk.Button(left_pane, text=text)
            temp_button.grid(row=current_grid_row, column=j)
        current_grid_row += 1
        ###############################################



        ########### GUI Specific Stuff ################
        self._current_zoom = 1
        temp_label = tk.Label(left_pane, text="GUI specific stuff")
        temp_label.grid(row=current_grid_row, column=0, columnspan=2)
        current_grid_row += 1
        def zoom_out(*args):
            self._current_zoom = max(0.1,self._current_zoom - 0.1)
            self.scale_background_image(self._current_zoom)
        def zoom_in(*args):
            self._current_zoom = min(3.0,self._current_zoom + 0.1)
            self.scale_background_image(self._current_zoom)
        
        zoom_out_button = tk.Button(left_pane, text="Zoom Out", command=zoom_out)
        zoom_out_button.grid(row=current_grid_row, column=0)
        zoom_in_button = tk.Button(left_pane, text="Zoom In", command=zoom_in)
        zoom_in_button.grid(row=current_grid_row, column=1)
        ###############################################



        #show_iself.mage_button = tk.Button(self, text="Show Background", command=self.show_image)
        #show_image_button.place(x=300, y=0)


    def create_menu_bar(self):
        #create the menu bar
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        #create the file menu
        file_menu = tk.Menu(menu, tearoff=0)
        for option in ["Open","Save","Save As..."]:
            self.addDummyMenuOption(option,file_menu)
        file_menu.add_command(label="Exit", command=self.exit)
        #attach to the menu bar
        menu.add_cascade(label="File", menu=file_menu)

        #create the import menu
        import_menu = tk.Menu(menu, tearoff=0)
        #import sprite
        for option in ["Sprite from Game File","PNG"]:
          self.addDummyMenuOption(option,import_menu)
        import_menu.add_separator()
        #import palette
        for option in ["GIMP Palette","YY-CHR Palette","Graphics Gale Palette"]:
          self.addDummyMenuOption(option,import_menu)
        import_menu.add_separator()
        #import raw data
        for option in ["Raw Pixel Data","Raw Palette Data"]:
          self.addDummyMenuOption(option,import_menu)

        #create the export menu
        export_menu = tk.Menu(menu, tearoff=0)
        #export sprite
        for option in ["Copy to new Game File","Inject into Game File","PNG"]:
          self.addDummyMenuOption(option,export_menu)
        export_menu.add_separator()
        #export animation
        for option in ["Animation as GIF","Animation as Collage"]:
          self.addDummyMenuOption(option,export_menu)
        export_menu.add_separator()
        #export palette
        for option in ["GIMP Palette","YY-CHR Palette","Graphics Gale Palette"]:
          self.addDummyMenuOption(option,export_menu)
        export_menu.add_separator()
        #export tracker images for crossproduct's and derivatives
        for option in ["Tracker Images"]:
          self.addDummyMenuOption(option,export_menu)
        export_menu.add_separator()
        #export raw data
        for option in ["Raw Pixel Data","Raw Palette Data"]:
          self.addDummyMenuOption(option,export_menu)

        #create the convert menu
        convert_menu = tk.Menu(menu, tearoff=0)
        convert_menu.add_cascade(label="Import", menu=import_menu)
        convert_menu.add_cascade(label="Export", menu=export_menu)
        #attach to the menu bar
        menu.add_cascade(label="Convert", menu=convert_menu)

        #create the help menu
        help_menu = tk.Menu(menu, tearoff=0)
        for option in ["About"]:
          self.addDummyMenuOption(option,help_menu)
        #attach to the menu bar
        menu.add_cascade(label="Help", menu=help_menu)

    def addDummyMenuOption(self,text,menuObject):
        menuObject.add_command(label=text, command=self.popup_NYI)

    def popup_NYI(self):
        messagebox.showinfo("Not Implemented", "This feature is not yet implemented")

    def create_random_title(self):
        with open(os.path.join("resources","app_names.json")) as name_file:
            name_parts = json.load(name_file)
        app_name = []
        if random.choice([True,False]):
            app_name.append(random.choice(name_parts["prefix enchantment"]))
        app_name.append(" Sprite ")         #Need to have "Sprite" in the name
        app_name.append(random.choice(name_parts["nouns"]))
        if random.choice([True,False]):
            suffix = random.choice(name_parts["suffix enchantment"])
            app_name.append(f" {suffix}")
        self.master.title("".join(app_name))

    def load_game(self,game_name):
        game_name = game_name.lower()   #no funny business with capitalization
        self._game_name = game_name

        #establishing now the convention that the file names are the folder names
        library_name = f"lib.{game_name}.{game_name}"                    
        library_module = importlib.import_module(library_name)

        rom_filename = self._get_sfc_filename(os.path.join("resources",game_name))
        meta_filename = None  #TODO

        #establishing now the convention that the class names are the first letter capitalized of the folder name
        #this line is not obvious; it is calling the appropriate Game class constructor, e.g. Zelda3 class from lib/zelda3/zelda3.py
        self.game = getattr(library_module, game_name.capitalize())(rom_filename,meta_filename)

        self.background_name = random.choice(list(self.game.background_images.keys()))
        self.load_background(self.background_name)

    def _get_sfc_filename(self, path):
        for file in os.listdir(path):
            if file.endswith(".sfc") or file.endswith(".smc"):
                return os.path.join(path, file)
        else:
            raise AssertionError(f"There is no sfc file in directory {path}")

    def load_background(self, background_name):
        if background_name in self.game.background_images:
            background_filename = self.game.background_images[background_name]
            full_path_to_background_image = os.path.join("resources",self._game_name,"backgrounds",background_filename)
            self._raw_background = Image.open(full_path_to_background_image)   #save this so it can easily be scaled later
            self._set_background(self._raw_background)
        else:
            raise AssertionError(f"load_background() called with invalid background name {background_filename}")

    def _set_background(self, background_raw_image):
        self._background_image = ImageTk.PhotoImage(background_raw_image)     #have to save this for it to display
        if self._background_ID is None:
            self._background_ID = self._canvas.create_image(0,0,image=self._background_image,anchor=tk.NW)    #so that we can manipulate the object later
        else:
            self._canvas.itemconfig(self._background_ID, image=self._background_image)

    def scale_background_image(self,factor):
        if self._background_ID is not None:   #if there is no background right now, do nothing
            new_size = tuple(int(factor*dim) for dim in self._raw_background.size)
            self._set_background(self._raw_background.resize(new_size))
        
    def attach_sprite(self,canvas,sprite_raw_image,location):
        sprite = ImageTk.PhotoImage(sprite_raw_image)
        ID = canvas.create_image(location[0], location[1],image=sprite, anchor = tk.NW)
        self._sprites[ID] = sprite     #if you skip this part, then the auto-destructor will get rid of your picture!
        return ID


    def exit(self):
        #TODO: confirmation box
        exit()



if __name__ == "__main__":
	main()