import os                   # for env vars
from shutil import copy			# file manipulation

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

# copy GitHub Pages files to staging area
# copy index page
copy(
    os.path.join(".", "html", "index.html"),
    os.path.join("..", "pages")
)
