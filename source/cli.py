import json
import os
import random
from source import common
from source import constants as CONST
from source import gamelib
from source import spritelib
from source import ssDiagnostics as diags

def make_CLI(command_line_args):
  init = CLIMainFrame(command_line_args)

class CLIMainFrame():

  def __init__(self, command_line_args):
    print(self.create_random_title() + " (v" + CONST.APP_VERSION + ')')
    print("")
    print("Initializing CLIMainFrame")
    if command_line_args["mode"]:
      mode = command_line_args["mode"]
      if mode[:4] == "diag":
        print("\n".join(diags.output()))
        exit(1)

      self.load_sprite(command_line_args["sprite"])

      if mode == "export":
        export_filename = command_line_args["export-filename"] if "export-filename" in command_line_args else "export.png"
        self.save_file_as(export_filename)
      elif "inject" in mode:
        dest_default_path = os.path.join("resources",self.game.internal_name,"gamefiles","export")
        source_default_path = os.path.join("resources",self.game.internal_name,"gamefiles","source")
        dest_filename = os.path.join(dest_default_path,"export")
        source_filename = os.path.join(source_default_path,self.game.internal_name)

        if not os.path.isdir(dest_default_path):
          os.makedirs(dest_default_path)

        if "dest-filename" in command_line_args:
          if not command_line_args["dest-filename"] == None:
            dest_filename = command_line_args["dest-filename"]
        if "src-filename" in command_line_args:
          if not command_line_args["src-filename"] == None:
            source_filename = command_line_args["src-filename"]
        if "-bulk" in mode:
          source_filepath = os.path.join("resources",self.game.internal_name,"gamefiles","inject")
          if "src-filepath" in command_line_args:
            if not command_line_args["src-filepath"] == None:
              source_filepath = command_line_args["src-filepath"]
              if "-random" in mode:
                if "spr-filepath" in command_line_args:
                  if not command_line_args["spr-filepath"] == None:
                    sprite_filepath = command_line_args["spr-filepath"]
                    self.randomize_into_ROM_bulk(source_filepath=source_filepath, sprite_filepath=sprite_filepath)
              else:
                self.copy_into_ROM_bulk(source_filepath=source_filepath)
        elif "-random" in mode:
          if "spr-filepath" in command_line_args:
            if not command_line_args["spr-filepath"] == None:
              sprite_filepath = command_line_args["spr-filepath"]
              self.randomize_into_ROM(inject=True, source_filename=source_filename, dest_filename=dest_filename, sprite_filepath=sprite_filepath)
        else:
          if not os.path.isfile(source_filename) and not os.path.isfile(source_filename + ".sfc"):
            print("   Source File does not exist: " + source_filename)
            print("   Source File does not exist: " + source_filename + ".sfc")
            print("    Nuke it from orbit.")
            exit(1)
          if not os.path.splitext(source_filename)[1]:
            source_filename += ".sfc"
          if not os.path.splitext(dest_filename)[1]:
            dest_filename += ".sfc"
          self.copy_into_ROM("-new" not in mode,dest_filename,source_filename)
      elif "get-" in mode and "-sprites" in mode:
        print("  Downloading Sprites")
        if mode == "get-alttpr-sprites":
          self.load_sprite(os.path.join("resources","zelda3","link","link.zspr"))
          self.sprite.get_alttpr_sprites()
      else:
        print("No valid CLI Mode provided")
    else:
      print("No CLI Mode provided")

  def create_random_title(self):
		# Generate a new epic random title for this application
    name_dict = {}
    for filename in common.get_all_resources("app_names.json"):
      with open(filename) as name_file:
        for key,item in json.load(name_file).items():
          if key in name_dict:
            name_dict[key].extend(item)
          else:
            name_dict[key] = item
    app_name = []
    if random.choice([True,False]):
      app_name.append(random.choice(name_dict["pre"]))
    app_name.append("Sprite")         #Need to have "Sprite" in the name
    app_name.append(random.choice(name_dict["noun"]))
    if random.choice([True,False]):
      app_name.append(random.choice(name_dict["post"]))
    return " ".join(app_name)

  def load_sprite(self, sprite_filename, random=False):
    if not random:
      print(" Loading Sprite for CLI")

    self.game, self.sprite = gamelib.autodetect(sprite_filename)

    if not random:
      print("  Loaded a \"" + self.sprite.classic_name + "\" Sprite for injection into " + self.game.name + " Game files")
    # Additional GUI stuff

  def save_file_as(self, export_filename):
    # Have a func that we send the filename to for saving
    #  since the GUI has extra dialogue boxes and stuff
    print("   Exporting \"" + self.sprite.classic_name + "\" Sprite as " + os.path.splitext(export_filename)[1].upper() + " to " + export_filename)
    self.sprite.save_as(export_filename)

  def copy_into_ROM(self, inject=False, dest_filename=None, source_filename=None):
    # Have a func that we send the filename to for source/destination
    #  since the GUI has extra dialogue boxes and stuff
    action = ""
    if inject:
      source_filename = dest_filename
      action = "   Injecting into: " + source_filename
    else:
      action = "   Copying using data from: " + source_filename
    rom = self.game.get_rom_from_filename(source_filename)
    same_internal_name = self.game.internal_name == gamelib.autodetect_game_type_from_rom_filename(source_filename)
    is_zsm = "ZSM" in str(rom.get_name())
    if same_internal_name or (is_zsm and self.sprite.classic_name in ["Link","Samus"]):
      modified_rom = self.sprite.inject_into_ROM(rom)
      modified_rom.save(dest_filename, overwrite=True)
      print(action)
      print("    Injected \"" + self.sprite.classic_name + "\" into: " + dest_filename[dest_filename.rfind('\\')+1:])
    else:
      msg = "   Game File does not match " + self.game.same_internal_name + '/'
      msg += self.sprite.classic_name if not random else "random"
      msg += ": " + dest_filename[dest_filename.rfind('\\')+1:]
      print(msg)

  def copy_into_ROM_bulk(self, source_filepath=None):
    # Have a func that we send the filename to for injecting
    #  since the GUI has to ask where the dir with game files is
    inject = True
    if inject:
      pass
    else:
      print("   Unsure if making copies fits this purpose well.")
      print("    Nuke it from orbit.")

    if not source_filepath:
      source_filepath = os.path.join("resources",self.game.internal_name,"gamefiles","inject")
      if not os.path.isdir(source_filepath):
        os.makedirs(source_filepath)

    if not random:
      print("   Injecting \"" + self.sprite.classic_name + "\" into: " + source_filepath)
    else:
      print("   Injecting into: " + source_filepath)

    source_filenames = []
    for r,d,f in os.walk(source_filepath):
      for file in f:
        _,file_extension = os.path.splitext(file)
        if file_extension.lower() in [".sfc",".smc"]:
          source_filenames.append(os.path.join(r,file))
    for source_filename in source_filenames:
      self.copy_into_ROM(inject=inject,dest_filename=source_filename,source_filename=source_filename)

  def get_random_sprite(self, sprite_filepath=None):
    if os.path.exists(sprite_filepath):
      sprite_filenames = []
      if os.path.isdir(sprite_filepath):
        for r,d,f in os.walk(sprite_filepath):
          for file in f:
            _,file_extension = os.path.splitext(file)
            if file_extension.lower() in [".png",".zspr",".sfc",".smc"]:
              sprite_filenames.append(os.path.join(r,file))
      elif os.path.isfile(sprite_filepath):
        sprite_filenames.append(sprite_filepath)
      return random.choice(sprite_filenames)
    else:
      print("Sprite File not found")
      return False

  def randomize_into_ROM(self, inject=False, dest_filename=None, source_filename=None, source_filepath=None, sprite_filepath=None):
#    self.load_sprite(self.get_random_sprite(sprite_filepath=sprite_filepath))
#    self.copy_into_ROM(inject=inject, dest_filename=dest_filename,source_filename=source_filename)
    print("If you got here, it's busted.")
    pass

  def randomize_into_ROM_bulk(self, source_filepath=None, sprite_filepath=None, unique=False):
    used_sprites = []
    source_filenames = []

    for r,d,f in os.walk(source_filepath):
      for file in f:
        _,file_extension = os.path.splitext(file)
        if file_extension.lower() in [".sfc",".smc"]:
          source_filenames.append(os.path.join(r,file))
    for source_filename in source_filenames:
      sprite = self.get_random_sprite(sprite_filepath=sprite_filepath)
      if unique:
        while sprite in used_sprites:
          sprite = self.get_random_sprite(sprite_filepath=sprite_filepath)
        used_sprites.append(sprite)
      print("If you got here, it's busted.")
#      self.load_sprite(sprite)
#      self.copy_into_ROM(inject=True, dest_filename=source_filename,source_filename=source_filename)
