import colorsys
import json
import os
from tkinter import messagebox, filedialog
import tkinter as tk
import re
import tempfile
import time
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
            ("Z3DoI: Convert GBR -> GBRY",None,self.convert_gbr_gbry),
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
                    width=150,
                    height=100,
                    image=image,
                    text=label,
                    compound=side,
                    command=partial(choose_sheet,sheet_id)
                )
                sheet_button.grid(row=i,column=j,sticky=tk.NSEW)
                sheet_buttons.append(sheet_button)
                if j == cols:
                    i += 1
                    j  = 1
                else:
                    j += 1
            sheet_chooser.grid_rowconfigure(0,weight=1)
            sheet_chooser.grid_rowconfigure(cols + 2,weight=1)
            sheet_chooser.grid_columnconfigure(0,weight=1)
            sheet_chooser.grid_columnconfigure(i + 1,weight=1)
            sheet_chooser.wait_window()
            if sheet_selector.get():
                selected_sheet = int(sheet_selector.get()) + 1
        else:
            selected_sheet = int(random.choice(sheets)) + 1
        print(f"Saving to DoI Slot: {selected_sheet}")
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

        if zip_dir:
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
                        for f in os.listdir(slot_dir):
                            if os.path.splitext(f)[1] == ".png":
                                sprite_sheet = Image.open(os.path.join(slot_dir, f))
                                orig_sheets[int(d) - 1] = {"image": sprite_sheet}
                        if os.path.isfile(metadata_path):
                            with open(metadata_path, "r") as metadata_file:
                                metadata_json = json.load(metadata_file)
                                orig_sheets[int(d) - 1].update(metadata_json)
                # get slot number
                slot = self.create_slot_chooser(9, orig_sheets)
                if slot and int(slot) > 0:
                    backups_dir = os.path.join(zip_dir,"data","characters","backups")
                    if not os.path.isdir(backups_dir):
                        os.makedirs(backups_dir)
                    zip_dir = os.path.join(
                        zip_dir,
                        "data",
                        "characters",
                        str(slot)
                    )
                    if os.path.isdir(zip_dir):
                        for r,d,f in os.walk(zip_dir):
                            for filename in f:
                                if os.path.splitext(filename)[1] == ".png":
                                    blast_sprite = messagebox.askyesno(
                                        f"Save to Slot {str(slot)}",
                                        "Wait a little bit, dude, there's already a sprite there." + "\n\n" +
                                        "Are you a bad enough dude to blast it anyway?"
                                    )
                                    if blast_sprite:
                                        backup_sprite = messagebox.askyesno(
                                            f"Save to Slot {str(slot)}",
                                            "Okay. I'm chargin' Malaysia to blast it away!" + "\n\n" +
                                            "Do you want to back that thang up so that you can save a copy of what's already there?"
                                        )
                                        if backup_sprite:
                                            backup_path_slug = os.path.splitext(filename)[0].replace("sCharacter_","")
                                            backup_path = os.path.join(backups_dir,backup_path_slug)
                                            backup_path += time.strftime("_%Y%m%dT%H%M%S", time.gmtime())
                                            backup_save_success = make_archive(
                                                backup_path,
                                                "zip",
                                                root_dir=os.path.join(zip_dir)
                                            )
                                            if backup_save_success:
                                                print(f"Backup saved to: {backup_path}")
                                        rmtree(zip_dir)
                                    else:
                                        return
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

    def convert_gbr_gbry(self):
        masterp = self.sprite.master_palette
        paletteNames = ["green", "blue", "red"]
        palNames = [
            ["green", "blue"],
            ["blue", "red"]
        ]
        if len(masterp) > 16 * 4:
            paletteNames.append("yellow")
            palNames.append(["red", "yellow"])
        paletteNames.append("bunny")
        palettes = {}
        for paletteID, paletteName in enumerate(paletteNames):
            palettes[paletteName] = masterp[paletteID*16:(paletteID+1)*16]
        for [palNameOne, palNameTwo] in palNames:
            print(f"Comparing {palNameOne} to {palNameTwo}")
            i = 0
            for [one, two] in zip(
                palettes[palNameOne],
                palettes[palNameTwo]
            ):
                o_hsv = list(
                    colorsys.rgb_to_hsv(
                        one[0]/255,
                        one[1]/255,
                        one[2]/255
                    )
                )
                t_hsv = list(
                    colorsys.rgb_to_hsv(
                        two[0]/255,
                        two[1]/255,
                        two[2]/255
                    )
                )
                o_hsv[0] = round(float(o_hsv[0]) * 360)
                o_hsv[1] = round(float(o_hsv[1]) * 100)
                o_hsv[2] = round(float(o_hsv[2]) * 100)
                t_hsv[0] = round(float(t_hsv[0]) * 360)
                t_hsv[1] = round(float(t_hsv[1]) * 100)
                t_hsv[2] = round(float(t_hsv[2]) * 100)
                if (i > 0) and (o_hsv != t_hsv):
                    print(i,o_hsv,t_hsv)
                i += 1

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
