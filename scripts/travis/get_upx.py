import os			# for env vars
import urllib	# for downloads
from shutil import move
import tarfile

TRAVIS_OS_NAME = os.getenv("TRAVIS_OS_NAME") or "TRAVIS_OS_NAME"

# set up download url
UPX_VERSION = os.getenv("UPX_VERSION") or "3.95"
UPX_SLUG = "upx-" + UPX_VERSION + "-amd64_linux"
UPX_FILE = UPX_SLUG + ".tar.xz"
UPX_URL = "https://github.com/upx/upx/releases/download/v" + UPX_VERSION + '/' + UPX_FILE

# make some dirs
os.makedirs("../upx")
os.makedirs("./upx")

with open("./" + UPX_FILE,"wb") as upx:
	UPX_REQ = urllib.request.Request(
		UPX_URL,
		data=None
	)
	UPX_REQ = urllib.request.urlopen(UPX_REQ)
	UPX_DATA = UPX_REQ.read()
	upx.write(UPX_DATA)
	upx.close()

tar = tarfile.TarFile(UPX_FILE)
tar.extractall("../upx")
move(
	"../upx/" + UPX_SLUG + "/*",
	"./upx"
)
