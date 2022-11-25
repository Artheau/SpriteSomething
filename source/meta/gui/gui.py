import tkinter as tk                            #for GUI stuff
from tkinter import ttk, messagebox, filedialog #for GUI stuff
import random                                   #for choosing random app titles
import json                                     #for reading JSON
import re                                       #for regexes in hyperlinks in about box
import traceback                                #for error reporting
import os                                       #for filesystem manipulation
import stat                                     #for filesystem manipulation
import sys                                      #for filesystem manipulation
import time                                     #for timekeeping
import urllib                                   #for getting latest version number from GitHub Pages
import webbrowser                               #for launching browser from about box
from functools import partial                   #for passing parameters to user-triggered function calls
from PIL import Image,ImageTk                   #for converting PNG to formats that tk can use
from source.meta.gui import widgetlib
from source.meta import ssDiagnostics as diagnostics
from source.meta.gui import gamelib
from source.meta.common import constants as CONST
from source.meta.ssTranslate import BabelFish
from source.meta.tkHyperlinkManager import HyperlinkManager
from source.meta.gui.tkSimpleStatusBar import StatusBar
from source.meta.common import common
from source.meta.gui import gui_common
from source.snes.zelda3.link.plugin.trawler import sheet_trawler

# make base GUI window
def make_GUI(command_line_args):
  root = tk.Tk()

  # get icon
  root.tk.call('wm','iconphoto',root._w,tk.PhotoImage(file=common.get_resource(["meta","icons"],'app.gif')))

  # set window attributes
  root.geometry("900x768")       #window size
  root.configure(bg='#f0f0f0')   #background color
  main_frame = SpriteSomethingMainFrame(root, command_line_args)
  root.protocol("WM_DELETE_WINDOW", main_frame.exit)           #intercept when the user clicks the X

  # generic error message
  def show_error(self, exception, message, callstack):
    # FIXME: English
    if exception.__name__.upper() == "NOTIMPLEMENTEDERROR":
      messagebox.showerror(   "Not Yet Implemented",
                  "This function is not yet implemented\n\n" + str(message)  )
    else:
      messagebox.showerror(   "FATAL ERROR",
                  f"While running, encountered fatal error:\n\n" +
                  f"{exception.__name__.upper()}\n" +
                  f"{str(message)}\n"+
                  f"{traceback.format_exc()}"
                  )
  tk.Tk.report_callback_exception = show_error     #tie this in so we see errors when they happen

  root.mainloop()

