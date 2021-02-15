import subprocess	#for executing scripts within scripts
import os					#for checking for dirs

DEST_DIRECTORY = "."

#UPX greatly reduces the filesize. You can get this utility from https://upx.github.io/
#just place it in a subdirectory named "upx" and this script will find it
if os.path.isdir("upx"):
	upx_string = "--upx-dir=upx "
else:
	upx_string = ""

subprocess.run(" ".join(["pyinstaller ./source/SpriteSomething.spec ",
						 upx_string,
						 "-y ",														#overwrite dist directory if necessary
						 "--onefile "											#compile everything into a single file, except for resources and whatnot
						 f"--distpath {DEST_DIRECTORY} ",	#place the executable in the specified directory
						 ])
					, shell=True)
