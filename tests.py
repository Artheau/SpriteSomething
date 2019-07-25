#there are several tests that must be run separately,
#e.g. cannot test which modules are imported if they are globally imported

import subprocess    #for calling the tests in their own sandboxes
import os            #for joining paths
import sys           #for figuring out how python is called (e.g. python or python3)

for test_file in ["test_asserts.py", "test_waterfalls.py", "test_gc.py"]:   #TODO: don't hardcode the file names
	print(f"Running tests from {test_file}")
	error_code = subprocess.call(f"{sys.executable} {os.path.join(os.getcwd(), 'unittests', test_file)}")
	if error_code != 0:
		exit(error_code)   #early exit
	
exit(error_code)   #standard exit, with error_code = 0
