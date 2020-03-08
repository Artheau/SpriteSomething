import subprocess	# do stuff at the shell level

def git_clean():
  excludes = [
    ".vscode",        # vscode IDE files
    ".idea",          # idea IDE files
    "*.json",         # keep JSON files for that one time I just nuked all that I was working on, oops
    "*app*version.*"  # keep appversion files
  ]
  excludes = ['--exclude={0}'.format(exclude) for exclude in excludes]

	# clean the git slate
  subprocess.check_call([
		"git",                # run a git command
		"clean",              # clean command
		"-dfx",               # d: directories, f: files, x: ignored files
    *excludes])

if __name__ == "__main__":
	git_clean()
