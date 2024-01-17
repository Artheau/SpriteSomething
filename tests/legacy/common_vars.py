#it is convenient to have tests in their own folder,
#but then they cannot easily access the source code using relative paths
#so we adjust that here, so that tests can import from one file folder up

import os
import sys
if not os.path.exists("source"):
	os.chdir("..")
	if not os.path.exists("source"):
		raise AssertionError("cannot find the root folder from test_common.py")

sys.path.append(os.getcwd())		#append the root folder to the python path, for imports


LINK_RESOURCE_SUBPATH = os.path.join("snes", "zelda3","link")
LINK_RESOURCE_PATH = os.path.join("resources", "app", LINK_RESOURCE_SUBPATH)
LINK_FILENAME = os.path.join(LINK_RESOURCE_PATH,"sheets","link.zspr")

SAMUS_RESOURCE_SUBPATH = os.path.join("snes", "metroid3","samus")
SAMUS_RESOURCE_PATH = os.path.join("resources", "app", SAMUS_RESOURCE_SUBPATH)
SAMUS_FILENAME = os.path.join(SAMUS_RESOURCE_PATH,"sheets","samus.png")
