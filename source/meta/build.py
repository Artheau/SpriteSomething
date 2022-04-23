import argparse
import platform
import subprocess  # for executing scripts within scripts
import os  # for checking for dirs

DEST_DIRECTORY = "."

# UPX greatly reduces the filesize.  You can get this utility from https://upx.github.io/
# just place it in a subdirectory named "upx" and this script will find it
UPX_DIR = "upx"
if os.path.isdir(os.path.join(".", UPX_DIR)):
    upx_string = f"--upx-dir={UPX_DIR}"
else:
    upx_string = ""


def run_build():
    print("Building via Python %s" % platform.python_version())

    PYINST_EXECUTABLE = "pyinstaller"
    args = [
        os.path.join("source", "SpriteSomething.spec"),
        upx_string,
        "-y",
        f"--distpath={DEST_DIRECTORY}"
    ]
    errs = []
    strs = []
    print("PyInstaller args: %s" % " ".join(args))
    cmd = [
      PYINST_EXECUTABLE,
      *args
    ]
    ret = subprocess.run(
      cmd,
      capture_output=True,
      text=True
    )
    if ret.stdout.strip():
      for line in ret.stdout.strip().split("\n"):
        if "NotCompressibleException" in line.strip():
          errs.append(line.strip())
    if ret.stderr.strip():
      for line in ret.stderr.strip().split("\n"):
        if "NotCompressibleException" in line.strip():
          strs.append(re.search(r'api-ms-win-(?:[^-]*)-([^-]*)', line.strip()).group(1))
          errs.append(line.strip())
    if len(errs) > 0:
      print("=" * 10)
      print("| ERRORS |")
      print("=" * 10)
      print("\n".join(errs))
    if len(strs) > 0:
      print("=" * 10)
      print("| STRINGS |")
      print("=" * 10)
      print("\n".join(strs))


if __name__ == "__main__":
    run_build()
