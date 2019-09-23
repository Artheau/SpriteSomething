import subprocess	# do stuff at the shell level

def git_clean():
	# clean the git slate
	subprocess.check_call([
		"git",
		"clean",
		"-dfx",
		"--exclude=.vscode",
		"--exclude=.idea",
		"--exclude=*.json"])

if __name__ == "__main__":
	git_clean()
