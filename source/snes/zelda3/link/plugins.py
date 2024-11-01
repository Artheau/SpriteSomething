import json
import os
from tkinter import messagebox, filedialog
import tkinter as tk
import re
import tempfile
from functools import partial
from PIL import Image, ImageTk
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
    def create_slot_chooser(self, num_slots=0, orig_sheets=[]):
        def choose_sheet(sheet_name):
            sheet_selector.set(sheet_name)
            sheet_chooser.destroy()

        selected_sheet = None
        sheets = orig_sheets
        images = []

        if len(sheets) > 1:
            sheet_chooser = tk.Toplevel()
            #FIXME: English
            sheet_chooser.title("Choose Slot to Save to")
            sheet_chooser.geometry("640x400")
            sheet_selector = tk.StringVar(sheet_chooser)
            sheet_buttons = []
            i = 1
            j = 1
            cols = 3
            for [sheet_id, sheet] in enumerate(sheets):
                label = f"Slot {sheet_id+1}\n"
                if "sprite.name" in sheet:
                    label += sheet["sprite.name"]
                if "author.name" in sheet:
                    label += "\n"
                    label += sheet["author.name"]
                image = sheet["image"] if "image" in sheet and sheet["image"] else None
                if image:
                    if image.size == (128, 448):
                        row = 1
                        col = 2
                        head_cell = image.crop((16*(col-1),16*(row-1),16*(col),16*(row)))
                        row = 2
                        col = 4
                        body_cell = image.crop((16*(col-1),16*(row-1),16*(col),16*(row)))
                        image = Image.new("RGBA", (16,24), (0,0,0,0))
                        image.paste(body_cell, (0,8), body_cell)
                        image.paste(head_cell, (0,0), head_cell)
                    image = image.resize((image.size[0] * 2, image.size[1] * 2), Image.NEAREST)
                    image = ImageTk.PhotoImage(image)
                    images.append(image)
                side = tk.BOTTOM
                sheet_button = tk.Button(
                    sheet_chooser,
                    width=24,
                    height=6,
                    image=image,
                    text=label,
                    compound=side,
                    command=partial(choose_sheet,sheet_id)
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

        tempdir = None
        tempdirObj = None
        zip_slug = ""
        if "sprite.name" in self.sprite.metadata and self.sprite.metadata["sprite.name"] != "":
            zip_slug = self.sprite.metadata["sprite.name"]
        else:
            zip_slug = "unknown"
        zip_slug = common.filename_scrub(zip_slug)

        window_title = "Save to Folder"
        if mode == "zipped":
            window_title += " for Archive"
            tempdirObj = tempfile.TemporaryDirectory()
            print("Zip Temp Dir:", tempdirObj)
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
            preview_path = os.path.join("resources", "app", self.sprite.resource_subpath, "sheets", "doi", "bundled")
            orig_sheets = [
                { "sprite.name": "Link",            "author.name": "Nintendo",                  "image": Image.open(os.path.join(preview_path, "link.png")) },
                { "sprite.name": "BS Girl",         "author.name": "InTheBeef",                 "image": Image.open(os.path.join(preview_path, "bsgirl.png")) },
                { "sprite.name": "Monkey",          "author.name": "",                          "image": Image.open(os.path.join(preview_path, "link.png")) },
                { "sprite.name": "Frog Link",       "author.name": "",                          "image": Image.open(os.path.join(preview_path, "frog.png")) },
                { "sprite.name": "Fox Link",        "author.name": "InTheBeef",                 "image": Image.open(os.path.join(preview_path, "fox.png")) },
                { "sprite.name": "Penguin Link",    "author.name": "Fish_waffle64",             "image": Image.open(os.path.join(preview_path, "penguin.png")) },
                { "sprite.name": "Super Bunny",     "author.name": "TheOkayGuy",                "image": Image.open(os.path.join(preview_path, "superbunny.png")) },
                { "sprite.name": "Wolf Link",       "author.name": "Fish_waffle64/InTheBeef",   "image": Image.open(os.path.join(preview_path, "wolf.png")) },
                { "sprite.name": "Mouse",           "author.name": "Malthaez",                  "image": Image.open(os.path.join(preview_path, "mouse.png")) }
            ]
            characters_dir = os.path.join(zip_dir, "data", "characters")
            for d in os.listdir(characters_dir):
                if d.isnumeric() and int(d) >= 1 and int(d) <= 9:
                    slot_dir = os.path.join(characters_dir, d)
                    metadata_path = os.path.join(slot_dir, "metadata.json")
                    if os.path.isfile(metadata_path):
                        with open(metadata_path, "r") as metadata_file:
                            metadata_json = json.load(metadata_file)
                            orig_sheets[int(d) - 1] = metadata_json
                    for f in os.listdir(slot_dir):
                        if os.path.splitext(f)[1] == ".png":
                            sprite_sheet = Image.open(os.path.join(slot_dir, f))
                            orig_sheets[int(d) - 1]["image"] = sprite_sheet

            # get slot number
            slot = self.create_slot_chooser(9, orig_sheets)
            slot = re.match(r"(?:Slot )([\d+])(?:[: ]{2})(?:.*)", slot)
            if slot:
                slot = slot.group(1)
                zip_dir = os.path.join(
                    zip_dir,
                    "data",
                    "characters",
                    str(slot)
                )
            else:
                zip_dir = None

        if tempdirObj:
            tempdir = tempdirObj.name
        else:
            tempdir = zip_dir

        if tempdir:
            #FIXME: Make temp files to put into archive
            if not os.path.isdir(os.path.join(tempdir,"Pal")):
                os.makedirs(os.path.join(tempdir,"Pal"))
            sheet_save_path = os.path.join(
                tempdir,
                f"sCharacter_{zip_slug}.png"
            )
            sheet_save_success = self.sprite.save_as(sheet_save_path, "zelda3")
            # print(f"Sheet Save: {sheet_save_success} to {sheet_save_path}")

            if sheet_save_success:
                doi_palette_block = self.sprite.get_image("DoI Palette Block")[0]
                palette_save_path = os.path.join(
                    tempdir,
                    "Pal",
                    f"sPalette_{zip_slug}.png"
                )
                palette_save_success = doi_palette_block.save(palette_save_path)
                palette_save_success = os.path.isfile(palette_save_path)
                # print(f"Palette Save: {palette_save_success} to {palette_save_path}")

                if palette_save_success:
                    with open(os.path.join(tempdir,"metadata.json"), "w") as metadata_file:
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
                            root_dir=os.path.join(tempdir)
                        )
                        # print("Archive Success:",archive_save_success)

                        if archive_save_success:
                            messagebox.showinfo(
                                "Save Complete",
                                f"Saved archive to {zip_path_slug}.zip"
                            )
                            tempdirObj.cleanup()
                    else:
                        messagebox.showinfo(
                            "Save Complete",
                            f"Saved files to {tempdir}"
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
