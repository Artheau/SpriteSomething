import argparse
import platform
import subprocess	#for executing scripts within scripts
import os					#for checking for dirs

from resources.ci.common import common

env = common.prepare_env()

DEST_DIRECTORY = "."

#UPX greatly reduces the filesize.  You can get this utility from https://upx.github.io/
#just place it in a subdirectory named "upx" and this script will find it
if os.path.isdir("upx"):
	upx_string = "--upx-dir=upx "
else:
	upx_string = ""

def run_build(PY_VERSION):
  # PYTHON_PATH = env["PYTHON_EXE_PATH"]
  # PYTHON_EXECUTABLE = "python3" if "osx" in env["OS_NAME"] else "python"

  # if PY_VERSION is None:
  #   PY_VERSION = 0

  # if float(PY_VERSION) > 0:
  #   PYTHON_EXECUTABLE = "py"
  #   PYTHON_PATH = env["PY_EXE_PATH"]
  #   print("Building via Python %.1f via Py Launcher" % float(PY_VERSION))
  # else:
  #   print("Building via Python %s" % platform.python_version())

  print("Building via Python %s" % platform.python_version())

  PYINST_EXECUTABLE = "pyinstaller"
  args = [
    "source/SpriteSomething.spec",
    upx_string,
    # "-y ",
    "--onefile ",
    f"--distpath {DEST_DIRECTORY}"
  ]
  # if PY_VERSION == 0:
  #   del args[1]
  subprocess.check_call([PYINST_EXECUTABLE,*args])

if __name__ == "__main__":
  # parser = argparse.ArgumentParser(add_help=False)
  # parser.add_argument('--py', default=0)
  # command_line_args = parser.parse_args()
  # PY_VERSION = vars(command_line_args)["py"]

  PY_VERSION = 0

  run_build(PY_VERSION)
