import os

def get_all_resources(desired_filename, subdir=None):
	file_list = []
	for directory in ["overrides","resources"]:
		if subdir: directory = os.path.join(directory,subdir)
		for filename in os.listdir(directory):
			if filename == desired_filename:
				file_list.append(os.path.join(directory,filename))
	return file_list

def get_resource(desired_filename, subdir=None):
	file_list = get_all_resources(desired_filename,subdir=subdir)
	return file_list[0] if file_list else None