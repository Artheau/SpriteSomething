# pylint: disable=fixme
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=no-self-use
"""
Runs the CLI interface for SpriteSomething
"""
import json    #for reading JSON
import os      #for filesystem manipulation
import random  #for choosing random app titles, random game files & random sprites
import sys     # exit
from json.decoder import JSONDecodeError
from source.meta.common import common
from source.meta.common import constants as CONST
from source.meta.gui import gamelib
from source.meta.gui.gui_common import get_sprites
from source.meta import ssDiagnostics as diags

def make_CLI(command_line_args):
    """run CLI"""
    print(command_line_args)
    CLIMainFrame(command_line_args)

class CLIMainFrame():
    """make a class that's similar to the GUI class"""
    # FIXME: Filled with English

    def mode_diag(self):
        """Run SpriteSomething diagnostics"""
        print("\n".join(diags.output()))
        return 0
        # sys.exit(0)
    def mode_convert(self, command_line_args):
        """Convert a batch of sprite files of like type to like type"""
        src_filepath = command_line_args["src-filepath"] if "src-filepath" in command_line_args and command_line_args["src-filepath"] is not None else "."
        convert_from = command_line_args["convert-from"] if "convert-from" in command_line_args and command_line_args["convert-from"] is not None else "zspr"
        convert_to = command_line_args["convert-to"] if "convert-to" in command_line_args and command_line_args["convert-to"] is not None else "rdc"

        if convert_from.startswith("."):
            convert_from = convert_from[1:]
        if convert_to.startswith("."):
            convert_to = convert_to[1:]

        for filename in os.listdir(os.path.join(src_filepath)):
            if os.path.isfile(os.path.join(src_filepath, filename)) and os.path.splitext(filename)[1][1:] == convert_from:
                self.load_sprite(os.path.join(src_filepath, filename))
                self.save_file_as(os.path.join(src_filepath, filename).replace(f".{convert_from}", f".{convert_to}"))
    def mode_export(self, export_filename):
        """Export sprite"""
        export_filename = export_filename if export_filename is not None and export_filename != "None" else "export.png"
        self.save_file_as(export_filename)
        return 0
    def mode_inject(self, mode, command_line_args):
        """Inject sprite"""
        dest_default_path = os.path.join("resources","user",self.game.console_name,self.game.internal_name,"gamefiles","export")    #default export location | user_resources/snes/zelda3/gamefiles/export/*.*
        source_default_path = os.path.join("resources","user",self.game.console_name,self.game.internal_name,"gamefiles","source")    #default source location | user_resources/snes/zelda3/gamefiles/source/*.*
        dest_filename = os.path.join(dest_default_path,"export")    # user_resources/zelda3/gamefiles/export/export.*
        source_filename = os.path.join(source_default_path,self.game.internal_name)    # user_resources/zelda3/gamefiles/source/zelda3.*

        if not os.path.isdir(dest_default_path):    #make directories to get the designated destination if necessary
            os.makedirs(dest_default_path)

        dest_filename = "dest-filename" in command_line_args and command_line_args["dest-filename"] or dest_filename    #if we've provide a destination, set it
        source_filename = "src-filename" in command_line_args and command_line_args["src-filename"] or source_filename    #if we've provided a source, set it
        if "-bulk" in mode:    #if we're injecting into many game files
            # SpriteSomething.[py|exe] --cli=1 --mode=inject-bulk --src-filepath=resources/zelda3/gamefiles/inject
            source_filepath = os.path.join("resources","user",self.game.console_name,self.game.internal_name,"gamefiles","inject")    #default inject location | user_resources/snes/zelda3/gamefiles/inject/*.*
            source_filepath = "src-filepath" in command_line_args or source_filepath    #if we've provided a source directory, set it
            if "-random" in mode:    #if we're injecting random sprites, get the directory
                sprite_filepath = "spr-filepath" in command_line_args or None
                # SpriteSomething.[py|exe] --cli=1 --mode=inject-bulk-random --src-filepath=user_resources/zelda3/gamefiles/inject \
                #    --spr-filepath=resource/zelda3/link/official
                if sprite_filepath is None:
                    print("   Sprite filepath not provided!")
                    return 1
                    # sys.exit(1)
                self.randomize_into_ROM_bulk(source_filepath=source_filepath, sprite_filepath=sprite_filepath)
            else:
                self.copy_into_ROM_bulk(source_filepath=source_filepath)
        elif "-random" in mode:    #we're injecting a random sprite into one game file
            sprite_filepath = "spr-filepath" in command_line_args and command_line_args["spr-filepath"] or None
            if sprite_filepath is None:
                print("   Sprite filepath not provided!")
                return 1
                # sys.exit(1)
            self.randomize_into_ROM(
                inject=True,
                # dest_filename=dest_filename,
                # source_filename=source_filename,
                # source_filepath=source_filepath,
                # sprite_filepath=sprite_filepath
            )
        else:    #we're injecting the loaded sprite into one game file
            if not isinstance(source_filename, str):
                print("   Source filepath not provided!")
                return 1
                # sys.exit(1)
            if not os.path.isfile(source_filename) and not os.path.isfile(source_filename + ".sfc"):
                #check that the provided source exists, if not, nuke it from orbit
                print(f"     Source File does not exist: {source_filename}")
                print(f"     Source File does not exist: {source_filename}.sfc")
                print("      Nuke it from orbit.")
                return 1
                # sys.exit(1)
            if not os.path.splitext(source_filename)[1]:    #if we don't have a file extension, default to *.sfc
                source_filename += ".sfc"
            if not os.path.splitext(dest_filename)[1]:    #if we don't have a file extension, default to *.sfc
                dest_filename += ".sfc"
            self.copy_into_ROM("-new" not in mode,dest_filename,source_filename)    #if we're injecting "-new", make a copy
    def mode_get(self, mode):
        """Download Sprites"""
        print("    Downloading Sprites")    #get ALttPR sprites
        if mode == "get-alttpr-sprites":
            # SpriteSomething.[py|exe] --cli=1 --mode=get-alttpr-sprites
            self.load_sprite(os.path.join("resources","app","snes","zelda3","link","sheets","link.zspr"))    #load Link
            get_sprites(self,"Official ALttPR","snes/zelda3/link/sheets/official","http://alttpr.com/sprites",False)    #get ALttPR sprites; # FIXME: Do we want this in the sprite class or somewhere else?

    def __init__(self, command_line_args):
        print(f"{self.create_random_title()} {CONST.APP_VERSION}")    #print title & version
        print("")    #newline
        print("Initializing CLIMainFrame")    #we made it, we're starting!
        if command_line_args["mode"]:    #get the mode
            mode = command_line_args["mode"]
            if mode[:4] == "diag":    #run diagnostics & exit; SpriteSomething.[py|exe] --cli=1 --mode=diag
                self.mode_diag()
                return
                # return 0
            else:
                self.load_sprite(command_line_args["sprite"])    #we're loading a sprite!

                if mode == "export":    #we're exporting as PNG/ZSPR/RDC based on the filetype provided, default to "export.png"
                    # SpriteSomething.[py|exe] --cli=1 --mode=export --export-filename=export.[png|zspr|rdc]
                    self.mode_export(command_line_args["export-filename"])
                    return
                    # return 0
                elif mode == "convert":
                    self.mode_convert(command_line_args)
                    return
                elif "inject" in mode:    #we're injecting a [single|random] sprite into game file(s)
                    # SpriteSomething.[py|exe] --cli=1 --mode=inject --dest-filename=resources/zelda3/gamefiles/export/export.sfc \
                    #    --source-filename=resources/zelda3/gamefiles/source/zelda3.sfc
                    self.mode_inject(mode, command_line_args)
                    return
                    # return 0

                elif "get-" in mode and "-sprites" in mode:    #get sprites
                    self.mode_get(mode)
                    return
                    # return 0
                else:
                    print("No valid CLI Mode provided")
        else:
            print("No CLI Mode provided")

    def create_random_title(self):
        """Generate a new epic random title for this application"""
        name_dict = {}
        for filename in common.get_all_resources(["meta","manifests"],"app_names.json"):
            with open(filename, encoding="utf-8") as name_file:
                nameJSON = {}
                try:
                    nameJSON = json.load(name_file)
                except JSONDecodeError as e:
                    raise ValueError("AppName JSON malformed!")
                for key,item in nameJSON.items():
                    if "$" not in key and key in name_dict:
                        name_dict[key].extend(item)
                    else:
                        name_dict[key] = item
        app_name = []
        if random.choice([True,False]):
            app_name.append(random.choice(name_dict["pre"]))
        app_name.append("Sprite")                 #Need to have "Sprite" in the name
        app_name.append(random.choice(name_dict["noun"]))
        if random.choice([True,False]):
            app_name.append(random.choice(name_dict["post"]))
        return " ".join(app_name)

    def load_sprite(self, sprite_filename, random=False):
        """
        #load sprite
        # Inbound:
        #    sprite_filename: Filename of sprite to load
        #    random: Include messages indicating that we're processing a random sprite
        """
        print(f" Loading {'Random' if random else ''}Sprite for CLI")

        self.game, self.sprite, self.animation_engine = gamelib.autodetect(sprite_filename)

        print(f"  Loaded a \"{self.sprite.classic_name}\" Sprite for injection into {self.game.name} Game files")
        # Additional GUI stuff

    def save_file_as(self, export_filename):
        """
        # Have a func that we send the filename to for saving
        #    since the GUI has extra dialogue boxes and stuff
        """
        print(f"   Exporting '{self.sprite.classic_name}' Sprite as {os.path.splitext(export_filename)[1].upper()} to {export_filename}")
        self.sprite.save_as(export_filename, self.game.name)

    def copy_into_ROM(self, inject=False, dest_filename=None, source_filename=None):
        """
        #inject/copy loaded sprite into game file
        # Inbound:
        #    inject: Are we injecting directly or making a copy?
        #    dest_filename: Destination filename for game file
        #    source_filename: Source filename for game file to copy from
        # Have a func that we send the filename to for source/destination
        #    since the GUI has extra dialogue boxes and stuff
        """
        action = ""
        if inject:    #if we're injecting, the source & destination are the same
            source_filename = dest_filename
            action = "     Injecting into: " + source_filename
        else:    #else, make a copy
            action = "     Copying using data from: " + source_filename
        rom = self.game.get_rom_from_filename(source_filename)    #read ROM data
        same_internal_name = self.game.internal_name == gamelib.autodetect_game_type_from_rom_filename("snes",source_filename)[0]    #the game file matches
        is_zsm = "ZSM" in str(rom.get_name())    #this is a ZSM game file
        if same_internal_name or (is_zsm and self.sprite.classic_name in ["Link","Samus"]):    #if we've got a compatible game file, inject it!
            modified_rom = self.sprite.inject_into_ROM(self.animation_engine.spiffy_dict, rom)
            modified_rom.save(dest_filename, overwrite=True)
            print(action)
            print("        Injected \"%s\" into: %s" % (self.sprite.classic_name, dest_filename[dest_filename.rfind('\\')+1:]))
        else:
            msg = (f"     Game File does not match {same_internal_name}/") #oops, it doesn't match
            msg += self.sprite.classic_name if not random else "random"
            msg += ": " + dest_filename[dest_filename.rfind('\\')+1:]
            print(msg)

    def copy_into_ROM_bulk(self, source_filepath=None):
        """
        #like above but for list of files
        # Have a func that we send the filename to for injecting
        #    since the GUI has to ask where the dir with game files is
        """
        inject = True
        if inject:    #only injection is supported, and it's forced at this time # FIXME: Maybe don't force it?
            pass
        else:
            print("     Unsure if making copies fits this purpose well.")
            print("      Nuke it from orbit.")

        if not source_filepath:    #default source filepath | resources/snes/zelda3/gamefiles/inject/*.*
            source_filepath = os.path.join("resources","user",self.game.console_name,self.game.internal_name,"gamefiles","inject")
            if not os.path.isdir(source_filepath):    #if directory doesn't exist, make it
                os.makedirs(source_filepath)

        print(f"   Injecting \"{self.sprite.classic_name}\" into: {source_filepath}")

        source_filenames = []    #walk through the game files and inject the loaded sprite
        if not isinstance(source_filepath, str):
            print("    Source filepath not provided!")
            return
            # sys.exit(1)
        for r,_,f in os.walk(source_filepath):
            for file in f:
                _,file_extension = os.path.splitext(file)
                if file_extension.lower() in [".sfc",".smc"]:
                    source_filenames.append(os.path.join(r,file))
        for source_filename in source_filenames:
            self.copy_into_ROM(inject=inject,dest_filename=source_filename,source_filename=source_filename)

    def get_random_sprite(self, sprite_filepath=None):
        """
        #pick a random sprite and return the filename; accepts PNG/ZSPR/SFC/SMC/RDC
        # Inbound:
        #    sprite_filepath: Directory of sprites to select from
        """
        if os.path.exists(sprite_filepath):
            sprite_filenames = []
            if os.path.isdir(sprite_filepath):
                for r,_,f in os.walk(sprite_filepath):
                    for file in f:
                        _,file_extension = os.path.splitext(file)
                        if file_extension.lower() in [
                            #FIXME: Supported filetypes
                            ".png",     # Main input
                            ".4bpp",    # Raw
                            ".zspr",    # Z3Link
                            ".sfc",     # SNES
                            ".smc",     # SNES
                            ".nes",     # NES
                            ".gbc",     # GBC
                            ".gb",      # GB
                            ".bmp",     # FFMQBen
                            ".zip",     # Mo3Player
                            ".aspr",    # ASPR (WIP)
                            ".zhx",     # ZHX (WIP)
                            ".rdc"      # Z3Link/M3Samus
                        ]:
                            sprite_filenames.append(os.path.join(r,file))
            elif os.path.isfile(sprite_filepath):
                sprite_filenames.append(sprite_filepath)
            return random.choice(sprite_filenames)
        print("Sprite File not found")
        return False

    def randomize_into_ROM(
        self,
        # inject=False,
        # dest_filename=None,
        # source_filename=None,
        # source_filepath=None,
        # sprite_filepath=None
    ):
        """
        #try to randomize a sprite and inject it
        # Inbound:
        #    inject: Are we injecting directly or making a copy?
        #    dest_filename: Destination filename of game file
        #    source_filename: Source filename to make a copy from
        #    source_filepath: Directory of source game files
        #    sprite_filepath: Directory of sprite files
        """
#        self.load_sprite(self.get_random_sprite(sprite_filepath=sprite_filepath))
#        self.copy_into_ROM(inject=inject, dest_filename=dest_filename,source_filename=source_filename)
        print("If you got here, it's busted.")

    def randomize_into_ROM_bulk(self, source_filepath=None, sprite_filepath=None, unique=False):
        """
        #try to randomize a sprite and inject it
        #like above but for list of files
        """
        used_sprites = []
        source_filenames = []

        for r,_,f in os.walk(source_filepath):
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
#            self.load_sprite(sprite)
#            self.copy_into_ROM(inject=True, dest_filename=source_filename,source_filename=source_filename)
