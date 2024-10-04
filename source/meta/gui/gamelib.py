# pylint: disable=bad-indentation
#common functions to all games
#handling backgrounds, etc.
#handles import of new sprites

try:
  from PIL import Image, ImageFile
  import tkinter as tk    #for GUI stuff
except ModuleNotFoundError as e:
  print(e)

import importlib            #for importing libraries dynamically
import json                        #for reading JSON
import os                            #for filesystem manipulation
import random                    #for choosing background image to load on app startup
from functools import partial
from shutil import unpack_archive
import zipfile
from source.snes import romhandler as snes
from json.decoder import JSONDecodeError
from source.meta.gui import widgetlib
from source.meta.common import common
from source.meta.gui import gui_common #TODO: Should not use GUI stuff in game class, need to move this elsewhere

def autodetect_snes(sprite_filename):
        #If the file is a rom, then we can go into the internal header and get the name of the game
        game_names = autodetect_game_type_from_rom_filename("snes",sprite_filename)
        selected_game = None

        #prompt user for input
        # FIXME: Ugh, more tk
        selected_game = gui_common.create_chooser("snes",game_names)

        if not selected_game:
            selected_game = random.choice(game_names)

        game = get_game_class_of_type("snes",selected_game)
        #And by default, we will grab the player sprite from this game
        return game, game.make_player_sprite(sprite_filename,"")

def autodetect_nes(sprite_filename):
        #If the file is a rom, then we can go into the internal header and get the name of the game
        game_names = autodetect_game_type_from_rom_filename("nes",sprite_filename)
        selected_game = None

        #prompt user for input
        # FIXME: Ugh, more tk
        selected_game = gui_common.create_chooser("nes",game_names)

        if not selected_game:
            selected_game = random.choice(game_names)

        game = get_game_class_of_type("nes",selected_game)
        #And by default, we will grab the player sprite from this game
        return game, game.make_player_sprite(sprite_filename,"")

def autodetect_png(sprite_filename):
        not_consoles = []
        with open(os.path.join("resources","app","meta","manifests","not_consoles.json")) as f:
            not_consoles = []
            try:
                not_consoles = json.load(f)
            except JSONDecodeError as e:
                raise ValueError("Not Consoles manifest malformed!")
        #the following line prevents a "cannot identify image" error from PIL
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        #I'm not sure what to do here yet in a completely scalable way, since PNG files have no applicable metadata
        (game, sprite, animation_assist) = (None, None, None)
        with Image.open(sprite_filename) as loaded_image:
          game_found = False
          search_path = os.path.join("resources","app")
          for console in os.listdir(search_path):
            if os.path.isdir(os.path.join(search_path,console)) and not console in not_consoles:
              for item in os.listdir(os.path.join(search_path,console)):
                game_name = item
                sprite_manifest_filename = os.path.join(search_path,console,game_name,"manifests","manifest.json")
                with open(sprite_manifest_filename) as f:
                  sprite_manifest = {}
                  try:
                    sprite_manifest = json.load(f)
                  except JSONDecodeError as e:
                    raise ValueError("Game Manifest malformed: " + game_name)
                  for sprite_id in sprite_manifest:
                    if "input" in sprite_manifest[sprite_id] and "png" in sprite_manifest[sprite_id]["input"] and "dims" in sprite_manifest[sprite_id]["input"]["png"]:
                      check_size = sprite_manifest[sprite_id]["input"]["png"]["dims"]
                      if loaded_image.size == tuple(check_size):
                        game = get_game_class_of_type(console,game_name)
                        sprite, animation_assist = game.make_player_sprite(sprite_filename,"")
                        game_found = True
        if not game_found:
            # FIXME: English
            raise AssertionError(f"Cannot recognize the type of file {sprite_filename} from its size: {loaded_image.size}")
        return game, sprite, animation_assist

