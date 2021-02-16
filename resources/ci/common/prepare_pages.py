import os                   						# for env vars
from shutil import copy, copytree, move	# file manipulation

# copy GitHub Pages files to staging area
copytree(
    os.path.join(".", "html"),
    os.path.join("..", "pages", "resources", "app")
)

# move index to index
move(
		os.path.join("..", "pages", "resources", "app", "index.html"),
		os.path.join("..", "pages", "index.html")
)

# remove readme
os.remove(os.path.join("..", "pages", "resources", "app", "README.md"))

# make dir to put app icon in
checkdir = os.path.join("..", "pages", "resources", "app", "meta", "icons")
if not os.path.isdir(checkdir):
    os.makedirs(checkdir)
# copy icon over
copy(
    os.path.join(".", "resources", "app", "meta", "icons", "app.gif"),
    os.path.join("..", "pages", "resources", "app", "meta", "icons")
)

# make dir to put build version in
checkdir = os.path.join("..", "pages", "resources", "app", "meta", "manifests")
if not os.path.isdir(checkdir):
    os.makedirs(checkdir)
# copy app_version over
copy(
    os.path.join("..", "build", "app_version.txt"),
    os.path.join("..", "pages", "resources", "app", "meta", "manifests")
)
# copy badges manifest over
copy(
    os.path.join(".", "resources", "app", "meta", "manifests", "badges.json"),
    os.path.join("..", "pages", "resources", "app", "meta", "manifests")
)
