import json
import os
import subprocess  # do stuff at the shell level

CI_SETTINGS = {}
manifest_path = os.path.join("resources","app","meta","manifests","ci.json")
if (not os.path.isfile(manifest_path)):
  raise AssertionError("Manifest not found: " + manifest_path)
with(open(manifest_path)) as ci_settings_file:
  CI_SETTINGS = json.load(ci_settings_file)

def git_clean(clean_ignored=True, clean_user=False):
    excludes = CI_SETTINGS["common"]["git_clean"]["excludes"]

    if not clean_user:
        excludes.append(CI_SETTINGS["common"]["git_clean"]["user_resources"])  # keep user resources

    excludes = ['--exclude={0}'.format(exclude) for exclude in excludes]

    # d: directories, f: files, x: ignored files
    switches = "df" + ("x" if clean_ignored else "")

    # clean the git slate
    subprocess.check_call([
        "git",                # run a git command
        "clean",              # clean command
        "-" + switches,
        *excludes])


def main():
    git_clean()

if __name__ == "__main__":
    main()
