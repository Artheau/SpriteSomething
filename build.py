import subprocess
import os

DIRECTORY = "."
subprocess.run(" ".join(["pyinstaller SpriteSomething.spec ",
						 "-y ",                #overwrite dist directory if necessary
						 "--onefile "          #compile everything into a single file, except for resources and whatnot
						 f"--distpath {DIRECTORY} ",      #place the executable in the specified directory
						 ])
				  , shell=True)
