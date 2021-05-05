from tkinter import Tk, Button, Frame, OptionMenu, StringVar, Toplevel, messagebox, LEFT, Y, N
from functools import partial
import os
from source.meta.common import common
import source.meta.gui.widgets as widgets

def show_trawler(frames_by_animation,animations_by_frame,overhead):
	cyan = "#00CAFF"
	green = "#00FF7A"
	yellow = "#FFFF00"
	default = ""

	def on_enter(e):
		if e.widget["background"] == default:
			e.widget["background"] = yellow
	def on_leave(e):
		if e.widget["background"] == yellow:
			e.widget["background"] = default

	def show_cell_data(itemID="A0", lookup="byFrame"):
		title = ""
		msg = ""
		process_cells = len(cell_buttons) > 0
		if lookup == "byFrame":
			title = itemID
			if process_cells and itemID in cell_buttons:
				for _,button in cell_buttons.items():
					bg = button.cget("bg")
					if bg != green:
						button.configure(bg=default)
						button.update()
				cell_buttons[itemID].configure(bg=cyan)
				cell_buttons[itemID].update()
			for animation,directions in animations_by_frame[itemID].items():
				for direction,frames in directions.items():
					msg += "> " + animation + " "
					msg += "(" + direction + ")\n"
					msg += ">> Poses: "
					for frameID, frame in frames.items():
						for cell in frame:
							msg += str(frameID + 1)
							if "flip" in cell and cell["flip"] != "":
								msg += " " + cell["flip"] + "-flipped"
							if "crop" in cell and cell["crop"] != "":
								crop = "[" + ",".join(map(str,cell["crop"])) + "]"
								switcher = {
									"[0,0,16,8]": "Top",
									"[0,0,8,8]": "Top Left",
									"[8,0,16,8]": "Top Right",
									"[0,0,8,16]": "Left",
									"[8,0,16,16]": "Right",
									"[0,8,16,16]": "Bottom",
									"[0,8,8,16]": "Bottom Left",
									"[8,8,16,16]": "Bottom Right"
								}
								crop = switcher.get(crop,crop)
								msg += " " + crop
							msg += "; "
					msg += "\n"
				msg += "\n"
		elif lookup == "byAnim":
			animation = itemID.split(":")[0]
			direction = itemID.split(":")[1]
			directions = frames_by_animation[animation]
			if overhead:
				if "_" in direction:
					aim = direction.split("_")[0]
					direction = direction.split("_")[1]
					direction = direction + "_aim_diag_" + aim
			if direction + "_aim_shoot" in directions:
				direction = direction + "_aim_shoot"
			if direction not in directions:
				if direction == "neutral" and "right" in directions:
					direction = "right"
				elif direction == "up" and "right_aim_up" in directions:
					direction = "right_aim_up"
				elif direction == "down" and "right_aim_down" in directions:
					direction = "right_aim_down"
				elif "right" in directions:
					direction = "right"
				else:
					direction = list(directions.keys())[0]
			title = animation + " (" + direction + ")"
			frames = directions[direction]
			if process_cells:
				for cellID,button in cell_buttons.items():
					bg = button.cget("bg")
					if bg != cyan:
						button.configure(bg=default)
						button.update()
			for frameID, frame in frames.items():
				msg += "> Pose: " + str(frameID + 1) + "\n"
				msg += ">> Cells: "
				for cell in frame:
					msg += cell["id"]
					if process_cells and cell["id"] in cell_buttons:
						cell_buttons[cell["id"]].configure(bg=green)
						cell_buttons[cell["id"]].update()
					if "flip" in cell and cell["flip"] != "":
						msg += " " + cell["flip"] + "-flipped"
					msg += "; "
				msg += "\n\n"
		widgets.make_messagebox("info",title,msg,parent=trawler)

	def show_ani_data(direction):
		animation = self.widgets["animation_display"].storageVar.get()
		show_cell_data(itemID=animation + ":" + direction, lookup="byAnim")

	dims = {
		"text": {
			"width": 4,
			"height": 1
		},
		"image": {
			"width": 20,
			"height": 20
		}
	}

	trawler = Toplevel()
	trawler.title("Sheet Trawler")
	trawler.geometry("1024x768")
	default = trawler.cget("bg")

	self = widgets.make_frame(trawler)

	self.widgets = {}
	self.frames = {}

	cell_buttons = {}
	if "A0" in animations_by_frame:
		letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		disabled = [
			"D5","D6",
			"E0","E1",
			"G5","G6",
			"K5",
			# "P0", # P0 right half
			"Q2","Q3","Q4",
			"R3","R4","R5",
			"V7",
			"W0","W1","W2","W3","W4","W5","W6","W7",
			"X0",
			"Z1", # "Z6" # Z6: lower right quarter
			"AB5","AB6","AB7"
		]

		# Cell Grid, click a cell for animations that use that cell
		cell_grid = Frame(trawler)
		for letter in letters:
			for i in range(0,7+1):
				cell_name = letter + str(i)
				cell_button = widgets.make_button(
					cell_grid,
					cell_name,
					partial(show_cell_data,cell_name),
					{
						"width": dims["text"]["width"],
						"height": dims["text"]["height"],
						"state": "disabled" if cell_name in disabled else "active"
					}
				)
				cell_button.bind("<Enter>", on_enter)
				cell_button.bind("<Leave>", on_leave)
				cell_button.grid(row=letters.index(letter),column=i)
				cell_buttons[cell_name] = cell_button
		letters = [ "AA", "AB" ]
		for letter in letters:
			lstr = ""
			for i in range(0,7+1):
				cell_name = letter + str(i)
				cell_button = widgets.make_button(
					cell_grid,
					cell_name,
					partial(show_cell_data,cell_name),
					{
						"width": dims["text"]["width"],
						"height": dims["text"]["height"],
						"state": "disabled" if cell_name in disabled else "active"
					}
				)
				cell_button.bind("<Enter>", on_enter)
				cell_button.bind("<Leave>", on_leave)
				cell_button.grid(row=letters.index(letter)+26,column=i)
				cell_buttons[cell_name] = cell_button
		cell_grid.pack(side=LEFT, anchor=N)

		# Display info about selected cell
		self.frames["cell_display"] = widgets.make_frame(trawler)
		thiswidget = {
			"cell_display": {
				"type": "selectbox",
				"default": "index",
				"options": {
					# "Vanilla Link": "vanilla",
					"Index labels": "index",
					# "Currently loaded sprite": "loaded"
				}
			}
		}
		dict_widgets = widgets.make_widgets_from_dict({}, thiswidget, self.frames["cell_display"])
		for key in dict_widgets:
			self.widgets[key] = dict_widgets[key]
			self.widgets[key].pack()
		self.frames["cell_display"].pack(side=LEFT, anchor=N)

	# Display info about selected animation
	self.frames["animation_display"] = widgets.make_frame(trawler)
	thiswidget = {
		"animation_display": {
			"type": "selectbox",
			"options": {}
		}
	}

	directions = ["down","left","up","right"]
	if overhead:
		directions = ["down","down_left","left","up_left","up","up_right","right","down_right","neutral"]

	for direction in directions:
		text = direction
		img = "arrow-" + direction.replace("_","") + ".png"
		if direction == "neutral":
			img = "no-thing.png"
		thiswidget[direction] = {
			"type": "button",
			"label": {
				"text": text
			},
			"options": {
				"image": common.get_resource(
					["meta","icons"],
					img
				),
				"width": dims["image"]["width"],
				"height": dims["image"]["height"],
				"compound": "none"
			}
		}
	for ani in frames_by_animation.keys():
		thiswidget["animation_display"]["options"][ani] = ani

	dict_widgets = widgets.make_widgets_from_dict(self, thiswidget, self.frames["animation_display"])
	for key in dict_widgets:
		self.widgets[key] = dict_widgets[key]
		if self.widgets[key].type == "button":
			self.widgets[key].config(command=partial(show_ani_data,key))
		self.widgets[key].pack(side=LEFT)
	self.frames["animation_display"].pack(side=LEFT, anchor=N)
