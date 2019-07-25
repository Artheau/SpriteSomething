#it is convenient to have tests in their own folder,
#but then they cannot easily access the source code using relative paths
#so we adjust that here, so that tests can import from one file folder up

import os
import sys
if not os.path.exists("source"):
	os.chdir("..")
	if not os.path.exists("source"):
		raise AssertionError("cannot find the root folder from test_common.py")

sys.path.append(os.getcwd())    #append the root folder to the python path, for imports
