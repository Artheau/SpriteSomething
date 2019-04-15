#originally written by Artheau
# while suffering from delusions of grandeur
#at some point a lot of content was added by Mike
# apparently he delights in delusions of grandeur
#and so my pain and his joy mixed in a constructive way
# back in April 2019

import os
import importlib
import json
import random
import re
import tkinter as tk
import webbrowser
from functools import partial
from tkinter import filedialog, messagebox, Text, ttk
from lib.crxtooltip import CreateToolTip
from lib.tkHyperlinkManager import HyperlinkManager
from lib.tkSimpleStatusBar import StatusBar
from PIL import Image, ImageTk

def main():
	root = tk.Tk()
	#window size
	root.geometry("600x480")
	root.configure(bg='#f0f0f0')
	SpriteSomethingMainFrame(root)
	root.mainloop()

class SpriteSomethingMainFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        dims = {
            "left_pane": {
                "minwidth": 200
            },
            "background_dropdown": {
                "width": 16
            },
            "animation_dropdown": {
                "width": 16
            },
            "animation_list": {
                "width": 16
            }
        }

        #set the title
        self.create_random_title()

        #main frame should take up the whole window
        self.pack(fill=tk.BOTH, expand=1)

        self.create_menu_bar()
        self._status = self.create_status_bar()

        panes = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=1)

        self._canvas = tk.Canvas(panes)

        self._sprites = {}
        self._background_ID = None

        #for now, just to prove that at least some of the features work
        self.load_game(random.choice(["zelda3", "metroid3"]))
        self.make_sprite(0x01)   #TODO: implement other sprites other than the player
        self.freeze_ray = False #freeze ray, stops time, tell your friends

        left_pane = tk.PanedWindow(self, orient=tk.VERTICAL)
        panes.add(left_pane, minsize=dims["left_pane"]["minwidth"])
        panes.add(self._canvas)


        #########   Sprite Metadata       #############
        metadata_section = tk.Frame(left_pane)
        left_pane.add(metadata_section)
        self.right_align_grid_in_frame(metadata_section)
        row = 0
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
        background_label.grid(row=0, column=1)
        self.background_selection = tk.StringVar(background_section)
        self.background_selection.set(self.background_name)
        background_keys = []
        for background_key in self.game.background_images:
            background_keys.append(background_key)
        background_dropdown = tk.ttk.Combobox(background_section, state="readonly", values=background_keys)
        background_dropdown.configure(width=dims["background_dropdown"]["width"], exportselection=0, textvariable=self.background_selection)
        background_dropdown.grid(row=0, column=2)
        def change_background_dropdown(*args):
            self.load_background(self.background_selection.get())
        self.background_selection.trace('w', change_background_dropdown)  #when the dropdown is changed, run this function
        self.background_animate = tk.IntVar()
        background_animate_check = tk.Checkbutton(background_section, text="Animate background", variable=self.background_animate)
        background_animate_check.select()
        background_animate_check.grid(row=1, column=1, sticky='E', columnspan=2)
        ###############################################


        ##########   Animation Dropdown   #############
        animation_section = tk.Frame(left_pane)
        left_pane.add(animation_section)
        self.right_align_grid_in_frame(animation_section)
        animation_label = tk.Label(animation_section, text="Animation:")
        animation_label.grid(row=0, column=1)
        self.animation_selection = tk.StringVar(animation_section)
        self.animation_selection.set(next(iter(self.sprite.animations)))   #start with the first animation
        animation_keys = []
        for animation_key in self.sprite.animations:
            animation_keys.append(animation_key)
        animation_dropdown = tk.ttk.Combobox(animation_section, state="readonly", values=animation_keys)
        animation_dropdown.configure(width=dims["animation_dropdown"]["width"], exportselection=0, textvariable=self.animation_selection)
        animation_dropdown.grid(row=0, column=2, sticky='E')
        animation_list = tk.Button(animation_section, text="As list", command=self.show_animation_list)
        animation_list.configure(width=dims["animation_list"]["width"])
        animation_list.grid(row=1, column=2, sticky='E')
        self._sprite_ID = None             #right now there is no animation
        self.animation_selection.trace('w', self.initialize_sprite_animation)  #when the dropdown is changed, run this function
        ###############################################



        ########### Sprite Specific Stuff #############
        sprite_section = tk.Frame(left_pane)
        left_pane.add(sprite_section)
        self.right_align_grid_in_frame(sprite_section)
        self.sprite_menu_buttons = {}   #a place to store the values that the pressed buttons correspond to

        #TODO: Move this into the sprite specific classes so that it can be different for each sprite within a game
        if (self._game_name == "metroid3"):
            row = 0
            col = 1

            sprite_display = tk.Label(sprite_section, text="Display:")
            sprite_display.grid(row=row, column=col, columnspan=3)
            row += 1

            self.add_spiffy_buttons(sprite_section, row, col, "Suit", {"Power":1,"Varia":2,"Gravity":3}, "suit", " Suit")
            row += 1
            self.add_spiffy_buttons(sprite_section, row, col, "Missile Port", {"No":0,"Yes":1}, "port", " Port")
        elif(self._game_name == "zelda3"):
            row = 0
            col = 1

            sprite_display = tk.Label(sprite_section, text="Display:")
            sprite_display.grid(row=row, column=col, columnspan=6)
            row += 1

            self.add_spiffy_buttons(sprite_section, row, col, "Mail", {"Green":1,"Blue":2,"Red":3,"Bunny":4}, "mail", " Mail")
            row += 1
            self.add_spiffy_buttons(sprite_section, row, col, "Sword", {"No":0,"Fighter's":1,"Master":2,"Tempered":3,"Gold":4}, "sword", " Sword")
            row += 1
            self.add_spiffy_buttons(sprite_section, row, col, "Shield", {"No":0,"Fighter's":1,"Fire":2,"Mirror":3}, "shield", " Shield")
            row += 1
            self.add_spiffy_buttons(sprite_section, row, col, "Gloves", {"No Gloves":0,"Power Glove":1,"Titan's Mitt":2}, "gloves", "")
        ###############################################



        ########### GUI Specific Stuff ################
        control_section = tk.Frame(left_pane)
        left_pane.add(control_section)
        button_width = 7
        self.zoom_factor = tk.StringVar(control_section)
        self.zoom_factor.set("x1 ")
        self.speed_factor = tk.StringVar(control_section)
        self.speed_factor.set("100%")
        self.right_align_grid_in_frame(control_section)
        current_grid_row = 0
        temp_label = tk.Label(control_section, text="GUI specific stuff")
        temp_label.grid(row=current_grid_row, column=1, columnspan=3)
        current_grid_row += 1
        def zoom_out(*args):
            self._current_zoom = max(0.1, self._current_zoom - 0.1)
            self.scale_background_image(self._current_zoom)
            self.update_sprite_animation()
            self.zoom_factor.set('x' + str(round(self._current_zoom, 1)) + ' ')
        def zoom_in(*args):
            self._current_zoom = min(3.0, self._current_zoom + 0.1)
            self.scale_background_image(self._current_zoom)
            self.update_sprite_animation()
            self.zoom_factor.set('x' + str(round(self._current_zoom, 1)) + ' ')
        def speed_down(*args):
            self._current_speed = max(0.1, self._current_speed - 0.1)
            self.speed_factor.set(str(round(self._current_speed * 100)) + '%')
        def speed_up(*args):
            self._current_speed = min(3.0, self._current_speed + 0.1)
            self.speed_factor.set(str(round(self._current_speed * 100)) + '%')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","zoom.png"))
        zoom_factor_label = tk.Label(control_section, image=img, textvariable=self.zoom_factor, compound=tk.RIGHT)
        zoom_factor_label.image = img
        zoom_factor_label.grid(row=current_grid_row, column=1, sticky='e')

        zoom_out_button = tk.Button(control_section, text="Zoom -", width=button_width, compound=tk.LEFT, command=zoom_out)
        zoom_out_button.grid(row=current_grid_row, column=2, sticky='nesw')

        zoom_in_button = tk.Button(control_section, text="Zoom +", width=button_width, compound=tk.RIGHT, command=zoom_in)
        zoom_in_button.grid(row=current_grid_row, column=3, sticky='nesw')
        current_grid_row += 1

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","speed.png"))
        speed_factor = tk.Label(control_section, image=img, textvariable=self.speed_factor, compound=tk.RIGHT)
        speed_factor.image = img
        speed_factor.grid(row=current_grid_row, column=1, sticky='e')

        speed_down_button = tk.Button(control_section, text="Speed -", width=button_width, state=tk.DISABLED, command=speed_down)
        speed_down_button.grid(row=current_grid_row, column=2, sticky='nesw')

        speed_up_button = tk.Button(control_section, text="Speed +", width=button_width, state=tk.DISABLED, command=speed_up)
        speed_up_button.grid(row=current_grid_row, column=3, sticky='nesw')
        current_grid_row += 1

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","play.png"))
        play_button = tk.Button(control_section, image=img, text="Play", width=button_width, compound=tk.RIGHT, command=self.start_global_frame_timer)
        play_button.image = img
        play_button.grid(row=current_grid_row, column=1, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","play-once.png"))
        play_one_button = tk.Button(control_section, image=img, text="Play 1", width=button_width, state=tk.DISABLED, compound=tk.RIGHT, command=self.play_once)
        play_one_button.image = img
        play_one_button.grid(row=current_grid_row, column=2, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","reset.png"))
        reset_button = tk.Button(control_section, image=img, text="Reset", width=button_width, compound=tk.RIGHT, command=self.reset_global_frame_timer)
        reset_button.image = img
        reset_button.grid(row=current_grid_row, column=3, sticky='nesw')
        current_grid_row += 1

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","step-back.png"))
        step_back_button = tk.Button(control_section, image=img, text="Step", width=button_width, compound=tk.LEFT, command=self.rewind_global_frame_timer)
        step_back_button.image = img
        step_back_button.grid(row=current_grid_row, column=1, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","pause.png"))
        pause_button = tk.Button(control_section, image=img, text="Pause", width=button_width, compound=tk.RIGHT, command=self.pause_global_frame_timer)
        pause_button.image = img
        pause_button.grid(row=current_grid_row, column=2, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","step-forward.png"))
        step_forward_button = tk.Button(control_section, image=img, text="Step", width=button_width, compound=tk.RIGHT, command=self.step_global_frame_timer)
        step_forward_button.image = img
        step_forward_button.grid(row=current_grid_row, column=3, sticky='nesw')
        ###############################################
        self._status.set(self.game.game_name)

        self.initialize_sprite_animation()        #set up the initial animation

        #and now, as the final act of setup, let us begin the march of the clock
        self.time_marches_forward()

    def time_marches_forward(self):
        FRAMERATE = 60 #Hz
        self.advance_global_frame_timer()
        if not self.freeze_ray: #stops time, tell your friends
            self.master.after(int(1000/FRAMERATE), self.time_marches_forward)


    def create_menu_bar(self):
        #create the menu bar
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        #create the file menu
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.load_sprite)
        file_menu.add_command(label="Save As...", command=self.save_sprite_as)
        file_menu.add_command(label="Exit", command=self.exit)
        #attach to the menu bar
        menu.add_cascade(label="File", menu=file_menu)

        #create the import menu
        import_menu = tk.Menu(menu, tearoff=0)
        import_menu.add_command(label="Sprite from Game File", command=self.import_from_game_file)
        import_menu.add_command(label="PNG", command=self.import_from_png)
        self.add_dummy_menu_options([""],import_menu)
        import_menu.add_command(label="GIMP Palette", command=lambda: self.import_palette("GIMP"))
        import_menu.add_command(label="YY-CHR Palette", command=lambda: self.import_palette("YY-CHR"))
        import_menu.add_command(label="Graphics Gale Palette", command=lambda: self.import_palette("Graphics Gale"))
        self.add_dummy_menu_options([""],import_menu)
        options = [
            "Raw Pixel Data",
            "Raw Palette Data"
        ]
        self.add_dummy_menu_options(options,import_menu)

        #create the export menu
        export_menu = tk.Menu(menu, tearoff=0)
        options = [
            "Copy to new Game File",
            "Inject into Game File"
        ]
        self.add_dummy_menu_options(options,export_menu)

        export_menu.add_command(label="PNG", command=self.export_png)
        self.add_dummy_menu_options([""],export_menu)
        export_menu.add_command(label="Animation as GIF", command=self.export_gif)
        export_menu.add_command(label="Animation as Collage", command=self.export_collage)
        self.add_dummy_menu_options([""],export_menu)
        export_menu.add_command(label="GIMP Palette", command=lambda: self.export_palette("GIMP"))
        export_menu.add_command(label="YY-CHR Palette", command=lambda: self.export_palette("YY-CHR"))
        export_menu.add_command(label="Graphics Gale Palette", command=lambda: self.export_palette("Graphics Gale"))

        options = [
            "",
            "Tracker Images",
            "",
            "Raw Pixel Data",
            "Raw Palette Data"
        ]
        self.add_dummy_menu_options(options,export_menu)

        #create the convert menu
        convert_menu = tk.Menu(menu, tearoff=0)
        convert_menu.add_cascade(label="Import", menu=import_menu)
        convert_menu.add_cascade(label="Export", menu=export_menu)
        #attach to the menu bar
        menu.add_cascade(label="Convert", menu=convert_menu)

        #create the plugins menu
        plugins_menu = tk.Menu(menu, tearoff=0)
        plugins_menu.add_command(label="Sheet Trawler", command=self.popup_NYI) # Z3-specific

        #create the tools menu
        tools_menu = tk.Menu(menu, tearoff=0)
        tools_menu.add_cascade(label="Plugins", menu=plugins_menu)
        #attach to the menu bar
        menu.add_cascade(label="Tools", menu=tools_menu)

        #create the help menu
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        #attach to the menu bar
        menu.add_cascade(label="Help", menu=help_menu)

    def create_status_bar(self):
        status = StatusBar(self)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        status.set("Status")
        return status

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

        dims = {
            "button": {
                "width": 20,
                "height": 20,
                "color.active": "#78C0F8",
                "color.selected": "#C0E0C0"
            }
        }

        spiffy_buttons = tk.Label(container, text=section_label + ':')
        spiffy_buttons.grid(row=row, column=col, sticky='E')
        col += 1
        if prefix == "mail":
            col += 1

        for label,level in items.items():
            imgfile = ""
            if level > 0 and label != "Yes":
                imgfile = os.path.join("resources",self._game_name,"icons",prefix+'-'+str(level)+".png")
            elif label.find("No") > -1:
                imgfile = os.path.join("resources","meta","icons","no-thing.png")
            elif label.find("Yes") > -1:
                imgfile = os.path.join("resources","meta","icons","yes-thing.png")
            img = tk.PhotoImage(file=imgfile)
            button = tk.Radiobutton(
                container,
                image=img,
                text=label+suffix,
                variable=prefix,
                value=level,
                activebackground=dims["button"]["color.active"],
                selectcolor=dims["button"]["color.selected"],
                width=dims["button"]["width"],
                height=dims["button"]["height"],
                indicatoron=False,
                command=partial(self.press_spiffy_button,prefix,level)
            )
            if col == 2 or (prefix == "mail" and level == 1):
                button.select()
                self.press_spiffy_button(prefix,level)
            CreateToolTip(button, label + suffix)
            button.image = img
            button.grid(row=row, column=col)
            col += 1

    def show_animation_list(self):
        def onFrameConfigure(canvas):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def change_animation_list_button(animation_name):
            # Use the list buttons to change the animation being painted
            # Also changes the dropdown menu to reflect the change
            self.animation_selection.set(animation_name)
            self.initialize_sprite_animation()
        animation_list = tk.Tk()
        animation_list.title("Animation List")
        animation_list_canvas = tk.Canvas(animation_list)
        animation_list_frame = tk.Frame(animation_list_canvas)
        animation_list_vscrollbar = tk.Scrollbar(animation_list, orient="vertical", command=animation_list_canvas.yview)
        animation_list_hscrollbar = tk.Scrollbar(animation_list, orient="horizontal", command=animation_list_canvas.xview)
        animation_list_canvas.configure(yscrollcommand=animation_list_vscrollbar.set)
        animation_list_canvas.configure(xscrollcommand=animation_list_hscrollbar.set)
        animation_list_vscrollbar.pack(side="right", fill="y")
        animation_list_hscrollbar.pack(side="bottom", fill="x")
        animation_list_canvas.pack(side="left", fill="both", expand=True)
        animation_list_canvas.create_window((4,4), window=animation_list_frame, anchor="nw")
        animation_list_frame.bind("<Configure>", lambda event,canvas=animation_list_canvas: onFrameConfigure(animation_list_canvas))
        row = 0
        col = 0
        stem = ""
        for animation in self.sprite.animations:
            if stem in animation and ',' in animation:
                col += 1
            else:
                if ',' in animation:
                    k = animation.rfind(',')
                    stem = animation[0:k]
                else:
                    stem = animation
                row += 1
                col = 0
            button = tk.Button(animation_list_frame, text=animation, textvariable=animation, command=partial(change_animation_list_button,animation))
            button.grid(row=row, column=col)

    def press_spiffy_button(self,prefix,level):
        #ins:
        # buttonID: This way the Sprite Class knows what we clicked
        self.sprite_menu_buttons[prefix] = level
        if hasattr(self, "_frame_number"):
            self.update_sprite_animation()

    def add_dummy_menu_option(self,text,menuObject):
        # Add menu option with junk placeholder
        #ins:
        # text: Text label for menu option
        # menuObject: Menu object to add menu option to
        menuObject.add_command(label=text, command=self.popup_NYI)

    def add_dummy_menu_options(self,options,menuObject):
        # Add array of menu options with junk placeholders
        #ins:
        # options: Array of menu options to add
        # menuObject: Menu object to add menu options to
        for option in options:
            if option != "":
                self.add_dummy_menu_option(option, menuObject)
            else:
                menuObject.add_separator()

    def add_text_link_array(self,lines,textObject):
        # Add an array of text lines, linkifying as necessary
        #ins:
        # lines: Lines of text to add
        # textObject: Text object to add lines to
        hyperlink = HyperlinkManager(textObject)
        for line in lines:
            matches = re.search(r'(.*)\[(.*)\]\((.*)\)(.*)',line)
            if matches:
                def click1(url=matches.group(3)):
                    webbrowser.open_new(url)
                textObject.insert(tk.INSERT, matches.group(1))
                textObject.insert(tk.INSERT, matches.group(2), hyperlink.add(click1))
                textObject.insert(tk.INSERT, matches.group(4))
                textObject.insert(tk.INSERT, "\n")
            else:
                textObject.insert(tk.INSERT, line + "\n")

    def popup_NYI(self):
        # This is not the method you are looking for
        messagebox.showinfo("Not Yet Implemented", "This DLC is not yet available")

    def create_random_title(self):
        # Generate a new epic random title for this application
        with open(os.path.join("resources","app_names.json")) as name_file:
            name_parts = json.load(name_file)
        app_name = []
        if random.choice([True,False]):
            app_name.append(random.choice(name_parts["prefix enchantment"]))
            app_name.append(" ")
        app_name.append("Sprite ")         #Need to have "Sprite" in the name
        app_name.append(random.choice(name_parts["nouns"]))
        if random.choice([True,False]):
            suffix = random.choice(name_parts["suffix enchantment"])
            app_name.append(f" {suffix}")
        self.app_title = "".join(app_name)
        self.master.title(self.app_title)

    def load_game(self,game_name):
        #once the identity of the game is known, call this function to do the initial class setup

        self._game_name = game_name.lower()   #no funny business with capitalization

        #establishing now the convention that the file names are the folder names
        library_name = self.get_library_name(self._game_name)
        self.game_module = importlib.import_module(library_name)

        rom_filename = self._get_sfc_filename(os.path.join("resources",self._game_name))
        meta_filename = None  #TODO

        #establishing now the convention that the class names are the first letter capitalized of the folder name
        #this line is not obvious; it is calling the appropriate Game class constructor, e.g. Zelda3 class from lib/zelda3/zelda3.py
        self.game = getattr(self.game_module, self._game_name.capitalize())(rom_filename,meta_filename)

        self._current_zoom = 1.0
        self._current_speed = 1.0
        self.background_name = random.choice(list(self.game.background_images.keys()))
        self.load_background(self.background_name)

    def make_sprite(self, sprite_number):
        #sets up the GUI and the display for a particular sprite from the current game
        # e.g. call with sprite_number 0x01 to set up the player sprite
        _, class_name = self.game.sprites[sprite_number]
        #this line is not obvious; it is calling the appropriate sprite class constructor, e.g. Z3Link class from lib/zelda3/zelda3.py
        self.sprite = getattr(self.game_module,class_name)(self.game.rom_data, self.game.meta_data)

    def get_library_name(self, game_name):
        #the libraries are dynamically loaded.  This function gives the directory and library name as a string (for import)
        return f"lib.{game_name}.{game_name}"

    def load_sprite(self):
        # Load a ZSPR
        self.sprite_filename = filedialog.askopenfile(initialdir="./", title="Select Sprite", filetypes=(("ZSPR Files","*.zspr"),))
    def save_sprite_as(self):
        # Save a ZSPR
        filedialog.asksaveasfile(initialdir="./", title="Save Sprite As...", filetypes=(("ZSPR Files","*.zspr"),))

    def import_from_game_file(self):
        # Import a ZSPR from a Game File
        filedialog.askopenfile(initialdir="./", title="Import from Game File", filetypes=(("SNES ROMs","*.sfc;*.smc"),))
    def import_from_png(self):
        # Import a ZSPR from a PNG
        filedialog.askopenfile(initialdir="./", title="Import from PNG", filetypes=(("PNGs","*.png"),))
    def import_palette(self,type):
        # Import a Palette from another source
        ftypes = ("All Files","*.*")
        if type == "GIMP":
            ftypes = ("GIMP Palettes","*.gpl")
        elif type == "Graphics Gale":
            ftypes = ("Graphics Gale Palettes","*.pal")
        elif type == "YY-CHR":
            ftypes = ("YY-CHR Palettes","*.pal")
        filedialog.askopenfile(initialdir="./", title="Import " + type + " Palette", filetypes=(ftypes,))
    def export_png(self):
        # Export ZSPR as a PNG
        filedialog.asksaveasfile(initialdir="./", title="Export PNG", filetypes=(("PNGs","*.png"),))
    def export_gif(self):
        # Export current Still or Animation as a GIF
        filedialog.asksaveasfile(initialdir="./", title="Export Animation as GIF", filetypes=(("GIFs","*.gif"),))
    def export_collage(self):
        # Export current Still or Exploded Animation as a PNG
        filedialog.asksaveasfile(initialdir="./", title="Export Animation as Collage", filetypes=(("PNGs","*.png"),))
    def export_palette(self,type):
        # Export a Palette for import into another source
        ftypes = ("All Files","*.*")
        if type == "GIMP":
            ftypes = ("GIMP Palettes","*.gpl")
        elif type == "Graphics Gale":
            ftypes = ("Graphics Gale Palettes","*.pal")
        elif type == "YY-CHR":
            ftypes = ("YY-CHR Palettes","*.pal")
        filedialog.askopenfile(initialdir="./", title="Export " + type + " Palette", filetypes=(ftypes,))


    def _get_sfc_filename(self, path):
        #for portions of the app that need a rom to work, this will look in the specified path and find the first rom it sees
        for file in os.listdir(path):
            if file.endswith(".sfc") or file.endswith(".smc"):
                return os.path.join(path, file)
        else:
            raise AssertionError(f"There is no sfc file in directory {path}")

    def load_background(self, background_name):
        #intended to be called when the user chooses a background from the dropdown menu.  This loads that background.
        if background_name in self.game.background_images:
            background_filename = self.game.background_images[background_name]
            full_path_to_background_image = os.path.join("resources",self._game_name,"backgrounds",background_filename)
            self._raw_background = Image.open(full_path_to_background_image)   #save this so it can easily be scaled later
            self._set_background(self._raw_background)
            self.scale_background_image(self._current_zoom)
        else:
            raise AssertionError(f"load_background() called with invalid background name {background_filename}")

    def _set_background(self, background_raw_image):
        #handles the funny business of converting the background to a PhotoImage, and makes sure there is only one background
        self._background_image = ImageTk.PhotoImage(background_raw_image)     #have to save this for it to display
        if self._background_ID is None:
            self._background_ID = self._canvas.create_image(0, 0, image=self._background_image, anchor=tk.NW)    #so that we can manipulate the object later
        else:
            self._canvas.itemconfig(self._background_ID, image=self._background_image)

    def scale_background_image(self,factor):
        #called by the zoom +/- buttons
        #this function is in charge of retrieving the PIL version of the background image, scaling it, and re-inserting it
        if self._background_ID is not None:   #if there is no background right now, do nothing
            new_size = tuple(int(factor*dim) for dim in self._raw_background.size)
            self._set_background(self._raw_background.resize(new_size))

    def initialize_sprite_animation(self, *args):
        #called by the animation dropdown
        self._frame_number = 0        #start out at the first frame of the animation
        self.freeze_ray = False
        self.update_sprite_animation()

    def advance_global_frame_timer(self):
        #move frame timer forward
        self._frame_number += 1
        if self._frame_number > 1e8:        #just in case someone leaves this running for, say...forever
            self._frame_number = 1e2
        self.update_sprite_animation()

    def step_global_frame_timer(self):
        #called by step radio button to pause and step forward
        self.pause_global_frame_timer()
        self.advance_global_frame_timer()

    def play_once(self):
        self.start_global_frame_timer()

    def pause_global_frame_timer(self):
        #called by pause button
        self.freeze_ray = True #stop time, tell your friends
        self.update_sprite_animation()

    def rewind_global_frame_timer(self):
        #called by step radio button to pause and step backward
        self._frame_number = max(0, self._frame_number - 1)
        self.pause_global_frame_timer()

    def start_global_frame_timer(self):
        #called by play button
        self.freeze_ray = False
        self.time_marches_forward()
        self.update_sprite_animation()

    def reset_global_frame_timer(self):
        #called by radio reset button
        self._frame_number = 0
        self.update_sprite_animation()

    def update_sprite_animation(self):
        #calls to the sprite library to get the appropriate animation, and anchors it correctly to the zoomed canvas
        #also makes sure that there are not multiple of the sprite at any given time
        if self._sprite_ID is not None:
            self._canvas.delete(self._sprite_ID)
        img, origin = self.sprite.get_sprite_frame(self.sprite.animations[self.animation_selection.get()], self._frame_number, self.sprite_menu_buttons)
        if img:
            new_size = tuple(int(self._current_zoom*dim) for dim in img.size)
            scaled_img = img.resize(new_size)
            self._sprite_ID = self._attach_sprite(self._canvas, scaled_img, tuple(self._current_zoom*(100-x) for x in origin))  #TODO: better coordinate
        else:
            self._sprite_ID = None


    def _attach_sprite(self,canvas,sprite_raw_image,location):
        sprite = ImageTk.PhotoImage(sprite_raw_image)
        ID = canvas.create_image(location[0], location[1], image=sprite, anchor = tk.NW)
        self._sprite_image = sprite     #if you skip this part, then the auto-destructor will get rid of your picture!
        return ID

    def about(self):
        # Credit where credit's due
        dims = {
            "window": {
                "width": 300,
                "height": 200
            },
            "textarea.characters": {
                "width": 60,
                "height": 100
            }
        }
        def txtEvent(event):
            return "break"
        lines = [
                  "Created by:",
                  "",
                  "Artheau & Mike Trethewey",
                  "",
                  "",
                  "Based on:",
                  "[SpriteAnimator](http://github.com/spannerisms/SpriteAnimator) by Spannerisms",
                  "[ZSpriteTools](http://github.com/sosuke3/ZSpriteTools) by Sosuke3",
                  "",
                  "Temporarily uses assets from SpriteAnimator"
        ]
        about = tk.Tk()
        about.title(f"About {self.app_title}")
        about.geometry(str(dims["window"]["width"]) + 'x' + str(dims["window"]["height"]))
        about.resizable(tk.FALSE,tk.FALSE)
        about.attributes("-toolwindow", 1)
        text = Text(about, bg='#f0f0f0', font='TkDefaultFont', width=dims["textarea.characters"]["width"], height=dims["textarea.characters"]["height"])
        text.pack()
        text.config(cursor="arrow")
        self.add_text_link_array(lines, text)
        text.bind("<Button-1>", lambda e: txtEvent(e))

    def exit(self):
        exit_confirm = messagebox.askyesno(self.app_title, "Are you sure you want to exit?")
        if exit_confirm:
            save_before_exit = messagebox.askyesno(self.app_title, "Do you want to save before exiting?")
            if save_before_exit:
                self.save_sprite_as()
            else:
                messagebox.showwarning(self.app_title, "Death in Super Metroid loses progress since last save." + "\n" + "You have been eaten by a grue.")
                exit()



if __name__ == "__main__":
	main()
