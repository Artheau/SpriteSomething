import distutils.dir_util			# for copying trees
import os											# for env vars
from shutil import copy, make_archive, move, rmtree	# file manipulation

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
	"../build/app_version.txt",
	"../pages/app_resources/meta/manifests"
)
# copy badges manifest over
copy(
	"./app_resources/meta/manifests/badges.json",
	"../pages/app_resources/meta/manifests"
)

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
