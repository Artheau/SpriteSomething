import os

def get_all_resources(desired_filename, subdir=None):
	#gets the file from overrides AND resources (returns a list of filenames)
	file_list = []
	for directory in ["overrides","resources"]:
		if subdir: directory = os.path.join(directory,subdir)
		if os.path.isdir(directory):
			for filename in os.listdir(directory):
				if filename == desired_filename:
					file_list.append(os.path.join(directory,filename))
	return file_list

def get_resource(desired_filename, subdir=None):
	#gets the file from overrides.  If not there, then from resources.
	file_list = get_all_resources(desired_filename,subdir=subdir)
	return file_list[0] if file_list else None

def gather_all_from_resource_subdirectory(subdir):
	#gathers all the filenames from a subdirectory in resources,
	# and then also throws in all the filenames from the same subdirectory in overrides
	#does not recurse
	file_list = []
	for directory in ["resources","overrides"]:
		directory = os.path.join(directory,subdir)
		if os.path.isdir(directory):
			for filename in os.listdir(directory):
				if os.path.isfile(os.path.join(directory,filename)):
					file_list.append(filename)    #just the filename, not the path, so that this overrrides correctly
	return file_list