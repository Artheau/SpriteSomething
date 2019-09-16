import os # for env vars

# get app version
APP_VERSION = ""
with open("./app_resources/meta/manifests/app_version.txt","r+") as f:
	APP_VERSION = f.readlines()[0].strip()
	f.close()

# get travis tag
TRAVIS_TAG = os.environ.get("TRAVIS_TAG") or ""
# get travis build number
TRAVIS_BUILD_NUMBER = os.environ.get("TRAVIS_BUILD_NUMBER") or ""
# get short github sha
GITHUB_SHA_SHORT = os.environ.get("GITHUB_SHA")[:7] or ""

BUILD_NUMBER = TRAVIS_BUILD_NUMBER + GITHUB_SHA_SHORT

# if no tag
if TRAVIS_TAG == "":
	# set to <app_version>.<build_number>
	TRAVIS_TAG = APP_VERSION
	if not BUILD_NUMBER == "":
		TRAVIS_TAG += '.' + BUILD_NUMBER

# set tag to app_version.txt
with open("./app_resources/meta/manifests/app_version.txt","r+") as f:
	_ = f.read()
	f.seek(0)
	f.write(TRAVIS_TAG)
	f.truncate()
