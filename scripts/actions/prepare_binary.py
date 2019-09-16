import distutils.dir_util			# for copying trees
import os											# for env vars
import stat										# for file stats
import subprocess							# do stuff at the shell level
from scripts.actions import common
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

# make dir to put the binary in
if not os.path.isdir("../artifact"):
	os.mkdir("../artifact")

BUILD_FILENAME = ""

# list executables
BUILD_FILENAME = common.find_binary('.')

DEST_FILENAME = common.prepare_filename(BUILD_FILENAME)

print("OS Name:        " + ["OS_NAME"])
print("OS Version:     " + ["OS_VERSION"])
print("Build Filename: " + BUILD_FILENAME)
print("Dest Filename:  " + DEST_FILENAME)
if not BUILD_FILENAME == "":
	print("Build Filesize: " + file_size(BUILD_FILENAME))

if not BUILD_FILENAME == "":
	move(
		BUILD_FILENAME,
		"../artifact/" + BUILD_FILENAME
	)