def autodetect(sprite_filename):
    selected_sheet = ""
    print("---")
    print(f"Autodetecting: {sprite_filename}")

    game, sprite, animation_assist = None, None, None

    not_games = []
    with open(os.path.join("resources","app","meta","manifests","not_games.json")) as f:
        not_games = []
        try:
            not_games = json.load(f)
        except JSONDecodeError as e:
            raise ValueError("Not Games manifest malformed!")

    #need to autodetect which game, and which sprite
    #then return an instance of THAT game's class, and an instance of THAT sprite
    file_slug,file_extension = os.path.splitext(sprite_filename)
    file_slug = os.path.basename(file_slug)

    # Cycle through console filetypes
    # If it matches a console filetype
    # Detected: Console game file
    # Get game names
    # create_extraction_chooser
    # If we didn't choose one, get a random one
    # Get game object
    # Get player sprite & animation assist objects

    for [console, console_types] in {
        "snes": [ ".sfc", ".smc" ],
        "nes": [ ".nes" ],
        "gbc": [ ".gbc", ".gb" ]
    }.items():
        if file_extension.lower() in console_types:
            print(f"Detected: {console.upper()} game file")
            # #If the file is a rom, then we can go into the internal header and get the name of the game
            game_names = autodetect_game_type_from_rom_filename(console,sprite_filename)
            selected_game = None

            #prompt user for input
            #FIXME: Ugh, more tk
            selected_game = gui_common.create_extraction_chooser(console,game_names)

            if not selected_game:
                selected_game = random.choice(game_names)

            game = get_game_class_of_type(console,selected_game)
            #And by default, we will grab the player sprite from this game
            sprite, animation_assist = game.make_player_sprite(sprite_filename,"")

    if game is None or sprite is None or animation_assist is None:
        #If it's not a known filetype but an image, cycle through and find one that matches
        if file_extension.lower() in [".bmp", ".png"]:
            #the following line prevents a "cannot identify image" error from PIL
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            #I'm not sure what to do here yet in a completely scalable way, since PNG files have no applicable metadata
            print(f"Detected: {file_extension.upper()[1:]}!")
            with Image.open(sprite_filename) as loaded_image:
                game_found = False
                sprite_found = False
                search_path = os.path.join("resources","app")
                for console in os.listdir(search_path):
                    if os.path.isdir(os.path.join(search_path,console)) and not console == "meta":
                        for item in os.listdir(os.path.join(search_path,console)):
                            game_name = item
                            if game_name in not_games:
                                continue
                            sprite_manifest_filename = os.path.join(search_path,console,game_name,"manifests","manifest.json")
                            with open(sprite_manifest_filename) as f:
                                sprite_manifest = json.load(f)
                                sprite_name = ""
                                found_id = None
                                for sprite_id in sprite_manifest:
                                    if "input" in sprite_manifest[sprite_id] and file_extension.lower()[1:] in sprite_manifest[sprite_id]["input"]:
                                        pngs = sprite_manifest[sprite_id]["input"][file_extension.lower()[1:]]
                                        if not isinstance(pngs,list):
                                            pngs = [pngs]
                                        for png in pngs:
                                            if "dims" in png and not sprite_found:
                                                check_size = png["dims"]
                                                if loaded_image.size == tuple(check_size):
                                                    print(f"Detected {file_extension.upper()[1:]} dimensions!" + " " + str(check_size))
                                                    if "name" in png:
                                                        check_names = png["name"]
                                                        print(f"Checking {file_extension.upper()[1:]} name!")
                                                        if file_slug in check_names:
                                                            sprite_name = file_slug
                                                            sprite_found = True
                                                            print(f"Detected {file_extension.upper()[1:]} name!" + " [" + sprite_name + "]")
                                                            found_id = sprite_id
                                                    elif not sprite_found:
                                                        sprite_name = sprite_manifest[sprite_id]["folder name"]
                                                        sprite_found = True
                                                        print("Defaulting name!" + " [" + sprite_name + "]")
                                                        found_id = sprite_id
                                if sprite_name != "":
                                    game = get_game_class_of_type(console,game_name)
                                    sprite, animation_assist = game.make_sprite_by_number(found_id, sprite_filename,sprite_name)
                                    game_found = True
            if not game_found:
                # FIXME: English
                raise AssertionError(f"Cannot recognize the type of file {sprite_filename} from its size: {loaded_image.size}")
        # FIXME: For now, ZSPRs are Z3Link sprites and we're assuming SNES
        elif file_extension.lower() == ".zspr":
            print("Detected: ZSPR file")
            with open(sprite_filename,"rb") as file:
                zspr_data = bytearray(file.read())
            game = get_game_class_of_type("snes",get_game_type_from_zspr_data(zspr_data))
            sprite, animation_assist = game.make_sprite_by_number(get_sprite_number_from_zspr_data(zspr_data),sprite_filename,"")
        elif file_extension.lower() == ".zip":
            print("Detected: ZIP file!")
            thisData = {
                "likely": {
                    "pc": {},
                    "nes": {},
                    "snes": { "ffmq": False, "mother2": False }
                },
                "lists": {
                    "snes": {
                        "ffmq": [ "darkking1.bmp", "darkking2.bmp" ],
                        "mother2": [1,5,6,7,8,14,15,16,17,21,27,335,362,378,437,457 ]
                    }
                },
                "filenames": {
                    "snes": {
                        "ffmq": [],
                        "mother2": []
                    }
                }
            }
            for i in range (0,len(thisData["lists"]["snes"]["mother2"])):
                thisData["lists"]["snes"]["mother2"][i] = (f'{thisData["lists"]["snes"]["mother2"][i]:03}') + ".png"
            scratch = os.path.join(".","resources","tmp","archive",file_slug)
            if not os.path.isdir(scratch):
                os.makedirs(scratch)
            with zipfile.ZipFile(sprite_filename,'r') as thisZip:
                for gameID in ["ffmq", "mother2"]:
                    for file in thisZip.namelist():
                        if os.path.basename(file) in thisData["lists"]["snes"][gameID]:
                            thisData["likely"]["snes"][gameID] = True
                            thisData["filenames"]["snes"][gameID].append(file)
                    if thisData["likely"]["snes"][gameID]:
                        selected_sheet = gui_common.create_sheet_chooser("snes",gameID,thisData["filenames"]["snes"][gameID])
                        game = get_game_class_of_type("snes",gameID)
                        #And by default, we will grab the player sprite from this game
                        sheet_slug,sheet_extension = os.path.splitext(os.path.basename(selected_sheet))
                        thisZip.extract(selected_sheet,scratch)
                        print(f"Detected: {game.internal_name}/{selected_sheet}!")
                        game, sprite, animation_assist = autodetect(os.path.join(scratch,selected_sheet))
        # elif file_extension.lower() in filetypes:
        #     raise AssertionError(f"{file_extension.upper()[1:]} not yet available by GUI!")

        elif sprite_filename == "":
                #FIXME: English
            raise AssertionError("No filename given")
        elif not os.path.isfile(sprite_filename):
            #FIXME: English
            raise AssertionError(f"Cannot open file: {sprite_filename}")
        else:
            # FIXME: English
            raise AssertionError(f"Filetype of '{file_extension.upper()[1:]}' for '{sprite_filename}' not supported!")

    detected = f"{game.internal_name}/{sprite.internal_name}"
    if selected_sheet != "":
        detected += f"/{selected_sheet}"
    print(f"Detected: {detected}!")
    if sprite.subtype == "doi":
        game.name += ": Dungeons of Infinity"

    return game, sprite, animation_assist

