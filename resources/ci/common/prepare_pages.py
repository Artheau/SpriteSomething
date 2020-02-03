import distutils.dir_util			# for copying trees
import os											# for env vars
from shutil import copy, make_archive, move, rmtree	# file manipulation

# make dir to put app icon in
checkdir = "../pages/resources/app/meta/icons/"
if not os.path.isdir(checkdir):
	os.makedirs(checkdir)
# copy icon over
copy(
	"./resources/app/meta/icons/app.gif",
	"../pages/resources/app/meta/icons"
)

# make dir to put build version in
checkdir = "../pages/resources/app/meta/manifests/"
if not os.path.isdir(checkdir):
	os.makedirs(checkdir)
# copy app_version over
copy(
	"../build/app_version.txt",
	"../pages/resources/app/meta/manifests"
)
# copy badges manifest over
copy(
	"./resources/app/meta/manifests/badges.json",
	"../pages/resources/app/meta/manifests"
)

# copy GitHub Pages files to staging area
# copy index page
copy(
	"./html/index.html",
	"../pages"
)

# copy sprite previews
distutils.dir_util.copy_tree(
	"./html",
	"../pages/resources/app"
)

# copy over game data
consoles = {}
games = []
checkdir = "./resources/app"
for console in os.listdir(checkdir):
	if os.path.isdir(os.path.join(checkdir,console)):
		if not console == "meta":
			consoles[console] = []
			for game in os.listdir(os.path.join(checkdir,console)):
			  if not game == "meta":
			    consoles[console].append(game)
			    gamedir = "../pages/resources/app/" + console + '/' + game
			    if not os.path.isdir(gamedir + "/manifests/"):
			      os.makedirs(gamedir + "/manifests/")
			      distutils.dir_util.copy_tree(
              "./resources/app/" + console + '/' + game + "/manifests/",
			      gamedir + "/manifests/"
			    )
			    distutils.dir_util.copy_tree(
			      "./resources/app/" + console + '/' + game + "/lang/",
			      gamedir + "/lang/"
			    )

# write games dirs to file
for console in consoles:
  with open("../pages/resources/app/meta/manifests/" + console + ".txt","w") as f:
  	for game in consoles[console]:
  		f.write("%s\n" % game)
