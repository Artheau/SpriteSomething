import distutils.dir_util			# for copying trees
import os											# for env vars
import stat										# for file stats
import subprocess							# do stuff at the shell level
import common
from git_clean import git_clean
from shutil import copy, make_archive, move, rmtree	# file manipulation

env = common.prepare_env() # get env vars

# make temp dir to put binary in
if not os.path.isdir(os.path.join("..","artifact")):
	os.mkdir(os.path.join("..","artifact"))

# make temp dir for other stuff
if not os.path.isdir(os.path.join("..","build")):
	os.mkdir(os.path.join("..","build"))

# make dir to put the archive in
if not os.path.isdir(os.path.join("..","deploy")):
	os.mkdir(os.path.join("..","deploy"))

# sanity check permissions for working_dirs.json
dirpath = "."
for dirname in ["resources","user","meta","manifests"]:
	dirpath += '/' + dirname
	os.chmod(dirpath,0o755)
os.remove(os.path.join(".",".travis.yml"))
# nuke test suite
distutils.dir_util.remove_tree(os.path.join(".","tests"))

BUILD_FILENAME = ""
ZIP_FILENAME = ""

# list executables
BUILD_FILENAME = common.find_binary(os.path.join("."))
if BUILD_FILENAME == "":
  BUILD_FILENAME = common.find_binary(os.path.join("..","artifact"))

if not BUILD_FILENAME == "":
  if not "artifact" in BUILD_FILENAME:
    # move the binary to temp folder
    move(
      BUILD_FILENAME,
      os.path.join("..","artifact") + BUILD_FILENAME
    )

  # clean the git slate
  git_clean()

	# mv dirs from source code
  dirs = [os.path.join(".",".git"), os.path.join(".",".github"), os.path.join(".",".gitignore"), os.path.join(".","html"), os.path.join(".","resources","ci")]
  for dir in dirs:
    if os.path.isdir(dir):
      move(
        dir,
        os.path.join("..","build",dir)
      )

  if not "artifact" in BUILD_FILENAME:
  	# move the binary back
  	move(
      os.path.join("..","artifact",BUILD_FILENAME),
  		BUILD_FILENAME
  	)

	# .zip if windows
	# .tar.gz otherwise
  ZIP_FILENAME = os.path.join("..","deploy",os.path.splitext(BUILD_FILENAME)[0])
  if env["OS_NAME"] == "windows":
    make_archive(ZIP_FILENAME,"zip")
    ZIP_FILENAME += ".zip"
  else:
    make_archive(ZIP_FILENAME,"gztar")
    ZIP_FILENAME += ".tar.gz"

	# mv dirs back
  for dir in dirs:
    if os.path.isdir(os.path.join("..","build",dir)):
      move(
        os.path.join("..","build",dir),
        dir
      )

print("Build Filename: " + BUILD_FILENAME)
print("Zip Filename:   " + ZIP_FILENAME)
if not BUILD_FILENAME == "":
	print("Build Filesize: " + common.file_size(BUILD_FILENAME))
if not ZIP_FILENAME == "":
	print("Zip Filesize:   " + common.file_size(ZIP_FILENAME))
print("Git tag:        " + env["GITHUB_TAG"])
