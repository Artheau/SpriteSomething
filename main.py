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

        #create the menu bar
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        #create the file menu
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Load Sprite", command=self.popup_NYI)
        file_menu.add_command(label="Export to ROM", command=self.popup_NYI)
        file_menu.add_command(label="Exit", command=self.exit)
        #attach to the menu bar
        menu.add_cascade(label="File", menu=file_menu)

        #create the edit menu
        image_menu = tk.Menu(menu, tearoff=0)
        image_menu.add_command(label="Create GIF", command=self.popup_NYI)
        #attach to the menu bar
        menu.add_cascade(label="Image", menu=image_menu)

        #create the help menu
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=self.popup_NYI)
        #attach to the menu bar
        menu.add_cascade(label="Help", menu=help_menu)

        panes = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=1)

        #for now, just show the default picture
        self._background = self.add_background(panes)
        #self.attach_sprites(self._background)

        right = tk.Label(panes, text="right pane")
        panes.add(right,stretch="always")

        self.scale_background_image(2)


        #button example
        #show_image_button = tk.Button(self, text="Show Background", command=self.show_image)
        #show_image_button.place(x=300, y=0)

    def scale_background_image(self,factor):
        new_size = [2*x for x in self._raw_background.size]
        new_background_image = ImageTk.PhotoImage(self._raw_background.resize(new_size))
        self._background.image = new_background_image
        self._background.configure(image=new_background_image)

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
            app_name.append(f" of {suffix}")
        self.master.title("".join(app_name))

    def add_background(self, panes):
        self._raw_background = Image.open("title.png")
        background = ImageTk.PhotoImage(self._raw_background)
        background_label = tk.Label(panes, image=background)
        background_label.image = background
        panes.add(background_label)
        return background_label

    def attach_sprites(self,background):
        sprites = ImageTk.PhotoImage(file="title.png")  #eventually just put the PIL image in the parenthesis
        sprites_label = tk.Label(background, image=sprites, borderwidth=0, highlightthickness=0)
        sprites_label.image = sprites
        #sprites_label.place(x=100, y=100)


    def load(self):
        #TODO: implement loading from ROM, later expand to other formats
        pass

    def export(self):
        #TODO: implement exporting to ROM, later expand to other formats
        pass

    def create_gif(self):
        #TODO: implement this
        pass

    def about(self):
        #TODO: Open up a window with information directing the user to the website/github/wiki
        pass

    def exit(self):
        #TODO: confirmation box
        exit()



if __name__ == "__main__":
	main()