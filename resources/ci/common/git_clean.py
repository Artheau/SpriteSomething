import subprocess	# do stuff at the shell level


def git_clean(clean_ignored=True, clean_user=False):
		excludes = [
				".vscode",				# vscode IDE files
				".idea",					# idea IDE files
				"*.json",				 # keep JSON files
				"*app*version.*"	# keep appversion files
		]

		if not clean_user:
				excludes.append("resources/user*")	# keep user resources

		excludes = ['--exclude={0}'.format(exclude) for exclude in excludes]

		# d: directories, f: files, x: ignored files
		switches = "df" + ("x" if clean_ignored else "")

		# clean the git slate
		subprocess.check_call([
				"git",								# run a git command
				"clean",							# clean command
				"-" + switches,
				*excludes])


if __name__ == "__main__":
		git_clean()
