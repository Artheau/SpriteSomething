import argparse
import json
import platform
import subprocess  # for executing scripts within scripts
import os  # for checking for dirs
import re

DEST_DIRECTORY = "."

# UPX greatly reduces the filesize.  You can get this utility from https://upx.github.io/
# just place it in a subdirectory named "upx" and this script will find it
UPX_DIR = "upx"
if os.path.isdir(os.path.join(".", UPX_DIR)):
    upx_string = f"--upx-dir={UPX_DIR}"
else:
    upx_string = ""
GO = True

def run_build():
    global GO

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
        print(line)
        if "NotCompressibleException" in line.strip():
          errs.append(line.strip())
    if ret.stderr.strip():
      for line in ret.stderr.strip().split("\n"):
        if "NotCompressibleException" in line.strip():
          strAdd = re.search(r'api-ms-win-(?:[^-]*)-([^-]*)', line.strip()).group(1)
          strs.append(strAdd)
          errs.append(line.strip())
    if len(errs) > 0:
      print("=" * 10)
      print("| ERRORS |")
      print("=" * 10)
      print("\n".join(errs))
    else:
      GO = False
    if len(strs) > 0:
      with open(os.path.join(".","resources","app","meta","manifests","excluded_dlls.json"), "r+", encoding="utf-8") as dllsManifest:
        dlls = json.load(dllsManifest)

        newDLLs = dlls

        addDLLs = sorted(list(set(strs)))

        newDLLs.append(*addDLLs)
        newDLLs = sorted(list(set(newDLLs)))

        dllsManifest.seek(0)
        dllsManifest.truncate()
        dllsManifest.write(json.dumps(sorted(newDLLs), indent=2))
        print(f"Wrote the following to the DLL manifest: {json.dumps(sorted(addDLLs))}")


if __name__ == "__main__":
    while GO:
        run_build()
