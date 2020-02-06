import subprocess	# do stuff at the shell level

def git_clean():
	# clean the git slate
	subprocess.check_call([
		"git",                # run a git command
		"clean",              # clean command
		"-dfx",               # d: directories, f: files, x: ignored files
		"--exclude=.vscode",  # keep vscode IDE files
		"--exclude=.idea",    # keep idea IDE files
		"--exclude=*.json"])  # keep JSON files for that one time I just nuked all that I was working on, oops

if __name__ == "__main__":
	git_clean()
