import os # for env vars
from shutil import copy	# file manipulation

# get app version
APP_VERSION = ""
with open("./resources/app/meta/manifests/app_version.txt","r+") as f:
	APP_VERSION = f.readlines()[0].strip()
	f.close()

# get travis tag
TRAVIS_TAG = os.getenv("TRAVIS_TAG","")
# get travis build number
TRAVIS_BUILD_NUMBER = os.getenv("TRAVIS_BUILD_NUMBER","")
# get short github sha
GITHUB_SHA_SHORT = os.getenv("GITHUB_SHA","")

if not GITHUB_SHA_SHORT == "":
	GITHUB_SHA_SHORT = GITHUB_SHA_SHORT[:7]

GITHUB_TAG = TRAVIS_TAG
BUILD_NUMBER = TRAVIS_BUILD_NUMBER + GITHUB_SHA_SHORT

# if no tag
if GITHUB_TAG == "":
	# set to <app_version>.<build_number>
	GITHUB_TAG = APP_VERSION
	if not BUILD_NUMBER == "":
		GITHUB_TAG += '.' + BUILD_NUMBER

# set tag to app_version.txt
with open("./resources/app/meta/manifests/app_version.txt","r+") as f:
	_ = f.read()
	f.seek(0)
	f.write(GITHUB_TAG)
	f.truncate()

if not os.path.isdir("../build"):
	os.mkdir("../build")
copy(
	"./resources/app/meta/manifests/app_version.txt",
	"../build/app_version.txt"
)
