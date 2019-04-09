#originally written by Artheau
#while suffering from delusions of grandeur
#in April 2019

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
        panes.add(self._canvas)

        self._sprites = {}
        self._background_ID = self.set_initial_background(self._canvas, Image.open("resources/metroid3/backgrounds/title.png"))
        self._sprite_ID = self.attach_sprite(self._canvas, Image.open("resources/zelda3/backgrounds/throne.png"), (100,100))

        right = tk.Label(panes, text="right pane")
        panes.add(right,stretch="always")

        self.scale_background_image(2)

        #button example
        #show_image_button = tk.Button(self, text="Show Background", command=self.show_image)
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
        with open("resources/app_names.json") as name_file:
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

    def set_initial_background(self, canvas, background_raw_image):
        self._raw_background = background_raw_image
        self._background_image = ImageTk.PhotoImage(background_raw_image)
        return canvas.create_image(0,0,image=self._background_image,anchor=tk.NW)   #return the object ID of the background

    def scale_background_image(self,factor):
        new_size = tuple(factor*dim for dim in self._raw_background.size)
        self._background_image = ImageTk.PhotoImage(self._raw_background.resize(new_size))
        self._canvas.itemconfig(self._background_ID, image = self._background_image)

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