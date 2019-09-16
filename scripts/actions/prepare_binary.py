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

# get travis tag
TRAVIS_TAG = os.getenv("TRAVIS_TAG","")
# get travis os
TRAVIS_OS_NAME = os.getenv("TRAVIS_OS_NAME","")
# get GHActions os
GHACTIONS_OS_NAME = os.getenv("OS_NAME","")
# get linux distro if applicable
TRAVIS_DIST = os.getenv("TRAVIS_DIST","notset")

OS_NAME = TRAVIS_OS_NAME + GHACTIONS_OS_NAME
OS_DIST = TRAVIS_DIST
OS_VERSION = ""
GITHUB_TAG = TRAVIS_TAG

if '-' in OS_NAME:
	OS_VERSION = OS_NAME[OS_NAME.find('-'):]
	OS_NAME = OS_NAME[:OS_NAME.find('-')]
	if OS_NAME == "linux" and OS_VERSION == "latest":
		OS_VERSION = "bionic"
		OS_DIST = OS_VERSION

# make dir to put the binary in
if not os.path.isdir("../artifact"):
	os.mkdir("../artifact")

# list executables
executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
for filename in os.listdir('.'):
	if os.path.isfile(filename):
		st = os.stat(filename)
		mode = st.st_mode
		if mode & executable:
			if "SpriteSomething" in filename:
				BUILD_FILENAME = filename

# build the filename
if not BUILD_FILENAME == "":
	fileparts = os.path.splitext(BUILD_FILENAME)
	DEST_SLUG = fileparts[0]
	DEST_EXTENSION = fileparts[1]
	DEST_SLUG = DEST_SLUG + '-' + GITHUB_TAG + '-' + OS_NAME
	if not OS_DIST == "" and not OS_DIST == "notset":
		DEST_SLUG += '-' + OS_DIST
	DEST_FILENAME = DEST_SLUG + DEST_EXTENSION

move(
	BUILD_FILENAME,
	"../artifact/" + BUILD_FILENAME
)

print("OS Name:        " + OS_NAME)
print("OS Version:     " + OS_VERSION)
print("Build Filename: " + BUILD_FILENAME)
print("Dest Filename:  " + DEST_FILENAME)
print("Build Filesize: " + file_size(BUILD_FILENAME))
