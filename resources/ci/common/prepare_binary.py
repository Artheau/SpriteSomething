import common
import distutils.dir_util     # for copying trees
import os                     # for env vars
import stat                   # for file stats
import subprocess             # do stuff at the shell level
from shutil import copy, make_archive, move, rmtree  # file manipulation

def prepare_binary():
  env = common.prepare_env()

  # make dir to put the binary in
  if not os.path.isdir(os.path.join("..", "artifact")):
      os.mkdir(os.path.join("..", "artifact"))

  BUILD_FILENAME = ""

  # list executables
  BUILD_FILENAME = common.find_binary('.')
  if BUILD_FILENAME == "":
      BUILD_FILENAME = common.find_binary(os.path.join("..", "artifact"))

  if isinstance(BUILD_FILENAME, str):
      BUILD_FILENAME = list(BUILD_FILENAME)

  BUILD_FILENAMES = BUILD_FILENAME

  for BUILD_FILENAME in BUILD_FILENAMES:
      DEST_FILENAME = common.prepare_filename(BUILD_FILENAME)

      print(f"OS Name:        {env['OS_NAME']}")
      print(f"OS Version:     {env['OS_VERSION']}")
      print(f"Build Filename: {BUILD_FILENAME}")
      print(f"Dest Filename:  {DEST_FILENAME}")
      if not BUILD_FILENAME == "":
          print("Build Filesize: " + common.file_size(BUILD_FILENAME))
      else:
          exit(1)

      if not BUILD_FILENAME == "":
          move(
              os.path.join(".", BUILD_FILENAME),
              os.path.join("..", "artifact", BUILD_FILENAME)
          )


def main():
  prepare_binary()

if __name__ == "__main__":
  main()
else:
  raise AssertionError("Script improperly used as import!")
