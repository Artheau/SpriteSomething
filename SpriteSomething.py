from argparse import ArgumentParser
from source.cli import make_CLI
from source.gui import make_GUI
from tkinter import messagebox   #for the error box in case of fatal error
import traceback #for error box
import os

def main():
	command_line_args = process_command_line_args()
	isCLI = command_line_args["cli"]
	isDiags = "mode" in command_line_args and not command_line_args["mode"] == None and command_line_args["mode"][:4] == "diag"
	if not isCLI and not isDiags:
		run_GUI(command_line_args)
	else:
		process_CLI(command_line_args)

def run_GUI(command_line_args):
	try:
		make_GUI(command_line_args)
	except Exception as ex:
		messagebox.showerror(   "FATAL ERROR",
								f"While running, encountered fatal error: {type(ex).__name__.upper()}\n\n" +
								f"{ex.args}\n\n"+
								f"{traceback.format_exc()}"
								)

def process_command_line_args():
	parser = ArgumentParser()
	parser.add_argument("--cli",
						dest="cli",
						help="Running via commandline",
						metavar="<cli>",
						default=None
	)
	parser.add_argument("--mode",
						dest="mode",
						help="CLI Mode",
						metavar="<mode>",
						default=None)
	parser.add_argument("--export-filename",
						dest="export-filename",
						help="Filename to Export sprite to",
						metavar="<export_filename>",
						default=None)
	parser.add_argument("--dest-filename",
						dest="dest-filename",
						help="Destination Filename for Single Game File",
						metavar="<dest_filename>",
						default=None)
	parser.add_argument("--src-filename",
						dest="src-filename",
						help="Source Filename for Game File Data",
						metavar="<src_filename>",
						default=None)
	parser.add_argument("--src-filepath",
						dest="src-filepath",
						help="Source Filepath for directory of Game Files",
						metavar="<src_filepath>",
						default=None)
	parser.add_argument("--spr-filepath",
						dest="spr-filepath",
						help="Source Filepath for directory of Sprite Files",
						metavar="<spr_filepath>",
						default=None)
	parser.add_argument("--sprite",
						dest="sprite",
						help="A sprite file to load upon opening",
						metavar="<sprite_filename>",
						default=os.path.join("resources","metroid3","samus","samus.png"))
#						default=os.path.join("resources","zelda3","link","link.zspr"))

	command_line_args = vars(parser.parse_args())
	return command_line_args

def process_CLI(command_line_args):
	make_CLI(command_line_args)

if __name__ == "__main__":
	main()
