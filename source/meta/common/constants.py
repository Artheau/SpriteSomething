import os
from source.meta.common import common

APP_VERSION = ""
app_version_filename = common.get_resource(
	["meta", "manifests"], "app_version.txt"
)
if app_version_filename and os.path.isfile(app_version_filename):
	with open(app_version_filename) as f:
		APP_VERSION = f.readlines()[0].strip()

# maximum number of frames an animation will display before it stops
MAX_FRAMES = 1E9

# adds some extra checks that are useful for development purposes
#	(to unset this, just comment out this line, don't set to false)
DEBUG_MODE = True


def main():
    print(f"Called main() on utility library {__file__}")

if __name__ == "__main__":
    main()