def autodetect_game_type_from_rom_filename(console,filename):
  #dynamic import
  rom_module = {}

  if console == "snes":
    rom_module = importlib.import_module(f"source.{console}.romhandler")
    return autodetect_game_type_from_rom(rom_module.RomHandlerParent(filename))
  if console == "nes":
    rom_module = importlib.import_module(f"source.{console}.romhandler")
    return autodetect_game_type_from_rom(rom_module.RomHandlerParent(filename))
  raise AssertionError(f"Cannot recognize {console} as a supported console")

def autodetect_game_type_from_rom(rom):
    rom_name = rom.get_name()
    with open(common.get_resource(["meta","manifests"],"game_header_info.json")) as file:
        game_header_info = json.load(file)

    game_names = []
    for game_name, header_name_list in game_header_info.items():
        if game_name.lower() != "$schema":
            for header_name in header_name_list:
                if rom_name.upper()[:len(header_name.upper())] == header_name.upper():
                    game_names.append(game_name)

    if len(game_names) == 0:
        game_names = None
        raise AssertionError(f"Could not identify the type of ROM from its header name: {rom_name}")
        # FIXME: English; CLI Errors
        #print(f"Could not identify the type of ROM from its header name: {rom_name}")
    else:
        print(f"Found games: {game_names}")

    return game_names

def get_game_type_from_rdc_data(rdc_data):
    #for now, until other types of RDC files exist, we will just assume that all RDC files are Metroid3 Samus files
    return "metroid3"

def get_game_type_from_zspr_data(zspr_data):
    #for now, until other types of ZSPR files exist, we will just assume that all ZSPR files are Zelda3 Link files
    return "zelda3"

