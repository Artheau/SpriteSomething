from source.meta.common import common

APP_VERSION = ""
app_version_filename = common.get_resource(["meta","manifests"],"app_version.txt")
with open(app_version_filename) as f:
	APP_VERSION = f.readlines()[0].strip()

MAX_FRAMES = 1E9     #maximum number of frames an animation will display before it stops

DEBUG_MODE = True    #adds some extra checks that are useful for development purposes (to unset this, just comment out this line, don't set to false)
