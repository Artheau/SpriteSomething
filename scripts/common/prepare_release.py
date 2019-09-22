import distutils.dir_util			# for copying trees
import os											# for env vars
import stat										# for file stats
import subprocess							# do stuff at the shell level
import common
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

env = common.prepare_env()

# make temp dir to put binary in
if not os.path.isdir("../artifact"):
	os.mkdir("../artifact")

# make temp dir for other stuff
if not os.path.isdir("../build"):
	os.mkdir("../build")

# make dir to put the archive in
if not os.path.isdir("../deploy"):
	os.mkdir("../deploy")

# sanity check permissions for working_dirs.json
dirpath = "."
for dirname in ["user_resources","meta","manifests"]:
	dirpath += '/' + dirname
	os.chmod(dirpath,0o755)

os.remove("./.travis.yml")
os.remove("./.travis.notes.yml")
# nuke test suite
distutils.dir_util.remove_tree("./unittests")
os.remove("./tests.py")

BUILD_FILENAME = ""
ZIP_FILENAME = ""

# list executables
BUILD_FILENAME = common.find_binary('.')

if not BUILD_FILENAME == "":
	# move the binary to temp folder
	move(
		BUILD_FILENAME,
		"../artifact/" + BUILD_FILENAME
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

	# mv dirs from source code
	dirs = ["./.git", "./.github","./pages_resources","./scripts"]
	for dir in dirs:
		if os.path.isdir(dir):
			move(
				dir,
				"../build/" + dir
			)

	# move the binary back
	move(
		"../artifact/" + BUILD_FILENAME,
		BUILD_FILENAME
	)

	# .zip if windows
	# .tar.gz otherwise
	ZIP_FILENAME = "../deploy/" + os.path.splitext(BUILD_FILENAME)[0]
	if env["OS_NAME"] == "windows":
		make_archive(ZIP_FILENAME,"zip")
		ZIP_FILENAME += ".zip"
	else:
		make_archive(ZIP_FILENAME,"gztar")
		ZIP_FILENAME += ".tar.gz"

	# mv dirs back
	for dir in dirs:
		if os.path.isdir("../build/" + dir):
			move(
				"../build/" + dir,
				dir
			)

print("Build Filename: " + BUILD_FILENAME)
print("Zip Filename:   " + ZIP_FILENAME)
if not BUILD_FILENAME == "":
	print("Build Filesize: " + file_size(BUILD_FILENAME))
if not ZIP_FILENAME == "":
	print("Zip Filesize:   " + file_size(ZIP_FILENAME))
print("Git tag:        " + env["GITHUB_TAG"])