def get_sprite_number_from_rdc_data(rdc_data):
    rdcSlice = rdc_data[50:200]
    txtFmt = rdcSlice.decode("utf-8")
    metadata = txtFmt[txtFmt.find("{"):txtFmt.rindex("}") + 1]
    try:
      metadata = json.loads(metadata)
    except JSONDecodeError as e:
      raise ValueError("Sprite Number metadata malformed!")
    spriteType = metadata["spriteType"] if "spriteType" in metadata else 1
    return spriteType

def get_sprite_number_from_zspr_data(zspr_data):
    return int.from_bytes(zspr_data[21:23], byteorder='little')

def get_game_class_of_type(console_name,game_name):
    #dynamic import
    source_subpath = f"source.{console_name}.{game_name}"
    game_module = None
    try:
        game_module = importlib.import_module(f"{source_subpath}.game")
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(f"Game module not found: {source_subpath}.game")
    return game_module.Game(os.path.join(console_name,game_name))

class GameParent():
    #parent class for games to inherit

    #to make a new game class, you must write code for all of the functions in this section below.
    ############################# BEGIN ABSTRACT CODE ##############################

    def __init__(self, my_subpath=""):
        self.name = "Game Parent Class"    #to be replaced by a name like "Super Metroid"
        self.internal_name = "meta"        #to be replaced by the specific folder name that this app uses, e.g. "metroid3"
        self.plugins = None
        self.has_plugins = None
        self.console_name = "snes" #to be replaced by the console that the game is native to, assuming SNES for now
        self.resource_subpath = my_subpath
        self.inputs = []
        self.outputs = []
        if os.path.isfile(os.path.join("resources","app",self.console_name,"manifests","manifest.json")):
            with open(os.path.join("resources","app",self.console_name,"manifests","manifest.json")) as f:
                manifest_dict = {}
                try:
                    manifest_dict = json.load(f)
                except JSONDecodeError as e:
                    raise ValueError(e)
                if "input" in manifest_dict:
                    self.inputs = [*self.inputs, *manifest_dict["input"]]
                if "output" in manifest_dict:
                    self.outputs = [*self.outputs, *manifest_dict["output"]]

    ############################# END ABSTRACT CODE ##############################

    #the functions below here are special to the parent class and do not need to be overwritten, unless you see a reason

    def load_plugins(self):
        try:
            plugins_module = importlib.import_module(f"source.{self.console_name}.{self.internal_name}.plugins")
            self.plugins = plugins_module.Plugins()
            self.has_plugins = True
        except ModuleNotFoundError as err:
            pass #not terribly interested right now

    def attach_background_panel(self, parent, canvas, zoom_getter, frame_getter, fish):
        #for now, accepting frame_getter as an argument because maybe the child class has animated backgrounds or something
        BACKGROUND_DROPDOWN_WIDTH = 25
        PANEL_HEIGHT = 25
        self.canvas = canvas
        self.zoom_getter = zoom_getter
        self.frame_getter = frame_getter
        self.background_datas = {"filename":{},"title":{},"origin":{}}
        self.current_background_title = None
        self.last_known_zoom = None

        background_panel = tk.Frame(parent, name="background_panel")
        widgetlib.right_align_grid_in_frame(background_panel)
        background_label = tk.Label(background_panel, text=fish.translate("meta","meta","background") + ':')
        background_label.grid(row=0, column=1)
        self.background_selection = tk.StringVar(background_panel)

        background_manifests = common.get_all_resources([self.resource_subpath,"backgrounds"],"backgrounds.json")
        for background_manifest in background_manifests:
            with open(background_manifest) as f:
                background_data = []
                try:
                  background_data = json.load(f)
                except JSONDecodeError as e:
                  raise ValueError("Backgrounds Manifest malformed: " + self.internal_name)
                for background in background_data["backgrounds"]:
                    self.background_datas["filename"][background["filename"]] = background["title"]
                    self.background_datas["title"][background["title"]] = background["filename"]
                    if "origin" in background:
                        self.background_datas["origin"][background["title"]] = background["origin"]
        if len(self.background_datas["filename"]) == 0:
            backgrounds_path = os.path.join("resources","app",self.resource_subpath,"backgrounds")
            if os.path.isdir(backgrounds_path):
                backgrounds = os.listdir(backgrounds_path)
                for background in backgrounds:
                    prettyname = os.path.splitext(background)[0]
                    prettyname = [x[:1].upper() + x[1:] for x in prettyname.split(" ")]
                    prettyname = " ".join(prettyname)
                    self.background_datas["filename"][background] = prettyname
                    self.background_datas["title"][prettyname] = background
        background_prettynames = list(self.background_datas["title"].keys())
        if len(background_prettynames):
            self.background_selection.set(random.choice(background_prettynames))

        background_dropdown = tk.ttk.Combobox(background_panel, state="readonly", values=background_prettynames, name="background_dropdown")
        background_dropdown.configure(width=BACKGROUND_DROPDOWN_WIDTH, exportselection=0, textvariable=self.background_selection)
        background_dropdown.grid(row=0, column=2)

        widgetlib.leakless_dropdown_trace(self, "background_selection", "set_background")

        parent.add(background_panel,minsize=PANEL_HEIGHT)
        return background_panel

    def set_background(self, image_title):
        if self.current_background_title == image_title:
            if self.last_known_zoom == self.zoom_getter():
                return   #there is nothing to do here, because nothing has changed
        else:     #image name is different, so need to load a new image
            image_filename = self.current_background_title
            if image_title in self.background_datas["title"]:
              image_filename = self.background_datas["title"][image_title]
            elif image_title in self.background_datas["filename"]:
              image_filename = image_title
            if common.get_resource([self.console_name,self.internal_name,"backgrounds"],image_filename):
                self.raw_background = Image.open(common.get_resource([self.console_name,self.internal_name,"backgrounds"],image_filename))
            #this doesn't work yet; not sure how to hook it
            if "origin" in self.background_datas:
                if image_title in self.background_datas["origin"]:
                    # print("Setting Coordinates because of background (%s): %s" % (image_title, self.background_datas["origin"][image_title]))
                    if hasattr(self,"coord_setter"):
                        self.coord_setter(self.background_datas["origin"][image_title])

        #now re-zoom the image
        if hasattr(self, "raw_background"):
            new_size = tuple(int(dim*self.zoom_getter()) for dim in self.raw_background.size)
            self.background_image = gui_common.get_tk_image(self.raw_background.resize(new_size,resample=Image.NEAREST))
            if self.current_background_title is None:
                self.background_ID = self.canvas.create_image(0, 0, image=self.background_image, anchor=tk.NW)    #so that we can manipulate the object later
            else:
                self.canvas.itemconfig(self.background_ID, image=self.background_image)
            self.last_known_zoom = self.zoom_getter()
            self.current_background_title = image_title

    def update_background_image(self):
        self.set_background(self.current_background_title)

    def make_player_sprite(self, sprite_filename, sprite_name):
        return self.make_sprite_by_number(0x01, sprite_filename, sprite_name)

    def make_sprite_by_number(self, sprite_number, sprite_filename, sprite_name):
        #go into the manifest and get the actual name of the sprite
        with open(common.get_resource([self.console_name,self.internal_name,"manifests"],"manifest.json")) as file:
            manifest = {}
            try:
                manifest = json.load(file)
            except JSONDecodeError as e:
                raise ValueError("Game Manifest malformed: " + self.internal_name)
        if str(sprite_number) in manifest:
            folder_name = manifest[str(sprite_number)]["folder name"]
            #dynamic imports to follow
            source_subpath = f"source.{self.console_name}.{self.internal_name}.{folder_name}"
            sprite_module = None
            try:
                sprite_module = importlib.import_module(f"{source_subpath}.sprite")
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(f"Sprite module not found: {source_subpath}.sprite")
            resource_subpath = os.path.join(self.console_name,self.internal_name,folder_name)
            sprite = sprite_module.Sprite(sprite_filename,manifest[str(sprite_number)],resource_subpath,sprite_name)

            try:
                animationlib = importlib.import_module(f"{source_subpath}.animation")
                animation_assist = animationlib.AnimationEngine(resource_subpath, self, sprite)
            except ImportError:    #there was no sprite-specific animation library, so import the parent
                animationlib = importlib.import_module(f"source.meta.gui.animationlib")
                animation_assist = animationlib.AnimationEngineParent(resource_subpath, self, sprite)
            return sprite, animation_assist
        # FIXME: English
        raise AssertionError(f"make_sprite_by_number() called for non-implemented sprite_number {sprite_number}")

    def get_rom_from_filename(self, filename):
        #dynamic import
        rom_module = importlib.import_module(f"source.{self.console_name}.{self.internal_name}.rom")
        return rom_module.RomHandler(filename)


def main():
    print(f"Called main() on utility library {__file__}")

if __name__ == "__main__":
    main()
