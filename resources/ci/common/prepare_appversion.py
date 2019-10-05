import common
import os               # for env vars
from shutil import copy	# file manipulation

# get app version
APP_VERSION = ""
with open("./resources/app/meta/manifests/app_version.txt","r+") as f:
	APP_VERSION = f.readlines()[0].strip()

env = common.prepare_env()

# set tag to app_version.txt
with open("./resources/app/meta/manifests/app_version.txt","r+") as f:
	_ = f.read()
	f.seek(0)
	f.write(env["GITHUB_TAG"])
	f.truncate()

if not os.path.isdir("../build"):
	os.mkdir("../build")
copy(
	"./resources/app/meta/manifests/app_version.txt",
	"../build/app_version.txt"
)
