import distutils.dir_util			# for copying trees
import os											# for env vars
import stat										# for file stats
import subprocess							# do stuff at the shell level
from shutil import copy, make_archive, move, rmtree	# file manipulation
import tarfile
import zipfile

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

if '-' in OS_NAME:
	OS_VERSION = OS_NAME[OS_NAME.find('-'):]
	OS_NAME = OS_NAME[:OS_NAME.find('-')]
	if OS_NAME == "linux" and OS_VERSION == "latest":
		OS_VERSION = "bionic"
		OS_DIST = OS_VERSION

# if no tag
if GITHUB_TAG == "":
	# set to <app_version>.<build_number>
	GITHUB_TAG = APP_VERSION + '.' + BUILD_NUMBER

# set tag to app_version.txt
with open("./app_resources/meta/manifests/app_version.txt","r+") as f:
	_ = f.read()
	f.seek(0)
	f.write(GITHUB_TAG)
	f.truncate()

# make dir to put the archive/binary in
if not os.path.isdir("../deploy"):
	os.mkdir("../deploy")

# make dir to put some build metadata in
if not os.path.isdir("../build"):
	os.mkdir("../build")

# make dir to put app icon in
checkdir = "../pages/app_resources/meta/icons/"
if not os.path.isdir(checkdir):
	os.makedirs(checkdir)
# copy icon over
copy(
	"./app_resources/meta/icons/app.gif",
	"../pages/app_resources/meta/icons"
)

# make dir to put build version in
checkdir = "../pages/app_resources/meta/manifests/"
if not os.path.isdir(checkdir):
	os.makedirs(checkdir)
# copy app_version over
copy(
	"./app_resources/meta/manifests/app_version.txt",
	"../pages/app_resources/meta/manifests"
)

# sanity check permissions for working_dirs.json
dirpath = "."
for dirname in ["user_resources","meta","manifests"]:
	dirpath += '/' + dirname
	os.chmod(dirpath,0o755)

# copy GitHub Pages files to staging area
# copy index page
copy(
	"./pages_resources/index.html",
	"../pages"
)

# copy sprite previews
distutils.dir_util.copy_tree(
	"./pages_resources",
	"../pages/app_resources"
)

checkdir = "./app_resources"
for item in os.listdir(checkdir):
	if os.path.isdir(os.path.join(checkdir,item)):
		if not item == "meta":
			game = item
			gamedir = "../pages/app_resources/" + game
			if not os.path.isdir(gamedir + "/manifests/"):
				os.makedirs(gamedir + "/manifests/")
			distutils.dir_util.copy_tree(
				"./app_resources/" + game + "/manifests/",
				gamedir + "/manifests/"
			)
			distutils.dir_util.copy_tree(
				"./app_resources/" + game + "/lang/",
				gamedir + "/lang/"
			)

# nuke GitHub Pages files from source code
#distutils.dir_util.remove_tree("./pages_resources")

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
ZIP_FILENAME = "../deploy/" + DEST_SLUG
if TRAVIS_OS_NAME == "windows":
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
print("Dest Filename:  " + DEST_FILENAME)
print("Zip Filename:   " + ZIP_FILENAME)
print("Build Filesize: " + file_size(BUILD_FILENAME))
print("Zip Filesize:   " + file_size(ZIP_FILENAME))