# build main window
class SpriteSomethingMainFrame(tk.Frame):
  def __init__(self, master, command_line_args):
    super().__init__(master)   #make the frame itself

    #set default working dirs to same dir as script
    self.working_dirs = {
      "file.open": "./",
      "file.save": "./",
      "export.dest": "./",
      "export.source": "./",
      "export.sprite-as-rdc": "./",
      "export.frame-as-png": "./",
      "export.animation-as-gif": "./",
      "export.animation-as-hcollage": "./",
      "export.animation-as-vcollage": "./"
    }
    #read saved working dirs file if it exists and set these
    working_dir_path = os.path.join(".","resources","user","meta","manifests","working_dirs.json")
    if os.path.exists(working_dir_path):
      with open(working_dir_path) as json_file:
        data = json.load(json_file)
        for k,v in data.items():
          self.working_dirs[k] = v

    #set default animation settings
    self.ani_settings = {}
    #read saved animation settings
    ani_settings_path = os.path.join(".","resources","user","meta","manifests","ani_settings.json")
    if os.path.exists(ani_settings_path):
      with open(ani_settings_path) as json_file:
        data = json.load(json_file)
        for console in data.keys():
          if console not in self.ani_settings:
            self.ani_settings[console] = {}
          for game in data[console]:
            if game not in self.ani_settings[console]:
              self.ani_settings[console][game] = {}
            for sprite,animation in data[console][game].items():
              if sprite not in self.ani_settings[console][game]:
                self.ani_settings[console][game][sprite] = 0
              self.ani_settings[console][game][sprite] = animation

    #create a fish
    self.fish = BabelFish(subpath=["meta"],lang=command_line_args["lang"] if "lang" in command_line_args else None)

    self.create_random_title()

    #build and add toolbar
    self.create_toolbar()

    self.pack(fill=tk.BOTH, expand=1)    #main frame should take up the whole window

    # add menu bar
    self.create_menu_bar()

    # add panes
    self.panes = tk.PanedWindow(self, orient=tk.HORIZONTAL, name="two_columns")
    self.panes.pack(fill=tk.BOTH, expand=1)

    # load sprite and populate stuff
    self.load_sprite(command_line_args["sprite"])

    self.unsaved_changes = False   #used to determine if we need to badger the user when they change things and try to exit

  def create_random_title(self):
    # Generate a new epic random title for this application
    name_dict = {}
    for filename in common.get_all_resources(["meta","manifests"],"app_names.json"):
      with open(filename) as name_file:
        for key,item in json.load(name_file).items():
          if not key == "$schema":
            if key in name_dict:
              name_dict[key].extend(item)
            else:
              name_dict[key] = item
    app_name = []
    if "pre" in name_dict and random.choice([True,False]):
      app_name.append(random.choice(name_dict["pre"]))
    app_name.append("Sprite")         #Need to have "Sprite" in the name
    if "noun" in name_dict:
      app_name.append(random.choice(name_dict["noun"]))
    if "post" in name_dict and random.choice([True,False]):
      app_name.append(random.choice(name_dict["post"]))
    self.app_title = " ".join(app_name)
    self.master.title(self.app_title)

  #create a toolbar
  def create_toolbar(self):
    toolbar = tk.Frame(self.master, bd=1, relief=tk.RAISED)
    #create a toolbar button
    # Inbound:
    #  fish_key: Main key for translation
    #  fish_subkey: Subkey for translation
    #  image_filename: Image to use, default to blank
    #  command: Command to associate with button, default to None
    def create_toolbar_button(fish_key, fish_subkey, image_filename=None, command=None):
      icon_path = common.get_resource(["meta","icons"],image_filename if image_filename is not None else "blank.png")
      img = ImageTk.PhotoImage(Image.open(icon_path)) if icon_path else None
      display_text = self.fish.translate("meta",fish_key,fish_subkey)
      button = tk.Button(toolbar,image=img,relief=tk.FLAT,width=16,height=16,command=command,state="disabled" if command is None else "normal")
      button.img = img
      widgetlib.ToolTip(button,display_text)
      button.pack(side=tk.LEFT,padx=2,pady=2)
      return button

    def create_toolbar_buttons(toolbar_buttons):
      for (fish_keys,image_filename,command) in toolbar_buttons:
        create_toolbar_button(fish_keys[0],fish_keys[1],image_filename,command)

    toolbar.pack(side=tk.TOP,fill=tk.X)
    toolbar_buttons = [
      (["menu","file.open"],"open.png",self.open_file), #File -> Open
      (["menu","file.save"],"save.png",self.save_file_as), #File -> Save
      (["menu","export.inject"],"inject.png",self.inject_into_ROM), #Export -> Inject
      (["menu","export.inject-new"],"inject-new.png",self.copy_into_ROM) #Export -> Inject Copy
    ]
    create_toolbar_buttons(toolbar_buttons)

  def create_cascade(self, name, internal_name, options_list, parent_menu=None):
    #options_list must be a list of 3-tuples containing
    # Display Name
    # image name (without the .png extension)
    # function to call
    if parent_menu is None:
      parent_menu = self.menu
    cascade = tk.Menu(parent_menu, tearoff=0, name=internal_name)
    cascade.images = {}
    for display_name,image_name,function_to_call in options_list:
      if (display_name,image_name,function_to_call) == (None,None,None):
        cascade.add_separator()
      else:
        if image_name:
          image_filename = (f"{image_name}")
          image_filename += ".gif" if "gif" in image_filename else ".png"
          image_path = os.path.join("meta","icons")
          if "game_plugins" in internal_name:
            image_path = os.path.join(self.game.resource_subpath,"icons")
          if "sprite_plugins" in internal_name:
            image_path = os.path.join(self.sprite.resource_subpath,"icons")
          if common.get_resource(image_path,image_filename) is not None:
            with Image.open(common.get_resource(image_path,image_filename)) as img:
              cascade.images[image_name] = ImageTk.PhotoImage(img)
          else:
            cascade.images[image_name] = None
        else:
          cascade.images[image_name] = None
        cascade.add_command(label=display_name, image=cascade.images[image_name], compound=tk.LEFT, command=function_to_call, state="disabled" if function_to_call is None else "normal")
    parent_menu.add_cascade(label=name, menu=cascade)
    return cascade

  def create_menu_bar(self):
    #create the menu bar
    self.menu = tk.Menu(self.master, name="menu_bar")
    self.master.configure(menu=self.menu)

    menu_options = []

    #create the file menu
    file_menu = self.create_cascade(self.fish.translate("meta","menu","file"), "file_menu",
                      [
                          (self.fish.translate("meta","menu","file.open"),"open",self.open_file),
                          (self.fish.translate("meta","menu","file.save"),"save",self.save_file_as),
                          (self.fish.translate("meta","menu","file.exit"),"exit",self.exit),
                      ])
    menu_options.append(file_menu)

    #create the export menu
    export_menu = self.create_cascade(self.fish.translate("meta","menu","export"),"export_menu",
                      [
                          (self.fish.translate("meta","menu","export.inject"),"inject",self.inject_into_ROM),
                          (self.fish.translate("meta","menu","export.inject-new"),"inject-new",self.copy_into_ROM),
                          (self.fish.translate("meta","menu","export.inject-bulk"),"inject-bulk",self.inject_into_ROM_bulk),
                          (None,None,None),
                          (self.fish.translate("meta","menu","export.frame-as-png"),"frame-as-png",self.export_frame_as_png),
                          (self.fish.translate("meta","menu","export.animation-as-gif"),"animation-as-gif",self.export_animation_as_gif),
                          (self.fish.translate("meta","menu","export.animation-as-hcollage"),"animation-as-hcollage",partial(self.export_animation_as_collage,"horizontal")),
                          #(self.fish.translate("meta","menu","export.animation-as-vcollage"),"animation-as-vcollage",None),#partial(self.export_animation_as_collage,"vertical")),
                          (None,None,None),
                          (self.fish.translate("meta","menu","export.palette-gimp"),"palette-gimp",partial(self.export_palette,"gimp")),
                          (self.fish.translate("meta","menu","export.palette-jasc"),"palette-jasc",partial(self.export_palette,"jasc")),
                          (self.fish.translate("meta","menu","export.palette-pdn"),"palette-pdn",partial(self.export_palette,"pdn")),
                          (self.fish.translate("meta","menu","export.palette-tileshop"),"palette-tileshop",partial(self.export_palette,"tileshop")),
                      ])
    menu_options.append(export_menu)

    # try to get bundled sprites and add menu options to load them instead of requiring the user to hunt for them
    bundled_games = {}
    not_consoles = []
    with open(os.path.join("resources","app","meta","manifests","not_consoles.json")) as f:
      not_consoles = json.load(f)
    root = os.path.join("resources","app")
    for console in os.listdir(root):
      if not console in not_consoles:
        if os.path.isdir(os.path.join(root,console)):
          if not console in bundled_games:
            bundled_games[console] = {}
          for gamedir in os.listdir(os.path.join(root,console)):
            if os.path.isdir(os.path.join(root,console,gamedir)):
              with open(os.path.join(root,console,gamedir,"lang","en.json")) as en_lang:
                en = json.load(en_lang)
                if "game" in en:
                  if "name" in en["game"]:
                    bundled_games[console][gamedir] = {}
                    bundled_games[console][gamedir]["game"] = {}
                    bundled_games[console][gamedir]["game"]["internal name"] = gamedir
                    bundled_games[console][gamedir]["game"]["name"] = en["game"]["name"]
                    bundled_games[console][gamedir]["sprites"] = []
              with open(os.path.join(root,console,gamedir,"manifests","manifest.json")) as game_manifest:
                sprites = json.load(game_manifest)
                for spriteID,sprite in sprites.items():
                  if spriteID != "$schema":
                    name = sprite["name"]
                    folder = sprite["folder name"]
                    path = os.path.join(root,console,gamedir,folder,"sheets")
                    filename = ""
                    for filetype in [".rdc",".zspr",".png"]:
                      filepath = os.path.join(path,folder+filetype)
                      if os.path.isfile(filepath):
                        filename = filepath
                    bundled_games[console][gamedir]["sprites"].append((name,partial(self.load_sprite,filename)))
    bundle_menu = tk.Menu(self.menu, tearoff=0, name="bundle_menu")
    for console in bundled_games:
      bundled_console = bundled_games[console]
      bundled_console_menu = tk.Menu(bundle_menu, tearoff=0, name="bundled_" + console + "_menu")
      for bundled_game in bundled_console:
        bundled_game = bundled_games[console][bundled_game]
        bundled_game_menu = tk.Menu(bundled_console_menu, tearoff=0, name="bundled_" + bundled_game["game"]["internal name"] + "_menu")
        for sprite in bundled_game["sprites"]:
          label,command = sprite
          bundled_game_menu.add_command(label=label,command=command)
        bundled_console_menu.add_cascade(label=bundled_game["game"]["name"], menu=bundled_game_menu)
      bundle_menu.add_cascade(label=self.fish.translate("meta","consoles",console), menu=bundled_console_menu)
    self.menu.add_cascade(label=self.fish.translate("meta","menu","bundle"), menu=bundle_menu)

    #for future implementation
    representative_images_menu = tk.Menu(self.menu, tearoff=0, name="representative_images_menu")
    plugins_menu = tk.Menu(self.menu, tearoff=0, name="plugins_menu")
    tools_menu = tk.Menu(self.menu, tearoff=0, name="tools_menu")
    tools_menu.add_command(label=self.fish.translate("meta","menu","tools.palette-editor"),command=None,state="disabled")
    tools_menu.add_command(label=self.fish.translate("meta","menu","tools.sheet-trawler"),command=sheet_trawler)
    tools_menu.add_cascade(label=self.fish.translate("meta","menu","tools.get-representative-image"), menu=representative_images_menu)
    tools_menu.add_cascade(label=self.fish.translate("meta","menu","plugins"), menu=plugins_menu)
    self.menu.add_cascade(label=self.fish.translate("meta","menu","tools"), menu=tools_menu)

    help_menu = self.create_cascade(self.fish.translate("meta","menu","help"),"help_menu",
                      [
                          (self.fish.translate("meta","menu","help.open-project-website"),None,self.open_project_website),
                          (self.fish.translate("meta","menu","help.open-project-repository"),None,self.open_project_repository),
                          (self.fish.translate("meta","menu","help.open-project-wiki"),None,self.open_project_wiki),
                          (self.fish.translate("meta","menu","help.check-for-updates"),None,self.check_for_updates),
                          (self.fish.translate("meta","menu","help.diagnostics"),"help-diagnostics",self.diagnostics),
                          (self.fish.translate("meta","menu","help.about"),"app",self.about),
                      ])
    menu_options.append(help_menu)


  #load plugins
  def load_plugins(self):
    self.menu.children["representative_images_menu"] = tk.Menu(self.menu, tearoff=0, name="representative_images_menu")

    # FIXME: English
    self.menu.children["representative_images_menu"].add_command(label="Default",command=partial(self.get_representative_images,"default"))
    for manifest_file in common.get_all_resources([self.sprite.resource_subpath,"manifests"],"representative-images.json"):
      with open(manifest_file) as manifest:
        manifest_images = json.load(manifest)
        for key in manifest_images.keys():
          if not key == "default":
            self.menu.children["representative_images_menu"].add_command(label=key[0].upper() + key[1:],command=partial(self.get_representative_images,key))

    self.menu.children["plugins_menu"] = tk.Menu(self.menu, tearoff=0, name="plugins_menu")

    #if we've got Game plugins or Sprite plugins
    if self.game.has_plugins or self.sprite.has_plugins:
      plugins_container = []
      #if we've got Game plugins, start the menu
      if self.game.has_plugins:
        #add the commands
        commands = []
        for label, icon, command in self.game.plugins.get_plugins():
          commands.append((label,icon,command))
        game_plugins_menu = self.create_cascade(self.fish.translate("meta","menu","plugins.game"),"game_plugins_menu",commands,self.menu.children["plugins_menu"])
        plugins_container.append(game_plugins_menu)

      #if we've got Sprite plugins
      if self.sprite.has_plugins:
        #add the commands
        commands = []
        for label, icon, command in self.sprite.plugins.get_plugins():
          commands.append((label,icon,command))
        sprite_plugins_menu = self.create_cascade(self.fish.translate("meta","menu","plugins.sprite"),"sprite_plugins_menu",commands,self.menu.children["plugins_menu"])
        plugins_container.append(sprite_plugins_menu)
    else:
      #if we got nothin', say as such
      self.menu.children["plugins_menu"].add_command(label=self.fish.translate("meta","meta","none"),state="disabled")

  #load sprite
  # Inbound:
  #  sprite_filename: Filename of sprite to load
  def load_sprite(self, sprite_filename):
    self.game, self.sprite, self.animation_engine = gamelib.autodetect(sprite_filename)
    self.fish.add_translation_file(os.path.join(self.game.console_name,self.game.internal_name))
    self.fish.add_translation_file(os.path.join(self.sprite.resource_subpath))
    # print("Loading sprite, setting origin to [100,100]")
    self.coord_setter((100,100))        #an arbitrary default
    self.attach_both_panels()            #remake the GUI panels
    self.load_plugins()
    self.initialize_sprite_animation()

  def attach_both_panels(self):
    #this same function can also be used to re-create the panels
    #have to make the canvas before the buttons so that the left panel buttons can manipulate it
    self.freeze_ray = True # stops time, tell your friends; do not update the sprite while doing this
    if hasattr(self, "timer_callback"):
      self.master.after_cancel(self.timer_callback)
    if hasattr(self, "left_panel"):
      for widget in self.left_panel.winfo_children():
        #if we've got direction buttons
        if "direction_buttons" in widget.winfo_name():
          #get the main bindings file
          bindings = None
          bindings_filename = common.get_resource(["meta","manifests"],"bindings.json")
          with open(bindings_filename,encoding="utf-8") as f:
            bindings = json.load(f)
          #cycle through all spiffy buttons
          for subwidget in widget.winfo_children():
            if "_button" in subwidget.winfo_name():
              button_name = subwidget.winfo_name().replace("_button","")
              button_section = button_name[:button_name.find("_")]
              button_name = button_name[button_name.find("_")+1:]
              keypresses = None
              keypresses_switcher = bindings[button_section] if button_section in bindings else {}
              keypresses = keypresses_switcher.get(button_name.lower(),None)
              if keypresses:
                #nuke all the bindings from orbit
                for keypress in keypresses:
                  subwidget.unbind_all(keypress)
                #nuke this button from orbit
                subwidget.destroy()
    self.left_panel = tk.PanedWindow(self.panes, orient=tk.VERTICAL, name="left_panel",width=320,handlesize=0,sashwidth=0,sashpad=2)
    self.right_panel = ttk.Notebook(self.panes, name="right_pane")
    self.canvas = tk.Canvas(self.right_panel, name="main_canvas")
    self.overview_frame = tk.Frame(self.right_panel, name="overview_frame")
    self.overview_canvas = tk.Canvas(self.overview_frame, name="overview_canvas")
    self.attach_left_panel()
    self.attach_right_panel()
    self.create_status_bar()

  def attach_left_panel(self):
    #this same function can also be used to re-create the panel
    BUTTON_HEIGHT = 26
    vcr_controls = self.get_vcr_controls()  #have to do this early so that their values are available for other buttons
    self.left_panel.add(self.get_reload_button(),height=1 * BUTTON_HEIGHT)
    self.attach_metadata_panel()
    self.game.attach_background_panel(self.left_panel,self.canvas,self.zoom_getter,self.frame_getter,self.fish)
    self.animation_engine.attach_animation_panel(self.left_panel,self.canvas,self.overview_canvas,self.zoom_getter,self.frame_getter,self.coord_getter,self.coord_setter,self.fish)
    #get animation engine handle
    ani_eng = self.animation_engine
    #get console internal name
    c = self.game.console_name
    #get game internal name
    g = self.game.internal_name
    #get sprite internal name
    s = self.sprite.internal_name
    if c in self.ani_settings:
      if g in self.ani_settings[c]:
        if s in self.ani_settings[c][g]:
          #get animation name
          #get background name
          #get facing direction name
          #get aiming direction name
          ani_name = self.ani_settings[c][g][s]["animation_name"] if "animation_name" in self.ani_settings[c][g][s] else ""
          bg_name = self.ani_settings[c][g][s]["background_name"] if "background_name" in self.ani_settings[c][g][s] else ""
          fac_dir = self.ani_settings[c][g][s]["facing_var"] if "facing_var" in self.ani_settings[c][g][s] else ""
          aim_dir = self.ani_settings[c][g][s]["aiming_var"] if "aiming_var" in self.ani_settings[c][g][s] else ""
          #set animation
          if ani_name != "":
            ani_eng.set_animation(ani_name)
            ani_eng.animation_selection.set(ani_name)
          #set background
          if bg_name != "":
            self.game.set_background(bg_name)
            self.game.background_selection.set(bg_name)
          #set facing direction
          if fac_dir != "":
            ani_eng.spiffy_dict["facing_var"].set(fac_dir)
          #set aiming direction
          if aim_dir != "":
            ani_eng.spiffy_dict["aiming_var"].set(aim_dir)
    self.left_panel.add(vcr_controls,height=5 * BUTTON_HEIGHT)
    self.animation_engine.attach_tile_details_panel(self.left_panel,self.fish)
    self.panes.add(self.left_panel)

  def attach_right_panel(self):
    #this same function can also be used to re-create the panel
    self.attach_canvas()
    self.attach_overview()
    self.panes.add(self.right_panel)

  # metadata panel in left pane
  def attach_metadata_panel(self):
    PANEL_HEIGHT = 64
    metadata_section = tk.Frame(self.left_panel, name="metadata_section")
    row = 0
    self.metadata_textbox_vars = {}
    for key in ["sprite.name","author.name","author.name-short"]:
      label = self.fish.translate("meta","meta",key)
      metadata_label = tk.Label(metadata_section, text=label, name=label.lower().replace(' ', '_'))
      metadata_label.grid(row=row,column=1)
      self.metadata_textbox_vars[key] = tk.StringVar()
      metadata_input = tk.Entry(metadata_section, textvariable=self.metadata_textbox_vars[key], name=label.lower().replace(' ', '_') + "_input", width=25)
      metadata_input.insert(0,self.sprite.metadata[key])

      def metadata_changed_trace(key, *args):
        #touch We Made Changes var
        self.sprite.metadata[key] = self.metadata_textbox_vars[key].get()   #retrieve the GUI StringVar value and place it in the true metadata
        self.unsaved_changes = True

      #trace method, fires when the field receives a change; may have more overhead than we'd like
      self.metadata_textbox_vars[key].trace_add("write",partial(metadata_changed_trace,key))

      #validation method, fires when the field loses focus; prone to not capturing changes if user exits before blurring the tk.Entry
      #metadata_input.configure(validate="focusout",validatecommand=partial(metadata_changed_trace,key))

      metadata_input.grid(row=row,column=2)
      row += 1
    self.left_panel.add(metadata_section,minsize=PANEL_HEIGHT,sticky="e")

  #make a status bar
  def create_status_bar(self):
    if not hasattr(self, "status_bar"):
      self.status_bar = StatusBar(self)
      self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    fmt = "%s"
    txt = self.fish.translate(self.game.console_name + '.' + self.game.internal_name,"game","name") + ': "' + self.sprite.classic_name + '"'
    self.status_bar.set(fmt,txt)

  # canvas panel in right pane
  def attach_canvas(self):
    def move_sprite(event):
      self.coord_setter([event.x/self.current_zoom, event.y/self.current_zoom])
      self.update_sprite_animation()
    self.canvas.bind("<Button-1>", move_sprite)   #hook this function to call when the canvas is left-clicked
    self.right_panel.add(self.canvas, text=self.fish.translate("meta","tab","animations"))

  # overview panel in right pane
  def attach_overview(self):
    self.overview_frame.grid_rowconfigure(0, weight=1)
    self.overview_frame.grid_columnconfigure(0, weight=1)

    xscrollbar = tk.Scrollbar(self.overview_frame, orient=tk.HORIZONTAL)
    xscrollbar.grid(row=1, column=0, sticky=tk.EW)

    yscrollbar = tk.Scrollbar(self.overview_frame)
    yscrollbar.grid(row=0, column=1, sticky=tk.NS)

    self.overview_canvas.configure(scrollregion=self.overview_canvas.bbox(tk.ALL),xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
    self.overview_canvas.grid(row=0, column=0, sticky=tk.NSEW)

    xscrollbar.config(command=self.overview_canvas.xview)
    yscrollbar.config(command=self.overview_canvas.yview)

    self.right_panel.add(self.overview_frame, text=self.fish.translate("meta","tab","overview"))

  # do the saving work of representative images
  def get_representative_images(self, style):
    #list representative images
    image_list = self.sprite.get_representative_images(style)
    #did we save successfully? assume no
    save_success_bool = False
    #if we've only got one representative image
    if len(image_list) == 1:
      #get the data
      filename, image = image_list[0]
      #ask for destination
      filename = filedialog.asksaveasfilename(initialfile=filename, initialdir=self.working_dirs["file.save"], title=self.fish.translate("meta","dialogue","file.save.representative-image-single"), filetypes=((self.fish.translate("meta","dialogue","file.save.types.label"),"*.png *.gif"),))
      if filename:
        try:
          #try to save it
          image.save(filename)
          # FIXME: English
          messagebox.showinfo("Save Complete", f"Saved as {filename}")
          save_success_bool = True
        except IOError:
          #something went oops
          save_success_bool = False
      else:    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
        save_success_bool = False
    #if we've got many representative images
    elif len(image_list) > 1:
      #ask for destination folder
      base_folder = filedialog.askdirectory(initialdir=self.working_dirs["file.save"], title=self.fish.translate("meta","dialogue","file.save.representative-images-multiple"))
      if base_folder:
        try:
          #try to save each one
          for filename, image in image_list:
            image.save(os.path.join(base_folder, filename))
          # FIXME: English
          messagebox.showinfo("Save Complete", f"Saved images to {base_folder}")
          save_success_bool = True
        except IOError:
          #something went oops
          save_success_bool = False
      else:    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
        save_success_bool = False
    if not save_success_bool:
      # FIXME: English
      messagebox.showerror("ERROR", f"ERROR: Could not create image file(s)")
    return save_success_bool



  ############################ ANIMATION FUNCTIONS HERE ################################

  # get sprite animation booted up and running
  def initialize_sprite_animation(self):
    self.frames_left_before_freeze = CONST.MAX_FRAMES
    self.freeze_ray = True # stops time, tell your friends
    self.frame_number = 0
    self.start_global_frame_timer()

  # update animation imagery in case an option was changed
  def update_sprite_animation(self):
    self.animation_engine.update_animation()

  # start up timer and play stuff
  def start_global_frame_timer(self):
    #called by play button
    if self.freeze_ray:     #if we were frozen before
      self.frames_left_before_freeze = CONST.MAX_FRAMES
      self.freeze_ray = False
      self.time_marches_forward()

  def advance_global_frame_timer(self):
    #move frame timer forward
    self.frame_number += 1
    self.frames_left_before_freeze = max(0, self.frames_left_before_freeze - 1)
    if self.frame_number >= CONST.MAX_FRAMES:   #just in case someone leaves this running for, say...forever
      self.reset_global_frame_timer()
    self.update_sprite_animation()

  # play through animation one time and stop
  def play_once(self):
    self.frames_left_before_freeze = self.animation_engine.frames_in_this_animation()
    if self.freeze_ray:   #if we were frozen before
      self.freeze_ray = False
      self.time_marches_forward()

  # reset timer and stop playback
  def reset_global_frame_timer(self):
    #called by radio reset button
    self.frame_number = 0
    self.pause_global_frame_timer()

  def pause_global_frame_timer(self):
    #called by pause button
    self.frames_left_before_freeze = 0
    self.freeze_ray = True  # stops time, tell your friends
    self.update_sprite_animation()

  def rewind_global_frame_timer(self):
    #called by step radio button to pause and step backward
    self.frame_number = max(0,self.frame_number - 1)
    self.pause_global_frame_timer()

  def step_global_frame_timer(self):
    #called by step radio button to pause and step forward
    self.pause_global_frame_timer()
    self.advance_global_frame_timer()

  # go to previous animation image set
  def go_to_previous_pose(self):
    self.frame_number = max(0,self.frame_number - self.animation_engine.frames_to_previous_pose())
    self.pause_global_frame_timer()

  # go to next animation image set
  def go_to_next_pose(self):
    self.frame_number = self.frame_number + self.animation_engine.frames_left_in_this_pose()
    self.pause_global_frame_timer()

  # start global timer
  def time_marches_forward(self):
    start_time = time.perf_counter()
    MIN_WAIT = 5      #have to give the rest of the program time to work, and tkInter is not thread-safe
    FRAME_DELAY = 17  #equal to about ceiling(1000/60) in order to simulate 60 Hz (can't go faster without skipping frames due to PC monitor refresh rate)
    if self.frames_left_before_freeze > 0 and not self.freeze_ray:
      self.advance_global_frame_timer()
      end_time = time.perf_counter()
      lag = (end_time-start_time)*1000
      wait_time = int(FRAME_DELAY/self.current_speed - lag)
      self.timer_callback = self.master.after(max(wait_time,5), self.time_marches_forward)     #schedule next tick of the clock
    else:
      self.pause_global_frame_timer()

  # get current zoom factor
  def zoom_getter(self):
    return self.current_zoom

  # get current frame number
  def frame_getter(self):
    return self.frame_number

  # get current coordinate location
  def coord_getter(self):
    return self.sprite_coord

  # set coordinate location
  def coord_setter(self,coords):
    self.sprite_coord = coords

  ########################### VCR CONTROLS HERE ######################################

  # build vcr controls
  def get_vcr_controls(self):
    control_section = tk.Frame(self.left_panel, name="vcr_controls_section")
    widgetlib.right_align_grid_in_frame(control_section)

    def zoom_out(*args):
      self.current_zoom = max(0.5, self.current_zoom - 0.1)
      set_zoom_text()
      self.game.update_background_image()
      self.update_sprite_animation()
    def zoom_in(*args):
      self.current_zoom = min(4.0, self.current_zoom + 0.1)
      set_zoom_text()
      self.game.update_background_image()
      self.update_sprite_animation()
    def set_zoom_text():
      self.zoom_factor.set('x' + str(round(self.current_zoom, 1)) + ' ')

    def speed_down(*args):
      self.current_speed = max(0.1, self.current_speed - 0.1)
      set_speed_text()
    def speed_up(*args):
      self.current_speed = min(2.0, self.current_speed + 0.1)
      set_speed_text()
    def set_speed_text():
      self.speed_factor.set(str(round(self.current_speed * 100)) + '%')

    if not hasattr(self,"current_zoom"):
      self.current_zoom = 2              #starting zoom, if app is just started
    if not hasattr(self,"current_speed"):
      self.current_speed = 1             #starting speed, if app is just started
    if not hasattr(self,"frame_number"):
      self.frame_number = 0              #starting frame, if app is just started
    self.zoom_factor = tk.StringVar(control_section)
    self.speed_factor = tk.StringVar(control_section)

    set_zoom_text()
    set_speed_text()

    BUTTON_WIDTH = 60
    self.current_grid_cell = 0

    #make a vcr button label
    # Inbound
    #  textvariable: var to report back to
    #  icon_name: filename of icon to use
    def make_vcr_label(textvariable, icon_name=None):
      icon_path = common.get_resource(["meta","icons"],icon_name if icon_name is not None else "blank.png")
      image = ImageTk.PhotoImage(Image.open(icon_path)) if icon_path else None
      vcr_label = tk.Label(control_section, image=image, anchor='e', compound="left", width=BUTTON_WIDTH, textvariable=textvariable)
      vcr_label.grid(row = self.current_grid_cell//3,
            column = 1 + (self.current_grid_cell % 3),
            sticky=['nes'])
      self.current_grid_cell += 1
      return vcr_label

    #make a vcr button
    # Inbound
    #  text: text label
    #  icon_name: filename of icon to use
    #  command: command to execute when pressed
    #  side: alignment
    def make_vcr_button(text="", icon_name=None, command=None, side=""):
      side = side if side != "" else "right"
      icon_path = common.get_resource(["meta","icons"],icon_name if icon_name is not None else "blank.png")
      image = ImageTk.PhotoImage(Image.open(icon_path)) if icon_path else None
      if side == "right":
        side = tk.RIGHT
      elif side == "left":
        side = tk.LEFT
      else:
        side = tk.NONE
      vcr_button = tk.Button(control_section, image=image, text=text, compound=side, width=BUTTON_WIDTH, command=command)
      vcr_button.image = image
      vcr_button.grid(row = self.current_grid_cell//3,
            column = 1 + (self.current_grid_cell % 3),
            sticky=['nesw','nesw','nesw'][self.current_grid_cell % 3])
      self.current_grid_cell += 1

    def make_vcr_buttons(vcr_buttons_in):
      vcr_buttons_out = []
      for (fish_subkey, icon_name, command, side) in vcr_buttons_in:
        vcr_buttons_out.append(make_vcr_button(self.fish.translate("meta","vcr-controls",fish_subkey), icon_name, command, side))

    #make a container for all the buttons
    vcr_buttons = []

    #zoom controls
    zoom_factor_label = make_vcr_label(self.zoom_factor, None)
    zoom_buttons = [
      ("zoom-minus","zoom-out.png",zoom_out,"left"),
      ("zoom-plus","zoom-in.png",zoom_in,"")
    ]
    make_vcr_buttons(zoom_buttons)

    #speed controls
    speed_factor_label = make_vcr_label(self.speed_factor,None)
    speed_buttons = [
      ("speed-minus","speed-down.png",speed_down,"left"),
      ("speed-plus","speed-up.png",speed_up,"")
    ]
    make_vcr_buttons(speed_buttons)

    #play controls
    play_buttons = [
      ("play","play.png",self.start_global_frame_timer,""),
      ("play-one","play-one.png",self.play_once,""),
      ("reset","reset.png",self.reset_global_frame_timer,"")
    ]
    make_vcr_buttons(play_buttons)

    #frame step controls
    frame_step_buttons = [
      ("frame-backward","frame-backward.png",self.rewind_global_frame_timer,"left"),
      ("pause","pause.png",self.pause_global_frame_timer,""),
      ("frame-forward","frame-forward.png",self.step_global_frame_timer,"")
    ]
    make_vcr_buttons(frame_step_buttons)

    #pose step controls
    make_vcr_buttons([("pose-backward","step-backward.png",self.go_to_previous_pose,"left")])
    null_label = make_vcr_label("", None)
    make_vcr_buttons([("pose-forward","step-forward.png",self.go_to_next_pose,"")])

    return control_section

  # build reload button for refreshing currently-loaded sprite file without having to navigate open dialogues
  def get_reload_button(self):
    reload_section = tk.Frame(self.left_panel, name="reload_section")
    widgetlib.center_align_grid_in_frame(reload_section)
    reload_button = tk.Button(reload_section, text=self.fish.translate("meta","meta","reload"), padx=20, command=self.reload)
    reload_button.grid(row=0,column=1)
    return reload_section

  def reload(self):
    #activated when the reload button is pressed.  Should reload the sprite from the file but not manipulate the buttons
    self.sprite.load_animations()
    self.sprite.import_from_filename()
    self.animation_engine.update_overview_panel()   #TODO: Need to decide if this belongs in animation_engine
    self.animation_engine.update_animation()

  ############################ MENU BAR FUNCTIONS HERE ################################

  #query user for file to open; ZSPR/PNG/SFC/SMC
  def open_file(self):
    #Give the user a chance to regret not saving their work
    if self.unsaved_changes:
      save_before_open = messagebox.askyesnocancel(self.app_title,self.fish.translate("meta","dialogue","open.save-before-open"))
      if save_before_open is not None:    #didn't cancel
        if save_before_open:        #if they chose to save, present save dialogue
          saved = self.save_file_as()
          if not saved:
            messagebox.showerror(self.app_title,self.fish.translate("meta","dialogue","open.save-failed-during-open-attempt"))
            return False          #don't open a new sprite; something went wrong with the save
        else:      #chose not to save before opening
          self.unsaved_changes = False

    #save current animation/bg/direction settings
    self.save_ani_settings()

    filetypes = ".zspr " # FIXME: Assuming Z3Link-only
    filetypes += ".png "
#    filetypes += ".nes " # NES RomHandler
    filetypes += ".smc .sfc " # SNES RomHandler
    filename = filedialog.askopenfilename(initialdir=self.working_dirs["file.open"], title=self.fish.translate("meta","dialogue","file.open.title"), filetypes=((self.fish.translate("meta","dialogue","file.open.types.label"),filetypes),))
    if filename:
      #if we've got a filename, set the working dir and load the sprite
      self.working_dirs["file.open"] = filename[:filename.rfind('/')]
      self.load_sprite(filename)
      return True        #report success to caller, if they care
    return False       #we didn't open anything

  #query user to export file; PNG/ZSPR/RDC
  def save_file_as(self):
    # Save in one of the valid formats.  TODO: When ZSPR export is implemented, switch this around so that ZSPR is the default
    filetypes = ((self.fish.translate("meta","dialogue","file.save.png"),"*.png"),(self.fish.translate("meta","dialogue","file.save.zspr"),"*.zspr"),(self.fish.translate("meta","dialogue","file.save.rdc"),"*.rdc"))

    filename = ""
    if "sprite.name" in self.sprite.metadata:
      filename = self.sprite.metadata["sprite.name"]
    else:
      # FIXME: English
      filename = "unknown"
    filename = common.filename_scrub(filename)

    filename = filedialog.asksaveasfilename(defaultextension=(".png",".zspr",".rdc"), initialfile=filename, initialdir=self.working_dirs["file.save"], title=self.fish.translate("meta","dialogue","file.save.title"), filetypes=filetypes)
    if filename:
      save_success_bool = self.sprite.save_as(filename)
      if save_success_bool:
        self.unsaved_changes = False
        self.working_dirs["file.save"] = os.path.dirname(filename)
        messagebox.showinfo("Save Complete", f"Saved as {filename}")
        self.save_working_dirs()
      else:
        # FIXME: English
        messagebox.showerror("Not Yet Implemented",os.path.splitext(filename)[1][1:].upper() + " format not yet available for " + self.game.name + '/' + self.sprite.classic_name + " Sprites.")
      return save_success_bool
    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
    return False

  #query user to inject sprite into game file
  # Inbound:
  #  inject: Are we injecting directly or making a copy?
  def copy_into_ROM(self, inject=False):
    dest_filename = None
    default_ext = ""
    if self.game.console_name == "nes":
      default_ext = ".nes"
    elif self.game.console_name == "snes":
      default_ext = ".sfc"
    if inject:
      dest_filename = filedialog.asksaveasfilename(defaultextension=default_ext, initialdir=self.working_dirs["export.dest"], title=self.fish.translate("meta","dialogue","export.inject.title"), filetypes=((self.fish.translate("meta","dialogue","export.inject.types"),"*.sfc *.smc"),))
      source_filename = dest_filename
    else:
      source_filename = filedialog.askopenfilename(initialdir=self.working_dirs["export.source"], title=self.fish.translate("meta","dialogue","export.source.title"), filetypes=((self.fish.translate("meta","dialogue","export.source.types"),"*.sfc *.smc"),))
      if source_filename:
        _,file_extension = os.path.splitext(source_filename)
        if file_extension.lower() in ['.sfc','.smc']:
          default_extension = file_extension.lower()
        else:
          default_extension = default_ext
        dest_filename = os.path.splitext(source_filename)[0] + "_modified"
        dest_filename = filedialog.asksaveasfilename(defaultextension=default_extension, initialfile=dest_filename, initialdir=self.working_dirs["export.dest"], title=self.fish.translate("meta","dialogue","export.inject-new.title"), filetypes=((self.fish.translate("meta","dialogue","export.inject-new.types"),"*.sfc *.smc"),))
    if dest_filename:
      rom = self.game.get_rom_from_filename(source_filename)
      modified_rom = self.sprite.inject_into_ROM(self.animation_engine.spiffy_dict, rom)
      #print(modified_rom.get_patch())
      modified_rom.save(dest_filename, overwrite=True)
      self.working_dirs["export.dest"] = dest_filename[:dest_filename.rfind('/')]
      self.working_dirs["export.source"] = source_filename[:source_filename.rfind('/')]
      # FIXME: English
      messagebox.showinfo("Export success",f"Saved injected ROM as {dest_filename}")

  #query user for directory to inject sprite into
  def copy_into_ROM_bulk(self, inject=False):
    source_filepath = None
    if inject:
      source_filepath = filedialog.askdirectory()  #only injection is supported
    else:
      # FIXME: English
      raise AssertionError("Unsure if making copies fits this purpose well")

    source_filenames = []  #walk through the game files and inject the loaded sprite

    default_exts = ""
    if self.game.console_name == "nes":
      default_exts = [ ".nes" ]
    elif self.game.console_name == "snes":
      default_exts = [ ".smc", ".sfc" ]

    for r,d,f in os.walk(source_filepath):
      for file in f:
        _,file_extension = os.path.splitext(file)
        if file_extension.lower() in default_exts:
          source_filenames.append(os.path.join(r,file))
    for source_filename in source_filenames:
      dest_filename = source_filename
      rom = self.game.get_rom_from_filename(source_filename)  #read ROM data
      same_internal_name = self.game.internal_name == gamelib.autodetect_game_type_from_rom_filename(self.game.console_name,source_filename)[0]  #the game file matches
      is_zsm = "ZSM" in str(rom.get_name())  #this is a ZSM game file
      # FIXME: English, need to get character name translations and compare against those
      if same_internal_name or (is_zsm and self.sprite.classic_name in ["Link","Samus"]):  #if we've got a compatible game file, inject it!
        modified_rom = self.sprite.inject_into_ROM(self.animation_engine.spiffy_dict, rom)
        modified_rom.save(dest_filename, overwrite=True)

  #alias to inject into a game file
  def inject_into_ROM(self):
    self.copy_into_ROM(inject=True)

  #alias to inject into a directory of game files
  def inject_into_ROM_bulk(self):
    self.copy_into_ROM_bulk(inject=True)

  #export current frame as PNG
  def export_frame_as_png(self):
    filetypes = ((self.fish.translate("meta","dialogue","file.save.png"),"*.png"),)

    filename = ""
    if "sprite.name" in self.sprite.metadata:
      filename = self.sprite.metadata["sprite.name"]
    else:
      filename = "unknown"

    if hasattr(self.animation_engine,"animation_selection"):
      filename += '_' + self.animation_engine.animation_selection.get()
    else:
      filename += "unknown-animation"

    if hasattr(self.animation_engine,"pose_number"):
      filename += '_' + str(self.animation_engine.pose_number+1)
    else:
      filename += str(-1)

    if hasattr(self.animation_engine,"frame_number"):
      filename += '_' + str(self.animation_engine.frame_number)
    else:
      filename += str(-1)

    if hasattr(self.animation_engine,"zoom_getter"):
      filename += ('_' + "zoom-" + self.zoom_factor.get()).strip()
    if hasattr(self,"current_speed"):
      filename += ('_' + "speed-" + str(self.current_speed * 100) + '%').strip()
    filename = common.filename_scrub(filename)

    filename = filedialog.asksaveasfilename(defaultextension=(".png"), initialfile=filename, initialdir=self.working_dirs["export.frame-as-png"], title=self.fish.translate("meta","dialogue","export.frame-as-png"), filetypes=filetypes)
    if filename:
      returnvalue = self.animation_engine.export_frame_as_PNG(filename)
      if returnvalue:
        self.working_dirs["export.frame-as-png"] = filename[:filename.rfind('/')]
        # FIXME: English
        messagebox.showinfo("Save Complete", f"Saved as {filename}")
      return returnvalue
    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
    return False

  #export current animation as GIF
  def export_animation_as_gif(self):
    filetypes = ((self.fish.translate("meta","dialogue","file.save.gif"),"*.gif"),)

    filename = ""
    if "sprite.name" in self.sprite.metadata and self.sprite.metadata["sprite.name"]:
      filename = self.sprite.metadata["sprite.name"]
    else:
      filename = "unknown"

    if hasattr(self.animation_engine,"animation_selection"):
      filename += '_' + self.animation_engine.animation_selection.get()

    if hasattr(self.animation_engine,"zoom_getter"):
      filename += ('_' + "zoom-" + self.zoom_factor.get()).strip()
    if hasattr(self,"current_speed"):
      filename += ('_' + "speed-" + str(self.current_speed * 100) + '%').strip()

    filename = common.filename_scrub(filename)

    filename = filedialog.asksaveasfilename(defaultextension=(".gif"), initialfile=filename, initialdir=self.working_dirs["export.frame-as-png"], title=self.fish.translate("meta","dialogue","export.animation-as-gif"), filetypes=filetypes)
    if filename:
      returnvalue = self.animation_engine.export_animation_as_gif(filename, zoom=self.current_zoom, speed=self.current_speed)
      if returnvalue:
        # FIXME: English
        messagebox.showinfo("Save Complete", f"Saved as {filename}")
      return returnvalue
    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
    return False

  #export current animation as collage PNG
  def export_animation_as_collage(self,orientation="horizontal"):
    if orientation == "vertical":
      raise NotImplementedError()
    filetypes = ((self.fish.translate("meta","dialogue","file.save.png"),"*.png"),)

    filename = ""
    if "sprite.name" in self.sprite.metadata:
      filename = self.sprite.metadata["sprite.name"]
    else:
      filename = "unknown"

    if hasattr(self.animation_engine,"animation_selection"):
      filename += '_' + self.animation_engine.animation_selection.get()
    filename = common.filename_scrub(filename)

    if hasattr(self.animation_engine,"zoom_getter"):
      filename += ('_' + "zoom-" + self.zoom_factor.get()).strip()
    if hasattr(self,"current_speed"):
      filename += ('_' + "speed-" + str(self.current_speed * 100) + '%').strip()

    filename = common.filename_scrub(filename)

    filename = filedialog.asksaveasfilename(defaultextension=(".png"), initialfile=filename, initialdir=self.working_dirs["export.animation-as-" + orientation[:1] + "collage"], title=self.fish.translate("meta","dialogue","export.animation-as-" + orientation[:1] + "collage"), filetypes=filetypes)
    if filename:
      returnvalue = self.animation_engine.export_animation_as_collage(filename,orientation)
      if returnvalue:
        self.working_dirs["export.animation-as-collage"] = filename[:filename.rfind('/')]
        # FIXME: English
        messagebox.showinfo("Save Complete", f"Saved as {filename}")
      return returnvalue
    #user cancelled out of the prompt, in which case report that you did not save (i.e. for exiting the program)
    return False

  def export_palette(self, fmt="gimp"):
    if self.sprite.classic_name != "Link":
      return

    palette_doc = []
    header = []
    footer = [""]
    clrfmt = lambda x:(
      "%d %d %d"
      %
      (
        x[0],
        x[1],
        x[2]
      )
    )

    paletteID = ""
    #get animation engine handle
    ani_eng = self.animation_engine
    if "mail_var" in ani_eng.spiffy_dict:
      paletteID = ani_eng.spiffy_dict["mail_var"].get()
    elif "suit_var" in ani_eng.spiffy_dict:
      paletteID = ani_eng.spiffy_dict["suit_var"].get()

    # GIMP
    # CinePaint
    # Inkscape
    # Krita
    if fmt == "gimp":
      header = [
        "GIMP Palette",
        "Base Sprite Name: ".ljust(len("Custom Sprite Name: "))   + self.sprite.classic_name,
        "Base Palette Name: ".ljust(len("Custom Sprite Name: "))  + paletteID,
        "Base Game Name: ".ljust(len("Custom Sprite Name: "))     + self.game.name,
        "Custom Sprite Name: ".ljust(len("Custom Sprite Name: ")) + self.sprite.metadata["sprite.name"],
        "Author: ".ljust(len("Custom Sprite Name: "))             + self.sprite.metadata["author.name"],
        "Columns: ".ljust(len("Custom Sprite Name: "))            + str(0),
        "#"
      ]
      clrfmt = lambda x:(
        "%s %s %s\t%s"
        %
        (
          str(x[0]).rjust(3),
          str(x[1]).rjust(3),
          str(x[2]).rjust(3),
          " " or "Color Name"
        )
      )

    # Corel
    # Graphics Gale
    # Paint Shop Pro
    elif fmt == "jasc":
      header = [
        "JASC-PAL",
        "0100",
        "16"
      ]

    # Paint.NET
    elif fmt == "pdn":
      header = [
        "; paint.net Palette File",
        "; Lines that start with a semicolon are comments",
        "; Colors are written as 8-digit hexadecimal numbers: aarrggbb",
        "; For example, this would specify green: FF00FF00",
        "; The alpha ('aa') value specifies how transparent a color is. FF is fully opaque, 00 is fully transparent.",
        "; A palette must consist of ninety six (96) colors. If there are less than this, the remaining color",
        "; slots will be set to white (FFFFFFFF). If there are more, then the remaining colors will be ignored.",
        ";",
        "; Base Sprite Name: ".ljust(len("; Custom Sprite Name: "))   + self.sprite.classic_name,
        "; Base Palette Name: ".ljust(len("; Custom Sprite Name: "))  + paletteID,
        "; Base Game Name: ".ljust(len("; Custom Sprite Name: "))     + self.game.name,
        "; Custom Sprite Name: ".ljust(len("; Custom Sprite Name: ")) + self.sprite.metadata["sprite.name"],
        "; Author: ".ljust(len("; Custom Sprite Name: "))             + self.sprite.metadata["author.name"],
      ]
      clrfmt = lambda x:(
        "%s%s%s%s"
        %
        (
          "FF",
          (hex(x[0])[2:]).ljust(2,'0').upper(),
          (hex(x[1])[2:]).ljust(2,'0').upper(),
          (hex(x[2])[2:]).ljust(2,'0').upper()
        )
      )

    # TileShop
    elif fmt == "tileshop":
      header = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<!--',
        '<sprite>',
        "\t" + f"<base name=\"{self.sprite.classic_name}\" game=\"{self.game.name}\" />",
        "\t" + f"<palette name=\"{paletteID}\" />",
        "\t" + f"<custom name=\"{self.sprite.metadata['sprite.name']}\" author=\"{self.sprite.metadata['author.name']}\" />",
        '</sprite>',
        '-->',
        '<palette datafile="" color="Bgr15" zeroindextransparent="true">'
      ]
      clrfmt = lambda x:(
        "\t<nativecolor value=\"#%s%s%s%s\" />"
        %
        (
          (hex(x[0])[2:]).ljust(2,'0').upper(),
          (hex(x[1])[2:]).ljust(2,'0').upper(),
          (hex(x[2])[2:]).ljust(2,'0').upper(),
          "FF"
        )
      )
      footer = [
        '</palette>',
        ""
      ]
      pass

    palette_doc += header

    palette_doc.append(clrfmt((0,0,0)))

    for color in self.sprite.get_palette([paletteID]):
      color = clrfmt(color)
      palette_doc.append(color)

    if fmt == "pdn":
      padding = 96 - len(palette_doc) + len(header)
      for i in range(padding):
        palette_doc.append("FFFFFFFF")

    palette_doc += footer

    print("\n".join(palette_doc))

  def open_project_website(self):
    website_url = "https://artheau.github.io/SpriteSomething"
    webbrowser.open_new(website_url)

  def open_project_repository(self):
    website_url = "https://github.com/Artheau/SpriteSomething"
    webbrowser.open_new(website_url)

  def open_project_wiki(self):
    website_url = "https://github.com/Artheau/SpriteSomething/wiki"
    webbrowser.open_new(website_url)

  def check_for_updates(self):
    update_available = False
    version_url = "https://artheau.github.io/SpriteSomething/resources/app/meta/manifests/app_version.txt"
    this_version = CONST.APP_VERSION  # get current version
    version_req = urllib.request.urlopen(version_url) # make request for online app version
    latest_version = version_req.readlines()[0].decode("utf-8").strip() # get version from file

    this_version_type = "TRAVIS"    # assume this version & latest version are in Travis format (<major>.<minor>.<build>)
    latest_version_type = "TRAVIS"

    if len(this_version.split('.')) > 2:
      # if it's alphanumeric, it's a hash ID and not a Travis build number
      if not this_version.split('.')[2].isnumeric():
        this_version_type = "GHACTIONS"
    if len(latest_version.split('.')) > 2:
      # if it's alphanumeric, it's a hash ID and not a Travis build number
      if not latest_version.split('.')[2].isnumeric():
        latest_version_type = "GHACTIONS"

    if this_version_type == "TRAVIS" and latest_version_type == "TRAVIS":
      # Travis && Travis is an arithmetical comparison
      update_available = latest_version > this_version
    elif this_version_type == "GHACTIONS" or latest_version_type == "GHACTIONS":
      # GH Actions in either version becomes a little more complex
      this_version_split = this_version.split('.')
      latest_version_split = latest_version.split('.')
      # check if <major>.<minor> is bigger
      update_available = float(latest_version_split[0] + '.' + latest_version_split[1]) > float(this_version_split[0] + '.' + this_version_split[1])
      if not update_available:
        # still no update calculated
        # check if <major>.<minor> is the same
        if float(latest_version_split[0] + '.' + latest_version_split[1]) == float(this_version_split[0] + '.' + this_version_split[1]):
          # if so, if the last part is different, there might be an update
          update_available = not latest_version_split[2] == this_version_split[2]

    if update_available:
      # FIXME: English
      get_update = messagebox.askyesno(
                    self.app_title,
                    "Current Version: " + this_version + "\n" +
                    "Latest Version: " + latest_version + "\n" +
                    "It seems that there is an update available. Would you like to go to the project page to get it?"
      )
      if get_update:
        webbrowser.open_new("https://github.com/Artheau/SpriteSomething/releases/v" + latest_version)
    else:
      # FIXME: English
      messagebox.showinfo(self.app_title,"It seems that you're up to date!")

  def diagnostics(self):
    # Debugging purposes
    dims = {
      "window": {
        "width": 800,
        "height": 500
      },
      "textarea.characters": {
        "width": 120,
        "height": 50
      }
    }
    diag = tk.Tk()
    diag.title("SpriteSomething Diagnostics")
    diag.geometry(str(dims["window"]["width"]) + 'x' + str(dims["window"]["height"]))
    text = tk.Text(diag, width=dims["textarea.characters"]["width"], height=dims["textarea.characters"]["height"])
    text.pack()
    self.add_text_link_array(diagnostics.output(), text)

  def about(self):
    # Credit where credit's due
    dims = {
      "window": {
        "width": 350,
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
          "[Artheau](http://github.com/Artheau/PixelArt)",
          "[Minnie A. Trethewey](http://github.com/miketrethewey)",
          "",
          "Thanks to:",
          "[Auximines](https://metroidfanon.fandom.com/wiki/Super_Justin_Bailey) for initial inspiration for custom Super Metroid sprites",
           "[Pneumatic](http://twitch.tv/pneumaticgaming) for datastamp for Super Metroid/Samus sprites",
          "",
          "Based on:",
          "[SpriteAnimator](http://github.com/spannerisms/SpriteAnimator) by Spannerisms",
          "[ZSpriteTools](http://github.com/sosuke3/ZSpriteTools) by Sosuke3",
          # Assets from SpriteAnimator & ZSpriteTools used with permission
    ]
    about = tk.Tk()
    about.title(f"About {self.app_title}")
    about.geometry(str(dims["window"]["width"]) + 'x' + str(dims["window"]["height"]))
    about.resizable(tk.FALSE,tk.FALSE)
    #about.attributes("-toolwindow", 1)  #Linux doesn't like this
    text = tk.Text(about, bg='#f0f0f0', font='TkDefaultFont', width=dims["textarea.characters"]["width"], height=dims["textarea.characters"]["height"])
    text.pack()
    text.configure(cursor="arrow")
    self.add_text_link_array(lines, text)
    text.bind("<Button-1>", lambda e: txtEvent(e))

  #write working dirs to file
  def save_working_dirs(self):
    user_resources_path = os.path.join(".","resources","user")
    working_dirs_path = os.path.join(user_resources_path,"meta","manifests")
    working_dirs_filename = "working_dirs.json"
    with open(os.path.join(working_dirs_path,working_dirs_filename),"w+") as f:
      f.write(json.dumps(self.working_dirs,indent=2))
    os.chmod(os.path.join(working_dirs_path,working_dirs_filename),0o775)

  #write current animation settings to file
  def save_ani_settings(self):
    c = self.game.console_name
    g = self.game.internal_name
    s = self.sprite.internal_name
    ani_eng = self.animation_engine
    ani_name = ani_eng.animation_selection.get()
    bg_name = self.game.background_selection.get()
    fac_dir = ani_eng.spiffy_dict["facing_var"].get() if "facing_var" in ani_eng.spiffy_dict else ""
    aim_dir = ani_eng.spiffy_dict["aiming_var"].get() if "aiming_var" in ani_eng.spiffy_dict else ""
    if c not in self.ani_settings:
      self.ani_settings[c] = {}
    if g not in self.ani_settings[c]:
      self.ani_settings[c][g] = {}
    if s not in self.ani_settings[c][g]:
      self.ani_settings[c][g][s] = {}
    self.ani_settings[c][g][s] = {
      "animation_name": ani_name,
      "background_name": bg_name,
      "facing_var": fac_dir,
      "aiming_var": aim_dir
    }
    user_resources_path = os.path.join(".","resources","user")
    ani_settings_path = os.path.join(user_resources_path,"meta","manifests")
    ani_settings_filename = "ani_settings.json"
    with open(os.path.join(ani_settings_path,ani_settings_filename),"w+") as f:
      f.write(json.dumps(self.ani_settings,indent=2))
      os.chmod(os.path.join(ani_settings_path,ani_settings_filename),0o755)

  #exit sequence
  def exit(self):
    if self.unsaved_changes:
      save_before_exit = messagebox.askyesnocancel(self.app_title,self.fish.translate("meta","dialogue","exit.save-before-exit"))
      if save_before_exit is not None:        #didn't cancel
        if save_before_exit:
          saved = self.save_file_as()
          if not saved:
            exit_anyway = messagebox.askyesno(self.app_title, self.fish.translate("meta","dialogue","exit.save-failed-during-exit-attempt"))
            if not exit_anyway:
              #user bails because their file didn't save
              return
        else:
          messagebox.showwarning(self.app_title, self.fish.translate("meta","dialogue","exit.nosave-before-exit"))   #TODO: can we add this humor somehow without forcing the user to close another dialogue box?

    self.save_working_dirs()
    self.save_ani_settings()
    sys.exit(0)

  ######################### HELPER FUNCTIONS ARE BELOW HERE ###############################

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
