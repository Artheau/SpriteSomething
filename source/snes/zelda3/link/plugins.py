import json
import os
from tkinter import messagebox, filedialog
import tkinter as tk
import re
from functools import partial
from source.meta.common import common
from source.meta.gui import gui_common
from source.meta.classes.pluginslib import PluginsParent
from source.meta.plugins import trawler
from shutil import copy, make_archive, move, rmtree  # file manipulation
from . import equipment

# FIXME: English

class Plugins(PluginsParent):
    def __init__(self, sprite):
        super().__init__(sprite)
        plugins = [
            ("Download ALttPR Official Sprites",None,self.get_alttpr_sprites),
            ("Download SpriteSomething Unofficial Sprites",None,self.get_spritesomething_sprites),
            ("Z3DoI: Save as Archive",None,self.save_doi_as_zip),
            ("Z3DoI: Save to Folder",None,self.save_doi_to_folder),
            ("Z3DoI: Save to Character Slot",None,self.save_doi_to_slot),
            ("Sheet Trawler",None,self.sheet_trawler)#,
            #("Equipment",None,self.equipment_test)
        ]
        self.set_plugins(plugins)

    def equipment_test(self, save=False):
        return equipment.equipment_test(save)

    def get_alttpr_sprites(self):
        success = gui_common.get_sprites(
            self,
            "Official ALttPR",
            "snes/zelda3/link/sheets/official",
            "http://alttpr.com/sprites"
        )
        return success

    def get_spritesomething_sprites(self):
        success = gui_common.get_sprites(
            self,
            "Unofficial SpriteSomething ALttP/Link",
            "snes/zelda3/link/sheets/unofficial",
            "https://miketrethewey.github.io/SpriteSomething-collections/snes/zelda3/link/sprites.json"
        )
        return success

    # create chooser for game files that have multiple sprite options for extraction
    def create_slot_chooser(self, num_slots):
        def choose_sheet(sheet_name):
            sheet_selector.set(sheet_name)
            sheet_chooser.destroy()

        selected_sheet = None

        orig_sheets = [
            "Link",   "Girl", "Monkey",
            "Frog",   "Fox",  "Penguin",
            "Rabbit", "Wolf", "Mouse"
        ]
        sheets = []
        for [slot_id, sheet] in enumerate(orig_sheets):
            sheets.append("Slot " + str(slot_id+1) + f": {orig_sheets[slot_id]}")

        if len(sheets) > 1:
            sheet_chooser = tk.Toplevel()
            #FIXME: English
            sheet_chooser.title("Choose Slot to Save to")
            sheet_chooser.geometry("640x140")
            sheet_selector = tk.StringVar(sheet_chooser)
            sheet_buttons = []
            i = 1
            j = 1
            cols = 3
            for sheet_name in sheets:
                label = os.path.basename(sheet_name)
                sheet_button = tk.Button(
                    sheet_chooser,
                    width=16,
                    height=1,
                    text=label,
                    command=partial(choose_sheet,sheet_name)
                )
                sheet_button.grid(row=i,column=j,sticky=tk.NSEW)
                sheet_buttons.append(sheet_button)
                if j == cols:
                    i += 1
                    j    = 1
                else:
                    j += 1
            sheet_chooser.grid_rowconfigure(0,weight=1)
            sheet_chooser.grid_rowconfigure(cols + 2,weight=1)
            sheet_chooser.grid_columnconfigure(0,weight=1)
            sheet_chooser.grid_columnconfigure(i + 1,weight=1)
            sheet_chooser.wait_window()
            selected_sheet = sheet_selector.get()
        else:
            selected_sheet = random.choice(sheets)
        return selected_sheet

    def save_doi_to_folder(self, mode="folder"):
        if not self.sprite.subtype == "doi":
            return

        zip_slug = ""
        if "sprite.name" in self.sprite.metadata and self.sprite.metadata["sprite.name"] != "":
            zip_slug = self.sprite.metadata["sprite.name"]
        else:
            zip_slug = "unknown"
        zip_slug = common.filename_scrub(zip_slug)

        window_title = "Save to Folder"
        if mode == "zipped":
            window_title += " for Archive"
        if mode == "slot":
            window_title = "Locate Zelda: Dungeons of Infinity Installation"

        zip_dir = filedialog.askdirectory(
            initialdir=os.path.join(
                ".",
                "resources",
                "user",
                self.sprite.resource_subpath,
                "sheets",
                zip_slug
            ),
            title=window_title
        )

        if mode == "slot":
            # get slot number
            slot = self.create_slot_chooser(9)
            slot = re.match(r"(?:Slot )([\d+])(?:[: ]{2})(?:.*)", slot)
            if slot:
                slot = slot.group(1)
            zip_dir = os.path.join(
                zip_dir,
                "data",
                "characters",
                str(slot)
            )

        if zip_dir:
            #FIXME: Make temp files to put into archive
            scratch_dir = os.path.join(zip_dir, "scratch") if mode == "zipped" else zip_dir
            if not os.path.isdir(os.path.join(scratch_dir,"Pal")):
                os.makedirs(os.path.join(scratch_dir,"Pal"))
            sheet_save_path = os.path.join(
                scratch_dir,
                f"sCharacter_{zip_slug}.png"
            )
            sheet_save_success = self.sprite.save_as(sheet_save_path, "zelda3")
            # print(f"Sheet Save: {sheet_save_success} to {sheet_save_path}")

            if sheet_save_success:
                doi_palette_block = self.sprite.get_image("DoI Palette Block")[0]
                palette_save_path = os.path.join(
                    scratch_dir,
                    "Pal",
                    f"sPalette_{zip_slug}.png"
                )
                palette_save_success = doi_palette_block.save(palette_save_path)
                palette_save_success = os.path.isfile(palette_save_path)
                # print(f"Palette Save: {palette_save_success} to {palette_save_path}")

                if palette_save_success:
                    with open(os.path.join(scratch_dir,"metadata.json"), "w") as metadata_file:
                        metadata_file.write(json.dumps(self.sprite.metadata, indent=2))

                    if mode == "zipped":
                        zip_path_slug = os.path.join(
                            zip_dir,
                            os.path.basename(zip_dir)
                        ) + "-doi"
                        # print(f"Ready to zip to: {zip_path_slug}.zip")

                        archive_save_success = make_archive(
                            zip_path_slug,
                            "zip",
                            root_dir=os.path.join(scratch_dir)
                        )
                        rmtree(os.path.join(scratch_dir))
                        messagebox.showinfo(
                            "Save Complete",
                            f"Saved archive to {zip_path_slug}.zip"
                        )
                    else:
                        messagebox.showinfo(
                            "Save Complete",
                            f"Saved files to {zip_dir}"
                        )

    def save_doi_as_zip(self):
        self.save_doi_to_folder(mode="zipped")

    def save_doi_to_slot(self):
        self.save_doi_to_folder(mode="slot")

    def sheet_trawler(self):
        animations = json.load(open(common.get_resource(os.path.join("snes","zelda3","link","manifests"),"animations.json")))
        frames_by_animation = {}
        animations_by_frame = {}
        for ani,dirs in animations.items():                # {"Stand": {"right": [...], "up": [...]}}
            if "$schema" not in ani:
                if ani not in frames_by_animation:
                    frames_by_animation[ani] = {}
                for direction,poses in dirs.items():    # {"right": [{"frames": 0, "tiles": [{"image": "cellID"}]}]}
                    poseID = 0
                    if direction not in frames_by_animation[ani]:
                        frames_by_animation[ani][direction] = {}
                    for pose in poses:                                    # {"frames": 0, "tiles": [{"image": "cellID"}]}
                        if poseID not in frames_by_animation[ani][direction]:
                            frames_by_animation[ani][direction][poseID] = []
                        if "tiles" in pose:
                            for tile in pose["tiles"]:            # {"image": "cellID"}
                                if "image" in tile:
                                    cellID = tile["image"]
                                    if "_shadow" not in cellID.lower() and \
                                        "SWORD" not in cellID and \
                                        "SHIELD" not in cellID:
                                        cell = {
                                            "id": cellID,
                                            "flip": tile["flip"].lower() if "flip" in tile else "",
                                            "crop": tile["crop"] if "crop" in tile else ""
                                        }
                                        if cellID not in animations_by_frame:
                                            animations_by_frame[cellID] = {}
                                        if ani not in animations_by_frame[cellID]:
                                            animations_by_frame[cellID][ani] = {}
                                        if direction not in animations_by_frame[cellID][ani]:
                                            animations_by_frame[cellID][ani][direction] = {}
                                        if poseID not in animations_by_frame[cellID][ani][direction]:
                                            animations_by_frame[cellID][ani][direction][poseID] = []
                                        frames_by_animation[ani][direction][poseID].append(cell)
                                        animations_by_frame[cellID][ani][direction][poseID].append(cell)
                        poseID += 1
        trawler.show_trawler(frames_by_animation,animations_by_frame,False)
