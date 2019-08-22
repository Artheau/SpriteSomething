from argparse import ArgumentParser	#to read stuff from commandline
from source.cli import make_CLI		#import commandline interface
from source.gui import make_GUI		#import visual interface
from tkinter import messagebox		#for the error box in case of fatal error
import traceback					#for error box
import os							#for default file to load

#main entry point
def main():
	command_line_args = process_command_line_args()	#get commandline args
	isCLI = command_line_args["cli"]				#determine if we're running the CLI
	isDiags = "mode" in command_line_args and not command_line_args["mode"] == None and command_line_args["mode"][:4] == "diag"	#determine if we're running diagnostics
	if not isCLI and not isDiags:
		run_GUI(command_line_args)	#if we're not running the CLI and not diagnostics, launch the GUI
	else:
		process_CLI(command_line_args)	#else, launch the CLI

#run the GUI, throw exception if we have any
def run_GUI(command_line_args):
	try:
		make_GUI(command_line_args)
	except Exception as ex:
		messagebox.showerror(   "FATAL ERROR",
								f"While running, encountered fatal error: {type(ex).__name__.upper()}\n\n" +
								f"{ex.args}\n\n"+
								f"{traceback.format_exc()}"
								)

#get commandline keys/values
# Inbound:
#  --cli: Are we gonna run the commandline interface?
#   Default: None
#  --mode: CLI Mode
#   Default: None
#   diag[nostics]:	Run Diagnostics report
#   export:					Export as PNG/ZSPR/RDC
#   inject:					Inject directly into a game file
#   *-bulk:					Inject directly into multiple game files (doesn't support copies)
#   *-random:				Randomize sprite file injected into game files
#   get-*-sprites:	Download sprites
#   get-alttpr-sprites:	Download Official ALttPR Sprites
#  --export-filename:	During mode:export, provide filename to export to (PNG/ZSPR/RDC)
#  --dest-filename:		During mode:inject, provide filename of game file to inject into
#  --src-filename:		During mode:inject, provide filename of game file to use as a source document to copy from
#  --src-filepath:		During mode:inject-bulk, provide directory of game files to inject into
#  --spr-filepath:		During mode:inject*, provide directory of sprite files to randomly select to inject
#  --sprite:					Sprite file to open on first load of the app
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
#						default=os.path.join("app_resources","metroid3","samus","sheets","samus.png"))
						default=os.path.join("app_resources","zelda3","link","sheets","link.zspr"))

	command_line_args = vars(parser.parse_args())
	return command_line_args

#launch the CLI
def process_CLI(command_line_args):
	make_CLI(command_line_args)

#main
if __name__ == "__main__":
	main()
