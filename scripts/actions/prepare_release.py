import distutils.dir_util			# for copying trees
import os											# for env vars
import stat										# for file stats
import subprocess							# do stuff at the shell level
from shutil import copy, make_archive, move, rmtree	# file manipulation

def convert_bytes(num):
	for x in ["bytes","KB","MB","GB","TB","PB"]:
		if num < 1024.0:
			return "%3.1f %s" % (num,x)
		num /= 1024.0

def file_size(file_path):
	if os.path.isfile(file_path):
		file_info = os.stat(file_path)
		return convert_bytes(file_info.st_size)

# get travis os
TRAVIS_OS_NAME = os.getenv("TRAVIS_OS_NAME","")
# get GHActions os
GHACTIONS_OS_NAME = os.getenv("OS_NAME","")

OS_NAME = TRAVIS_OS_NAME + GHACTIONS_OS_NAME

# make dir to put the archive in
if not os.path.isdir("../deploy"):
	os.mkdir("../deploy")

# sanity check permissions for working_dirs.json
dirpath = "."
for dirname in ["user_resources","meta","manifests"]:
	dirpath += '/' + dirname
	os.chmod(dirpath,0o755)

# nuke GitHub Pages files from source code
#distutils.dir_util.remove_tree("./pages_resources")

# list executables
executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
for filename in os.listdir('.'):
	if os.path.isfile(filename):
		st = os.stat(filename)
		mode = st.st_mode
		big = st.st_size > (10 * 1024 * 1024) # 10MB
		if mode & executable or mode & big:
			if "SpriteSomething" in filename:
				BUILD_FILENAME = filename

# move the binary to temp folder
move(
	BUILD_FILENAME,
	"../build/" + BUILD_FILENAME
)

# clean the git slate
subprocess.check_call([
	"git",
	"clean",
	"-dfx",
	"--exclude=.vscode",
	"--exclude=.idea",
	"--exclude=scripts/travis",
	"--exclude=*.json"])

if os.path.isdir("./.git"):
	# move .git to a temp folder
	move(
		"./.git",
		"../build/.git"
	)

# move the binary back
move(
	"../build/" + BUILD_FILENAME,
	BUILD_FILENAME
)

# .zip if windows
# .tar.gz otherwise
ZIP_FILENAME = "../deploy/" + os.path.splitext(BUILD_FILENAME)[0]
if OS_NAME == "windows":
	make_archive(ZIP_FILENAME,"zip")
	ZIP_FILENAME += ".zip"
else:
	make_archive(ZIP_FILENAME,"gztar")
	ZIP_FILENAME += ".tar.gz"

if os.path.isdir("../build/.git"):
	# move .git back
	move(
		"../build/.git",
		"./.git"
	)

print("Build Filename: " + BUILD_FILENAME)
print("Zip Filename:   " + ZIP_FILENAME)
print("Build Filesize: " + file_size(BUILD_FILENAME))
print("Zip Filesize:   " + file_size(ZIP_FILENAME))
