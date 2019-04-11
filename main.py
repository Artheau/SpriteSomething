#originally written by Artheau
#while suffering from delusions of grandeur
#in April 2019

import os
import importlib
import json
import random
import tkinter as tk
from lib.crxtooltip import CreateToolTip
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

        left_pane = tk.PanedWindow(self, orient=tk.VERTICAL)
        panes.add(left_pane, minsize=200)
        panes.add(self._canvas)


        #########   Sprite Metadata       #############
        metadata_section = tk.Frame(left_pane)
        left_pane.add(metadata_section)
        self.right_align_grid_in_frame(metadata_section)
        row=0
        for label in ["Sprite Name","Author Name","Author Name Short"]:
            metadata_label = tk.Label(metadata_section, text=label)
            metadata_label.grid(row=row,column=1)
            metadata_input = tk.Entry(metadata_section)
            metadata_input.grid(row=row,column=2)
            row += 1
        ###############################################


        #########   Background Dropdown   #############
        background_section = tk.Frame(left_pane)
        left_pane.add(background_section)
        self.right_align_grid_in_frame(background_section)
        background_label = tk.Label(background_section, text="Background:")
        background_label.grid(row=0,column=1)
        self.background_selection = tk.StringVar(background_section)
        self.background_selection.set(self.background_name)
        background_dropdown = tk.OptionMenu(background_section, self.background_selection, *self.game.background_images)
        background_dropdown.configure(width=16)
        background_dropdown.grid(row=0,column=2)
        def change_background_dropdown(*args):
            self.load_background(self.background_selection.get())
        self.background_selection.trace('w', change_background_dropdown)  #when the dropdown is changed, run this function
        ###############################################


        ##########   Animation Dropdown   #############
        animation_section = tk.Frame(left_pane)
        left_pane.add(animation_section)
        self.right_align_grid_in_frame(animation_section)
        animation_label = tk.Label(animation_section, text="Animation:")
        animation_label.grid(row=0, column=1)
        self.animation_selection = tk.StringVar(animation_section)
        self.animation_selection.set("Watch me Nae Nae")
        animation_dropdown = tk.OptionMenu(animation_section, self.animation_selection, *["Watch me Nae Nae", "Watch me Whip"])
        animation_dropdown.configure(width=16)
        animation_dropdown.grid(row=0, column=2)
        def change_animation_dropdown(*args):
            print(f"Received instruction to change animation to {self.animation_selection.get()}")
        self.animation_selection.trace('w', change_animation_dropdown)  #when the dropdown is changed, run this function
        ###############################################



        ########### Sprite Specific Stuff #############
        sprite_section = tk.Frame(left_pane)
        left_pane.add(sprite_section)
        self.right_align_grid_in_frame(sprite_section)
        
        #TODO: Move this into the sprite specific classes so that it can be different for each sprite within a game
        if (self._game_name == "metroid3"):
            row = 0
            col = 1

            sprite_display = tk.Label(sprite_section,text="Display:")
            sprite_display.grid(row=row,column=col,columnspan=3)
            row += 1

            self.add_spiffy_buttons(sprite_section,row,col,"Suit",{"Power":1,"Varia":2,"Gravity":3},"suit"," Suit")
            row += 1
        elif(self._game_name == "zelda3"):
            row = 0
            col = 1

            sprite_display = tk.Label(sprite_section,text="Display:")
            sprite_display.grid(row=row,column=col,columnspan=6)
            row += 1

            self.add_spiffy_buttons(sprite_section,row,col,"Mail",{"Green":1,"Blue":2,"Red":3,"Bunny":4},"mail"," Mail")
            row += 1
            self.add_spiffy_buttons(sprite_section,row,col,"Sword",{"No":0,"Fighter's":1,"Master":2,"Tempered":3,"Gold":4},"sword"," Sword")
            row += 1
            self.add_spiffy_buttons(sprite_section,row,col,"Shield",{"No":0,"Fighter's":1,"Fire":2,"Mirror":3},"shield"," Shield")
            row += 1
            self.add_spiffy_buttons(sprite_section,row,col,"Gloves",{"No Gloves":0,"Power Glove":1,"Titan's Mitt":2},"gloves","")
        ###############################################



        ########### GUI Specific Stuff ################
        control_section = tk.Frame(left_pane)
        left_pane.add(control_section)
        self.right_align_grid_in_frame(control_section)
        current_grid_row = 0
        temp_label = tk.Label(control_section, text="GUI specific stuff")
        temp_label.grid(row=current_grid_row, column=1, columnspan=3)
        current_grid_row += 1
        def zoom_out(*args):
            self._current_zoom = max(0.1,self._current_zoom - 0.1)
            self.scale_background_image(self._current_zoom)
        def zoom_in(*args):
            self._current_zoom = min(3.0,self._current_zoom + 0.1)
            self.scale_background_image(self._current_zoom)

        zoom_out_button = tk.Button(control_section, text="Zoom -", command=zoom_out)
        zoom_out_button.grid(row=current_grid_row, column=2, sticky='nesw')

        zoom_in_button = tk.Button(control_section, text="Zoom +", command=zoom_in)
        zoom_in_button.grid(row=current_grid_row, column=3, sticky='nesw')
        current_grid_row += 1

        speed_down_button = tk.Button(control_section, text="Speed -")
        speed_down_button.grid(row=current_grid_row, column=2, sticky='nesw')

        speed_up_button = tk.Button(control_section, text="Speed +")
        speed_up_button.grid(row=current_grid_row, column=3, sticky='nesw')
        current_grid_row += 1

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","play.png"))
        play_button = tk.Button(control_section, image=img, text="Play", compound=tk.RIGHT)
        play_button.image = img
        play_button.grid(row=current_grid_row, column=1, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","play-once.png"))
        play_one_button = tk.Button(control_section, image=img, text="Play 1", compound=tk.RIGHT)
        play_one_button.image = img
        play_one_button.grid(row=current_grid_row, column=2, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","reset.png"))
        reset_button = tk.Button(control_section, image=img, text="Reset", compound=tk.RIGHT)
        reset_button.image = img
        reset_button.grid(row=current_grid_row, column=3, sticky='nesw')
        current_grid_row += 1

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","step-back.png"))
        step_back_button = tk.Button(control_section, image=img, text="Step", compound=tk.LEFT)
        step_back_button.image = img
        step_back_button.grid(row=current_grid_row, column=1, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","pause.png"))
        pause_button = tk.Button(control_section, image=img, text="Pause", compound=tk.RIGHT)
        pause_button.image = img
        pause_button.grid(row=current_grid_row, column=2, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","step-forward.png"))
        step_forward_button = tk.Button(control_section, image=img, text="Step", compound=tk.RIGHT)
        step_forward_button.image = img
        step_forward_button.grid(row=current_grid_row, column=3, sticky='nesw')
        ###############################################


    def create_menu_bar(self):
        #create the menu bar
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        #create the file menu
        file_menu = tk.Menu(menu, tearoff=0)
        for option in ["Open","Save","Save As..."]:
            self.add_dummy_menu_option(option,file_menu)
        file_menu.add_command(label="Exit", command=self.exit)
        #attach to the menu bar
        menu.add_cascade(label="File", menu=file_menu)

        #create the import menu
        import_menu = tk.Menu(menu, tearoff=0)
        #import sprite
        for option in ["Sprite from Game File","PNG"]:
          self.add_dummy_menu_option(option,import_menu)
        import_menu.add_separator()
        #import palette
        for option in ["GIMP Palette","YY-CHR Palette","Graphics Gale Palette"]:
          self.add_dummy_menu_option(option,import_menu)
        import_menu.add_separator()
        #import raw data
        for option in ["Raw Pixel Data","Raw Palette Data"]:
          self.add_dummy_menu_option(option,import_menu)

        #create the export menu
        export_menu = tk.Menu(menu, tearoff=0)
        #export sprite
        for option in ["Copy to new Game File","Inject into Game File","PNG"]:
          self.add_dummy_menu_option(option,export_menu)
        export_menu.add_separator()
        #export animation
        for option in ["Animation as GIF","Animation as Collage"]:
          self.add_dummy_menu_option(option,export_menu)
        export_menu.add_separator()
        #export palette
        for option in ["GIMP Palette","YY-CHR Palette","Graphics Gale Palette"]:
          self.add_dummy_menu_option(option,export_menu)
        export_menu.add_separator()
        #export tracker images for crossproduct's and derivatives
        for option in ["Tracker Images"]:
          self.add_dummy_menu_option(option,export_menu)
        export_menu.add_separator()
        #export raw data
        for option in ["Raw Pixel Data","Raw Palette Data"]:
          self.add_dummy_menu_option(option,export_menu)

        #create the convert menu
        convert_menu = tk.Menu(menu, tearoff=0)
        convert_menu.add_cascade(label="Import", menu=import_menu)
        convert_menu.add_cascade(label="Export", menu=export_menu)
        #attach to the menu bar
        menu.add_cascade(label="Convert", menu=convert_menu)

        #create the help menu
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        #attach to the menu bar
        menu.add_cascade(label="Help", menu=help_menu)

    def center_align_grid_in_frame(self, frame):
        frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
        frame.grid_columnconfigure(1000, weight=1)    #so I guess technically this just needs to be larger than the number of columns


    def right_align_grid_in_frame(self, frame):
        frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
        frame.grid_columnconfigure(1000, weight=0)    #so I guess technically this just needs to be larger than the number of columns


    def add_spiffy_buttons(self,container,row,col,section_label,items,prefix,suffix):
        #ins:
        # container: the parent widget for this button set
        # row,col: where in the parent's grid to anchor these buttons
        # section_label: What this row of buttons represents (e.g. Mail colors)
        # items: 
        # prefix: a string that begins the icon filenames corresponding to the buttons of this row
        # suffix: a string that is used in the tooltip after the identifying string (e.g. "Mail")
        spiffy_buttons = tk.Label(container,text=section_label+':')
        spiffy_buttons.grid(row=row,column=col)
        col += 1
        if prefix == "mail":
            col += 1

        for label,level in items.items():
            if level > 0:
                img = tk.PhotoImage(file=os.path.join("resources",self._game_name,"icons",prefix+'-'+str(level)+".png"))
            else:
                img = tk.PhotoImage(file=os.path.join("resources","meta","icons","no-thing.png"))
            button = tk.Button(container,image=img,text=label+suffix)
            button_tip = CreateToolTip(button,label+suffix)
            button.image = img
            button.grid(row=row,column=col)
            col += 1

    def add_dummy_menu_option(self,text,menuObject):
        menuObject.add_command(label=text, command=self.popup_NYI)

    def popup_NYI(self):
        messagebox.showinfo("Not Yet Implemented", "This DLC is not yet available")

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

        self._current_zoom = 1.0
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
            self.scale_background_image(self._current_zoom)
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

    def about(self):
        lines = ["Created by: Artheau & Mike Trethewey", "", "Based on:","Sprite Animator by Spannerisms","ZSpriteTools by Sosuke3","","Temporarily uses assets from SpriteAnimator"]
        messagebox.showinfo("About this App","\n".join(lines))

    def exit(self):
        #TODO: confirmation box
        exit()



if __name__ == "__main__":
	main()
