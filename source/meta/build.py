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
    print("PyInstaller args: %s" % " ".join(args))
    cmd = [
      PYINST_EXECUTABLE,
      *args
    ]
    with subprocess.Popen(
      cmd,
      stdout=subprocess.PIPE,
      bufsize=1,
      universal_newlines=True
    ) as p:
      if p.stdout:
        for line in p.stdout:
          print(line.strip(), end='')
          if "NotCompressibleException" in line.strip():
            errs.append(line.strip())
      if p.stderr:
        for line in p.stderr:
          errs.append(line.strip())
          print(f"ERROR: {line.strip()}", end='')
    if len(errs) > 0:
      print("=" * 10)
      print("| ERRORS |")
      print("=" * 10)
      print("\n".join(errs))


if __name__ == "__main__":
    run_build()
