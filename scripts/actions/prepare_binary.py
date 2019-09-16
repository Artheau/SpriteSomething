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

# get app version
APP_VERSION = ""
with open("./app_resources/meta/manifests/app_version.txt","r+") as f:
	APP_VERSION = f.readlines()[0].strip()
	f.close()

# get travis tag
TRAVIS_TAG = os.getenv("TRAVIS_TAG","")
# get travis build number
TRAVIS_BUILD_NUMBER = os.getenv("TRAVIS_BUILD_NUMBER","")
# get travis os
TRAVIS_OS_NAME = os.getenv("TRAVIS_OS_NAME","")
# get GHActions os
GHACTIONS_OS_NAME = os.getenv("OS_NAME","")
# get linux distro if applicable
TRAVIS_DIST = os.getenv("TRAVIS_DIST","notset")
# get short github sha
GITHUB_SHA_SHORT = os.getenv("GITHUB_SHA","")

if not GITHUB_SHA_SHORT == "":
	GITHUB_SHA_SHORT = GITHUB_SHA_SHORT[:7]

BUILD_NUMBER = TRAVIS_BUILD_NUMBER + GITHUB_SHA_SHORT
OS_NAME = TRAVIS_OS_NAME + GHACTIONS_OS_NAME
OS_DIST = TRAVIS_DIST
OS_VERSION = ""
GITHUB_TAG = TRAVIS_TAG

OS_NAME = OS_NAME.replace("macOS","osx")

if '-' in OS_NAME:
	OS_VERSION = OS_NAME[OS_NAME.find('-')+1:]
	OS_NAME = OS_NAME[:OS_NAME.find('-')]
	if OS_NAME == "linux" or OS_NAME == "ubuntu":
		if OS_VERSION == "latest":
			OS_VERSION = "bionic"
		elif OS_VERSION == "16.04":
			OS_VERSION = "xenial"
		OS_DIST = OS_VERSION

# if no tag
if GITHUB_TAG == "":
	# set to <app_version>.<build_number>
	GITHUB_TAG = APP_VERSION + '.' + BUILD_NUMBER

# make dir to put the binary in
if not os.path.isdir("../artifact"):
	os.mkdir("../artifact")

BUILD_FILENAME = ""

# list executables
executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
for filename in os.listdir('.'):
	if os.path.isfile(filename):
		st = os.stat(filename)
		mode = st.st_mode
		big = st.st_size > (10 * 1024 * 1024) # 10MB
		if (mode & executable) or big:
			if "SpriteSomething" in filename:
				BUILD_FILENAME = filename

# build the filename
if not BUILD_FILENAME == "":
	os.chmod(BUILD_FILENAME,0o755)
	fileparts = os.path.splitext(BUILD_FILENAME)
	DEST_SLUG = fileparts[0]
	DEST_EXTENSION = fileparts[1]
	DEST_SLUG = DEST_SLUG + '-' + GITHUB_TAG + '-' + OS_NAME
	if not OS_DIST == "" and not OS_DIST == "notset":
		DEST_SLUG += '-' + OS_DIST
	DEST_FILENAME = DEST_SLUG + DEST_EXTENSION

print("OS Name:        " + OS_NAME)
print("OS Version:     " + OS_VERSION)
print("Build Filename: " + BUILD_FILENAME)
print("Dest Filename:  " + DEST_FILENAME)
if not BUILD_FILENAME == "":
	print("Build Filesize: " + file_size(BUILD_FILENAME))

if not BUILD_FILENAME == "":
	move(
		BUILD_FILENAME,
		"../artifact/" + BUILD_FILENAME
	)
