import argparse
import platform
import subprocess	#for executing scripts within scripts
import os					#for checking for dirs

DEST_DIRECTORY = "."

#UPX greatly reduces the filesize.  You can get this utility from https://upx.github.io/
#just place it in a subdirectory named "upx" and this script will find it
if os.path.isdir("./upx"):
	upx_string = "--upx-dir=upx "
else:
	upx_string = ""

def run_build(PY_VERSION):
  print("Building via Python %s" % platform.python_version())

  PYINST_EXECUTABLE = "pyinstaller"
  args = [
    "source/SpriteSomething.spec",
    upx_string,
    "-y",
    "--onefile",
    f"--distpath={DEST_DIRECTORY}"
  ]
  print("PyInstaller args: %s" % " ".join(args))
  subprocess.check_call([PYINST_EXECUTABLE,*args])

if __name__ == "__main__":
  PY_VERSION = 0

  run_build(PY_VERSION)
