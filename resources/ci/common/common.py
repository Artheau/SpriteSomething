import os
import stat

def prepare_env():
	env = {}

	# get app version
	APP_VERSION = ""
	with open("./resources/app/meta/manifests/app_version.txt","r+") as f:
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
	# get github actor
	GITHUB_ACTOR = os.getenv("GITHUB_ACTOR","MegaMan.EXE")
	# get github tag
	GITHUB_TAG = os.getenv("GITHUB_TAG","")
	# get github sha
	GITHUB_SHA_SHORT = os.getenv("GITHUB_SHA","")

	if not GITHUB_SHA_SHORT == "":
		GITHUB_SHA_SHORT = GITHUB_SHA_SHORT[:7]

	BUILD_NUMBER = TRAVIS_BUILD_NUMBER + GITHUB_SHA_SHORT
	OS_NAME = TRAVIS_OS_NAME + GHACTIONS_OS_NAME
	OS_DIST = TRAVIS_DIST
	OS_VERSION = ""

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
		# if we've got a Travis Tag
		if not TRAVIS_TAG == "":
			GITHUB_TAG = TRAVIS_TAG
		# if we haven't appended the build number, do it
		if not BUILD_NUMBER in GITHUB_TAG:
			# set to <app_version>.<build_number>
			GITHUB_TAG = APP_VERSION + '.' + BUILD_NUMBER

	env["BUILD_NUMBER"] = BUILD_NUMBER
	env["GITHUB_ACTOR"] = GITHUB_ACTOR
	env["GITHUB_TAG"] = GITHUB_TAG
	env["OS_NAME"] = OS_NAME
	env["OS_DIST"] = OS_DIST
	env["OS_VERSION"] = OS_VERSION

	return env

def prepare_filename(BUILD_FILENAME):
	env = prepare_env()

	# build the filename
	if not BUILD_FILENAME == "":
		os.chmod(BUILD_FILENAME,0o755)
		fileparts = os.path.splitext(BUILD_FILENAME)
		DEST_SLUG = fileparts[0]
		DEST_EXTENSION = fileparts[1]
		DEST_SLUG = DEST_SLUG + '-' + env["GITHUB_TAG"] + '-' + env["OS_NAME"]
		if not env["OS_DIST"] == "" and not env["OS_DIST"] == "notset":
			DEST_SLUG += '-' + env["OS_DIST"]
		DEST_FILENAME = DEST_SLUG + DEST_EXTENSION
	return DEST_FILENAME

def find_binary(listdir):
	BUILD_FILENAME = ""
	executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
	for filename in os.listdir(listdir):
		if os.path.isfile(filename):
			st = os.stat(filename)
			mode = st.st_mode
			big = st.st_size > (10 * 1024 * 1024) # 10MB
			if (mode & executable) or big:
				if "SpriteSomething" in filename:
					BUILD_FILENAME = filename
	return BUILD_FILENAME
