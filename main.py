#originally written by Artheau
# while suffering from delusions of grandeur
#at some point a lot of content was added by Mike
# apparently he delights in delusions of grandeur
#and so my pain and his joy mixed in a constructive way
# back in April 2019

import os
import argparse
import importlib
import lib.constants as CONST
import json
import random
import re
import tkinter as tk
import webbrowser
import numpy as np
from lib.RomHandler import util
from functools import partial
from tkinter import colorchooser, filedialog, messagebox, Text, ttk
from lib.crxtooltip import CreateToolTip
from lib.tkHyperlinkManager import HyperlinkManager
from lib.tkSimpleStatusBar import StatusBar
from PIL import Image, ImageTk

def main():
    command_line_args = process_command_line_args()
    
    root = tk.Tk()
    #window size
    root.geometry("800x600")
    root.configure(bg='#f0f0f0')
    SpriteSomethingMainFrame(root, command_line_args["game"])
    root.mainloop()

def process_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game",
                        dest="game",
                        help="Which game to start in (e.g. 'metroid3')",
                        metavar="<game_name>",
                        default='zelda3')

    command_line_args = vars(parser.parse_args())
    return command_line_args

class SpriteSomethingMainFrame(tk.Frame):
    def __init__(self, master=None, starting_game="zelda3"):
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

        panes = tk.PanedWindow(self, orient=tk.HORIZONTAL, name="two_columns")
        panes.pack(fill=tk.BOTH, expand=1)

        self._canvas = tk.Canvas(panes, name="right_pane")

        self._sprites = {}
        self._background_ID = None

        self.load_game(starting_game)

        self.create_menu_bar(self._game_name)
        self._status = self.create_status_bar()

        self.make_sprite(0x01)   #TODO: implement other sprites other than the player
        self.freeze_ray = False #freeze ray, stops time, tell your friends

        left_pane = tk.PanedWindow(self, orient=tk.VERTICAL, name="left_pane")
        panes.add(left_pane, minsize=dims["left_pane"]["minwidth"])
        panes.add(self._canvas)


        #########   Sprite Metadata       #############
        # Gui.class
        # print_sprite_metadata()
        metadata_section = tk.Frame(left_pane, name="metadata_section")
        left_pane.add(metadata_section)
        self.right_align_grid_in_frame(metadata_section)
        row = 0
        for label in ["Sprite Name","Author Name","Author Name Short"]:
            metadata_label = tk.Label(metadata_section, text=label, name=label.lower().replace(' ', '_'))
            metadata_label.grid(row=row,column=1)
            metadata_input = tk.Entry(metadata_section, name=label.lower().replace(' ', '_') + "_input")
            metadata_input.grid(row=row,column=2)
            row += 1
        ###############################################


        #########   Background Dropdown   #############
        # Gui.class, populated by Game.class
        background_section = tk.Frame(left_pane, name="background_section")
        left_pane.add(background_section)
        self.right_align_grid_in_frame(background_section)
        background_label = tk.Label(background_section, text="Background:")
        background_label.grid(row=0, column=1)
        self.background_selection = tk.StringVar(background_section)
        self.background_selection.set(self.background_name)
        background_keys = []
        for background_key in self.game.background_images:
            background_keys.append(background_key)
        background_dropdown = tk.ttk.Combobox(background_section, state="readonly", values=background_keys, name="background_dropdown")
        background_dropdown.configure(width=dims["background_dropdown"]["width"], exportselection=0, textvariable=self.background_selection)
        background_dropdown.grid(row=0, column=2)
        def change_background_dropdown(*args):
            self.load_background(self.background_selection.get())
        self.background_selection.trace('w', change_background_dropdown)  #when the dropdown is changed, run this function
        self.background_animate = tk.IntVar()
        background_animate_check = tk.Checkbutton(background_section, text="Animate background", variable=self.background_animate, name="background_animate_check")
        background_animate_check.select()
        background_animate_check.grid(row=1, column=1, sticky='E', columnspan=2)
        ###############################################


        ##########   Animation Dropdown   #############
        # Gui.class, populated by Game.Sprite.class
        animation_section = tk.Frame(left_pane, name="animation_section")
        left_pane.add(animation_section)
        self.right_align_grid_in_frame(animation_section)
        animation_label = tk.Label(animation_section, text="Animation:")
        animation_label.grid(row=0, column=1)
        self.animation_selection = tk.StringVar(animation_section)
        self.animation_selection.set(next(iter(self.sprite.animations)))   #start with the first animation
        animation_keys = []
        for animation_key in self.sprite.animations:
            animation_keys.append(animation_key)
        animation_dropdown = tk.ttk.Combobox(animation_section, state="readonly", values=animation_keys, name="animation_dropdown")
        animation_dropdown.configure(width=dims["animation_dropdown"]["width"], exportselection=0, textvariable=self.animation_selection)
        animation_dropdown.grid(row=0, column=2, sticky='E')
        animation_list = tk.Button(animation_section, text="As list", command=self.show_animation_list, name="animation_list")
        animation_list.configure(width=dims["animation_list"]["width"])
        animation_list.grid(row=1, column=2, sticky='E')
        self._sprite_ID = None             #right now there is no animation
        self.animation_selection.trace('w', self.initialize_sprite_animation)  #when the dropdown is changed, run this function
        ###############################################



        ########### Sprite Specific Stuff #############
        # Game.Sprite.class
        # print_knobs_and_buttons()
        sprite_section = tk.Frame(left_pane, name="sprite_section")
        left_pane.add(sprite_section)
        self.right_align_grid_in_frame(sprite_section)
        self.button_values = {}   #a place to store the values that the pressed buttons correspond to
        self.buttons = {}
        self.buttons["palette"] = []
        bgcolors = {}

        palette_section = tk.Frame(left_pane, name="palette_section")
        left_pane.add(palette_section)
        self.right_align_grid_in_frame(palette_section)

        #TODO: Move this into the sprite specific classes so that it can be different for each sprite within a game
        if (self._game_name == "metroid3"):
            # Metroid3.class, M3Samus.class
            row = 0
            col = 1

            sprite_display = tk.Label(sprite_section, text="Display:")
            sprite_display.grid(row=row, column=col, columnspan=3)
            row += 1

            self.add_spiffy_buttons(sprite_section, row, col, "Suit", {"Power":1,"Varia":2,"Gravity":3}, "suit", " Suit")
            row += 1
            self.add_spiffy_buttons(sprite_section, row, col, "Cannon Port", {"No":0,"Yes":1}, "port", " Port")

            bgcolors = {
                "Transparent": "#000000",
                "Suit Lining (Dark)": "#404000",
                "Body (Bright)": "#E8E800",
                "Outline": "#280028",
                "Visor": "#00F870",
                "Metal (Dark)": "#406840",
                "Glint/Sparkle/Shine": "#F8E0A8",
                "Metal (Brightest)": "#90B090",
                "Metal (Bright)": "#709070",
                "Head (Brightest)": "#D82800",
                "Body (Normal)": "#A8A800",
                "Body (Dark)": "#585800",
                "Suit Lining (Normal)": "#A09800",
                "Metal (Darkest)": "#204020",
                "Head (Bright)": "#A01800",
                "Head (Normal)": "#680000"
            }
        elif(self._game_name == "zelda3"):
            # Zelda3.class, Z3Link.class
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
            row += 1

            bgcolors = {
                "Transparent": "#000000",
                "Eyes": "#F8F8F8",
                "Belt": "#F0D840",
                "Skin (Dark)": "#B86820",
                "Skin (Light)": "#F0A068",
                "Outline": "#282828",
                "Hat Trim": "#F87800",
                "Mouth": "#C01820",
                "Hair": "#E860B0",
                "Tunic (Dark)": "#389068",
                "Tunic (Light)": "#40D870",
                "Hat (Dark)": "#509010",
                "Hat (Light)": "#78B820",
                "Hands": "#E09050",
                "Sleeves": "#885828",
                "Water Ripples": "#C080F0"
            }

        for i in range(len(bgcolors)):
            img = tk.PhotoImage(file=os.path.join("resources","meta","icons","transparent.png"))
            label = list(bgcolors.keys())[i]
            bgcolor = list(bgcolors.values())[i]
            button = tk.Button(palette_section,image=img,text=i,name="palette_section_colorpicker_"+str(i),width=20,height=20,bg=bgcolor,command=partial(self.press_color_button,i))
            button.image = img
            button.label = label
            self.buttons["palette"].append(button)
        i = 1
        for color in self.buttons["palette"]:
            CreateToolTip(color,color.label)
            color.grid(row=row,column=i+1)
            i += 1
            if i == 8 + 1:
                row += 1
                i = 1
        ###############################################



        ########### GUI Specific Stuff ################
        # Gui.class
        # print_vcr_controls()
        control_section = tk.Frame(left_pane, name="vcr_controls_section")
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

        speed_down_button = tk.Button(control_section, text="Speed -", width=button_width, command=speed_down)
        speed_down_button.grid(row=current_grid_row, column=2, sticky='nesw')

        speed_up_button = tk.Button(control_section, text="Speed +", width=button_width, command=speed_up)
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
        step_back_button = tk.Button(control_section, image=img, text="Frame", width=button_width, compound=tk.LEFT, command=self.rewind_global_frame_timer)
        step_back_button.image = img
        step_back_button.grid(row=current_grid_row, column=1, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","pause.png"))
        pause_button = tk.Button(control_section, image=img, text="Pause", width=button_width, compound=tk.RIGHT, command=self.pause_global_frame_timer)
        pause_button.image = img
        pause_button.grid(row=current_grid_row, column=2, sticky='nesw')

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","step-forward.png"))
        step_forward_button = tk.Button(control_section, image=img, text="Frame", width=button_width, compound=tk.RIGHT, command=self.step_global_frame_timer)
        step_forward_button.image = img
        step_forward_button.grid(row=current_grid_row, column=3, sticky='nesw')
        current_grid_row += 1

        if self._game_name == "metroid3":
            img = tk.PhotoImage(file=os.path.join("resources","meta","icons","step-back.png"))
            step_back_button = tk.Button(control_section, image=img, text="Pose", width=button_width, compound=tk.LEFT, command=self.rewind_global_pose_timer)
            step_back_button.image = img
            step_back_button.grid(row=current_grid_row, column=1, sticky='nesw')

            img = tk.PhotoImage(file=os.path.join("resources","meta","icons","step-forward.png"))
            step_forward_button = tk.Button(control_section, image=img, text="Pose", width=button_width, compound=tk.RIGHT, command=self.step_global_pose_timer)
            step_forward_button.image = img
            step_forward_button.grid(row=current_grid_row, column=3, sticky='nesw')

        ###############################################

        self._status.set(self.game.game_name + ': "' + self.game.sprites[0x01][0] + '"')

        self.initialize_sprite_animation()        #set up the initial animation

        #and now, as the final act of setup, let us begin the march of the clock
        self._ready_for_next_frame = True     #gating mechanism to handle display lag
        self._stutter_frame = False           #gating mechanism to handle display lag
        self.time_marches_forward()

    def time_marches_forward(self):
        FRAME_SPEED = 1000/60 #to simulate 60 Hz
        if self._ready_for_next_frame:
            self._ready_for_next_frame = False
            if not self.freeze_ray: #stops time, tell your friends
                self.master.after(int(FRAME_SPEED/self._current_speed), self.time_marches_forward)
            self.advance_global_frame_timer()
            self._ready_for_next_frame = True
            if self._stutter_frame:
                self._stutter_frame = False
                self.master.after(int(FRAME_SPEED/self._current_speed), self.time_marches_forward)
        else:
            self._stutter_frame = True
        

    def create_menu_bar(self, game_name):
        #create the menu bar
        menu = tk.Menu(self.master, name="menu_bar")
        self.master.configure(menu=menu)

        #create the file menu
        file_menu = tk.Menu(menu, tearoff=0, name="file_menu")
        file_menu.images = {}

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","open.png"))
        file_menu.images["open"] = img
        file_menu.add_command(label="Open", image=file_menu.images["open"], compound=tk.LEFT, command=self.load_sprite)

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","save.png"))
        file_menu.images["save"] = img
        file_menu.add_command(label="Save As...", image=file_menu.images["save"], compound=tk.LEFT, command=self.save_sprite_as)

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","exit.png"))
        file_menu.images["exit"] = img
        file_menu.add_command(label="Exit", image=file_menu.images["exit"], compound=tk.LEFT, command=self.exit)
        #attach to the menu bar
        menu.add_cascade(label="File", menu=file_menu)

        #create the import menu
        import_menu = tk.Menu(menu, tearoff=0, name="import_menu")
        import_menu.images = {}

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","extract.png"))
        import_menu.images["import-sfc"] = img
        import_menu.add_command(label="Sprite from Game File", image=import_menu.images["import-sfc"], compound=tk.LEFT, command=self.import_from_game_file)

        import_menu.add_command(label="PNG", command=self.import_from_png)

        self.add_dummy_menu_options([""],import_menu)

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","gimp.png"))
        import_menu.images["import-gimp"] = img
        import_menu.add_command(label="GIMP Palette", image=import_menu.images["import-gimp"], compound=tk.LEFT, command=lambda: self.import_palette("GIMP"))

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","yy-chr.png"))
        import_menu.images["import-yy-chr"] = img
        import_menu.add_command(label="YY-CHR Palette", image=import_menu.images["import-yy-chr"], compound=tk.LEFT, command=lambda: self.import_palette("YY-CHR"))

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","gale.png"))
        import_menu.images["import-gale"] = img
        import_menu.add_command(label="Graphics Gale Palette", image=import_menu.images["import-gale"], compound=tk.LEFT, command=lambda: self.import_palette("Graphics Gale"))

        self.add_dummy_menu_options([""],import_menu)

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","import-pixels.png"))
        import_menu.images["import-pixels"] = img
        import_menu.add_command(label="Raw Pixel Data", image=import_menu.images["import-pixels"], compound=tk.LEFT, command=self.load_sprite)

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","import-palette.png"))
        import_menu.images["import-palette"] = img
        import_menu.add_command(label="Raw Palette Data", image=import_menu.images["import-palette"], compound=tk.LEFT, command=self.load_sprite)

        #create the export menu
        export_menu = tk.Menu(menu, tearoff=0, name="export_menu")
        export_menu.images = {}

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","inject-new.png"))
        export_menu.images["export-sfc-new"] = img
        export_menu.add_command(label="Copy to new Game File", image=export_menu.images["export-sfc-new"], compound=tk.LEFT, command=self.import_from_game_file)

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","inject.png"))
        export_menu.images["export-sfc"] = img
        export_menu.add_command(label="Inject into Game File", image=export_menu.images["export-sfc"], compound=tk.LEFT, command=self.import_from_game_file)

        export_menu.add_command(label="PNG", command=self.export_png)
        self.add_dummy_menu_options([""],export_menu)
        export_menu.add_command(label="Animation as GIF", command=self.export_gif)
        export_menu.add_command(label="Animation as Collage", command=self.export_collage)
        self.add_dummy_menu_options([""],export_menu)

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","gimp.png"))
        export_menu.images["export-gimp"] = img
        export_menu.add_command(label="GIMP Palette", image=export_menu.images["export-gimp"], compound=tk.LEFT, command=lambda: self.export_palette("GIMP"))

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","yy-chr.png"))
        export_menu.images["export-yy-chr"] = img
        export_menu.add_command(label="YY-CHR Palette", image=export_menu.images["export-yy-chr"], compound=tk.LEFT, command=lambda: self.export_palette("YY-CHR"))

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","gale.png"))
        export_menu.images["export-gale"] = img
        export_menu.add_command(label="Graphics Gale Palette", image=export_menu.images["export-gale"], compound=tk.LEFT, command=lambda: self.export_palette("Graphics Gale"))

        options = [
            "",
            "Tracker Images",
            "",
        ]
        self.add_dummy_menu_options(options,export_menu)

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","export-pixels.png"))
        export_menu.images["export-pixels"] = img
        export_menu.add_command(label="Raw Pixel Data", image=export_menu.images["export-pixels"], compound=tk.LEFT, command=self.load_sprite)

        img = tk.PhotoImage(file=os.path.join("resources","meta","icons","export-palette.png"))
        export_menu.images["export-palette"] = img
        export_menu.add_command(label="Raw Palette Data", image=export_menu.images["export-palette"], compound=tk.LEFT, command=self.load_sprite)

        #create the convert menu
        convert_menu = tk.Menu(menu, tearoff=0, name="convert_menu")
        convert_menu.add_cascade(label="Import", menu=import_menu)
        convert_menu.add_cascade(label="Export", menu=export_menu)
        #attach to the menu bar
        menu.add_cascade(label="Convert", menu=convert_menu)

        #create the plugins menu
        plugins_menu = tk.Menu(menu, tearoff=0, name="plugins_menu")
        if game_name == "zelda3":
            plugins_menu.add_command(label="Sheet Trawler", command=self.popup_NYI)
        else:
            plugins_menu.add_command(label="None", state="disabled")

        #create the tools menu
        tools_menu = tk.Menu(menu, tearoff=0, name="tools_menu")
        tools_menu.add_cascade(label="Plugins", menu=plugins_menu)
        #attach to the menu bar
        menu.add_cascade(label="Tools", menu=tools_menu)

        #create the help menu
        help_menu = tk.Menu(menu, tearoff=0, name="help_menu")
        help_menu.add_command(label="About", command=self.about)
        #attach to the menu bar
        menu.add_cascade(label="Help", menu=help_menu)

    def create_status_bar(self):
        # Gui.class
        status = StatusBar(self)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        status.set("Status")
        return status

    def center_align_grid_in_frame(self, frame):
        # Gui.class
        frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
        frame.grid_columnconfigure(1000, weight=1)    #so I guess technically this just needs to be larger than the number of columns


    def right_align_grid_in_frame(self, frame):
        # Gui.class
        frame.grid_columnconfigure(0, weight=1)       #the 0th column will be the margin
        frame.grid_columnconfigure(1000, weight=0)    #so I guess technically this just needs to be larger than the number of columns


    def add_spiffy_buttons(self,container,row,col,section_label,items,prefix,suffix):
        # Gui.class
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
        self.buttons[prefix] = {}
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
                name=prefix + str(level) + "_button",
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
            self.buttons[prefix][level] = button
            button.grid(row=row, column=col)
            col += 1

    def show_animation_list(self):
        # Gui.class
        def onFrameConfigure(canvas):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def change_animation_list_button(animation_name):
            # Use the list buttons to change the animation being painted
            # Also changes the dropdown menu to reflect the change
            self.animation_selection.set(animation_name)
            self.initialize_sprite_animation()
        animation_list = tk.Tk()
        animation_list.title("Animation List")
        animation_list_canvas = tk.Canvas(animation_list, name="animation_list_canvas")
        animation_list_frame = tk.Frame(animation_list_canvas, name="animation_list_frame")
        animation_list_vscrollbar = tk.Scrollbar(animation_list, orient="vertical", command=animation_list_canvas.yview, name="animation_list_vscroll")
        animation_list_hscrollbar = tk.Scrollbar(animation_list, orient="horizontal", command=animation_list_canvas.xview, name="animation_list_hscroll")
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

    def press_color_button(self,index):
        color = tk.colorchooser.askcolor()
        self.buttons["palette"][index].configure(bg=str(color)[-9:])

    def press_spiffy_button(self,prefix,level):
        # Gui.class
        #ins:
        # buttonID: This way the Sprite Class knows what we clicked
        self.button_values[prefix] = level
        if prefix == "mail" or prefix == "suit":
            bgcolors = []
            if prefix == "mail":
                bgcolors = [
                    ["#000000","#F8F8F8","#F0D840","#B86820","#F0A068","#282828","#F87800","#C01820","#E860B0","#389068","#40D870","#509010","#78B820","#E09050","#C86020","#C080F0"],
                    ["#000000","#F8F8F8","#F0D840","#B86820","#F0A068","#282828","#F87800","#C01820","#E860B0","#0060D0","#88A0E8","#C0A048","#F8D880","#E09050","#C86020","#C080F0"],
                    ["#000000","#F8F8F8","#F0D840","#B86820","#F0A068","#282828","#F87800","#C01820","#E860B0","#B81020","#F05888","#9878D8","#C8A8F8","#E09050","#C86020","#C080F0"],
                    ["#000000","#F8F8F8","#F0D840","#B86820","#F0A068","#282828","#F87800","#C01820","#E860B0","#389068","#40D870","#509010","#78B820","#F098A8","#901830","#C080F0"]
                ]
            elif prefix == "suit":
                bgcolors = [
                    ["#000000","#404000","#E8E800","#280028","#00F870","#406840","#F8E0A8","#90B090","#709070","#D82800","#A8A800","#585800","#A09800","#204020","#A01800","#680000"],
                    ["#000000","#404000","#F8B800","#280028","#00F870","#406840","#F8E0A8","#90B090","#709070","#D82800","#F06800","#702000","#A09800","#204020","#A01800","#680000"],
                    ["#000000","#404000","#F88080","#280028","#00F870","#406840","#F8E0A8","#90B090","#709070","#D82800","#A040B0","#502860","#A09800","#204020","#A01800","#680000"]
                ]

            colors = bgcolors[int(level)-1]
            if "palette" in self.buttons:
                for i in range(len(self.buttons["palette"])):
                    color = colors[i]
                    self.buttons["palette"][i].configure(bg=color)
        if hasattr(self, "_frame_number"):
            self.update_sprite_animation()

    def add_dummy_menu_option(self,text,menuObject):
        # Gui.class
        # Add menu option with junk placeholder
        #ins:
        # text: Text label for menu option
        # menuObject: Menu object to add menu option to
        menuObject.add_command(label=text, command=self.popup_NYI)

    def add_dummy_menu_options(self,options,menuObject):
        # Gui.class
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
        # Gui.class
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
        # Gui.class
        # This is not the method you are looking for
        messagebox.showinfo("Not Yet Implemented", "This DLC is not yet available")

    def create_random_title(self):
        # Gui.class
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
        # Game.class
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
        # Gui.class
        #sets up the GUI and the display for a particular sprite from the current game
        # e.g. call with sprite_number 0x01 to set up the player sprite
        _, class_name = self.game.sprites[sprite_number]
        #this line is not obvious; it is calling the appropriate sprite class constructor, e.g. Z3Link class from lib/zelda3/zelda3.py
        self.sprite = getattr(self.game_module,class_name)(self.game.rom_data, self.game.meta_data)

    def get_library_name(self, game_name):
        # Gui.class
        #the libraries are dynamically loaded.  This function gives the directory and library name as a string (for import)
        return f"lib.{game_name}.{game_name}"

    def load_sprite(self):
        # Gui.class, refs ZSPR.class
        # Load a ZSPR
        self.sprite_filename = filedialog.askopenfile(initialdir="./", title="Select Sprite", filetypes=(("ZSPR Files","*.zspr"),))
    def save_sprite_as(self):
        # Gui.class, refs ZSPR.class
        # Save a ZSPR
        filedialog.asksaveasfile(initialdir="./", title="Save Sprite As...", filetypes=(("ZSPR Files","*.zspr"),))

    def import_from_game_file(self):
        # Gui.class, refs ZSPR.class
        # Import a ZSPR from a Game File
        filedialog.askopenfile(initialdir="./", title="Import from Game File", filetypes=(("SNES ROMs","*.sfc;*.smc"),))
    def import_from_png(self):
        # Gui.class, refs PNG.class
        # Import a ZSPR from a PNG
        filedialog.askopenfile(initialdir="./", title="Import from PNG", filetypes=(("PNGs","*.png"),))
    def import_palette(self,type):
        # Gui.class, refs Palette.class
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
        # Gui.class, refs PNG.class
        # Export ZSPR as a PNG
        filedialog.asksaveasfile(initialdir="./", title="Export PNG", filetypes=(("PNGs","*.png"),))
    def export_gif(self):
        # Gui.class, refs GIF.class
        # Export current Still or Animation as a GIF
        filedialog.asksaveasfile(initialdir="./", title="Export Animation as GIF", filetypes=(("GIFs","*.gif"),))
    def export_collage(self):
        # Gui.class, refs PNG.class
        # Export current Still or Exploded Animation as a PNG
        filedialog.asksaveasfile(initialdir="./", title="Export Animation as Collage", filetypes=(("PNGs","*.png"),))
    def export_palette(self,type):
        # Gui.class, refs Palette.class
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
        # Game.class
        #for portions of the app that need a rom to work, this will look in the specified path and find the first rom it sees
        for file in os.listdir(path):
            if file.endswith(".sfc") or file.endswith(".smc"):
                return os.path.join(path, file)
        else:
            raise AssertionError(f"There is no sfc file in directory {path}")

    def load_background(self, background_name):
        # Gui.class
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
        # Gui.class
        #handles the funny business of converting the background to a PhotoImage, and makes sure there is only one background
        self._background_image = ImageTk.PhotoImage(background_raw_image)     #have to save this for it to display
        if self._background_ID is None:
            self._background_ID = self._canvas.create_image(0, 0, image=self._background_image, anchor=tk.NW)    #so that we can manipulate the object later
        else:
            self._canvas.itemconfig(self._background_ID, image=self._background_image)

    def scale_background_image(self,factor):
        # Gui.class
        #called by the zoom +/- buttons
        #this function is in charge of retrieving the PIL version of the background image, scaling it, and re-inserting it
        if self._background_ID is not None:   #if there is no background right now, do nothing
            new_size = tuple(int(factor*dim) for dim in self._raw_background.size)
            self._set_background(self._raw_background.resize(new_size))

    def initialize_sprite_animation(self, *args):
        # Gui.class
        #called by the animation dropdown
        self._frame_number = 0        #start out at the first frame of the animation
        self.freeze_ray = False
        self.update_sprite_animation()

    def advance_global_frame_timer(self):
        # Gui.class
        #move frame timer forward
        self._frame_number += 1
        if self._frame_number > 1e8:        #just in case someone leaves this running for, say...forever
            self._frame_number = 1e2
        self.update_sprite_animation()

    def step_global_frame_timer(self):
        # Gui.class
        #called by step radio button to pause and step forward
        self.pause_global_frame_timer()
        self.advance_global_frame_timer()

    def step_global_pose_timer(self):
        # Gui.class
        pass

    def play_once(self):
        # Gui.class
        self.start_global_frame_timer()

    def pause_global_frame_timer(self):
        # Gui.class
        #called by pause button
        self.freeze_ray = True #stops time, tell your friends
        self.update_sprite_animation()

    def rewind_global_frame_timer(self):
        # Gui.class
        #called by step radio button to pause and step backward
        self._frame_number = max(0, self._frame_number - 1)
        self.pause_global_frame_timer()

    def rewind_global_pose_timer(self):
        # Gui.class
        pass

    def start_global_frame_timer(self):
        # Gui.class
        #called by play button
        if self.freeze_ray:
            self.freeze_ray = False
            self.time_marches_forward()
            self.update_sprite_animation()

    def reset_global_frame_timer(self):
        # Gui.class
        #called by radio reset button
        self._frame_number = 0
        self.update_sprite_animation()

    def update_sprite_animation(self):
        # Gui.class, refs Game.Sprite.class
        #calls to the sprite library to get the appropriate animation, and anchors it correctly to the zoomed canvas
        #also makes sure that there are not multiple of the sprite at any given time
        if self._sprite_ID is not None:
            self._canvas.delete(self._sprite_ID)
        animation_ID = self.sprite.animations[self.animation_selection.get()]
        img, origin = self.sprite.get_sprite_pose(animation_ID, self.sprite.get_pose_number_from_frame_number(animation_ID, self._frame_number))
        if img:
            palette = self.sprite.get_sprite_palette_from_buttons(self.button_values, self._frame_number)
            img = util.apply_palette(img, palette)
            new_size = tuple(int(self._current_zoom*dim) for dim in img.size)
            scaled_img = img.resize(new_size)
            self._sprite_ID = self._attach_sprite(self._canvas, scaled_img, tuple(self._current_zoom*(100-x) for x in origin))  #TODO: better coordinate
        else:
            self._sprite_ID = None


    def _attach_sprite(self,canvas,sprite_raw_image,location):
        # Gui.class
        sprite = ImageTk.PhotoImage(sprite_raw_image)
        ID = canvas.create_image(location[0], location[1], image=sprite, anchor = tk.NW)
        self._sprite_image = sprite     #if you skip this part, then the auto-destructor will get rid of your picture!
        return ID

    def about(self):
        # Gui.class
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
                  "SpriteSomething v" + CONST.APP_VERSION,
                  "",
                  "Created by:",
                  "Artheau & Mike Trethewey",
                  "",
                  "Based on:",
                  "[SpriteAnimator](http://github.com/spannerisms/SpriteAnimator) by Spannerisms",
                  "[ZSpriteTools](http://github.com/sosuke3/ZSpriteTools) by Sosuke3",
                  "",
                  "Temporarily uses assets from SpriteAnimator"
                  # Assets from ZSpriteTools used with permission
        ]
        about = tk.Tk()
        about.title(f"About {self.app_title}")
        about.geometry(str(dims["window"]["width"]) + 'x' + str(dims["window"]["height"]))
        about.resizable(tk.FALSE,tk.FALSE)
        about.attributes("-toolwindow", 1)
        text = Text(about, bg='#f0f0f0', font='TkDefaultFont', width=dims["textarea.characters"]["width"], height=dims["textarea.characters"]["height"])
        text.pack()
        text.configure(cursor="arrow")
        self.add_text_link_array(lines, text)
        text.bind("<Button-1>", lambda e: txtEvent(e))

    def exit(self):
        save_before_exit = messagebox.askyesnocancel(self.app_title,"Do you want to save before exiting?")
        if save_before_exit != None:
            if save_before_exit:
                self.save_sprite_as()
            else:
                messagebox.showwarning(self.app_title, "Death in Super Metroid loses progress since last save." + "\n" + "You have been eaten by a grue.")
            exit()

if __name__ == "__main__":
    main()
