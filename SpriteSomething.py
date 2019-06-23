from argparse import ArgumentParser
from source.gui import make_GUI
from tkinter import messagebox   #for the error box in case of fatal error
import traceback #for error box
import os

def main():
	command_line_args = process_command_line_args()
	if True:          #TODO: figure out when to use the command line intercept here
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
	parser.add_argument("--sprite",
						dest="sprite",
						help="A sprite file to load upon opening",
						metavar="<sprite_filename>",
						default=os.path.join("resources","metroid3","samus","samus.png"))
#						default=os.path.join("resources","zelda3","link","link.zspr"))

	command_line_args = vars(parser.parse_args())
	return command_line_args

def process_CLI(command_line_args):
	raise NotImplementedError()

if __name__ == "__main__":
	main()