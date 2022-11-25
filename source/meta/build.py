import platform
import subprocess	#for executing scripts within scripts
import os					#for checking for dirs
import sys
from shutil import move

DEST_DIRECTORY = "."

def run_build(PY_VERSION):
  print("Building via Python %s" % platform.python_version())
  include_modules = []

  for (r,d,f) in os.walk(os.path.join(".","source")):
    if "__pycache__" not in r:
      if "__pycache__" in d:
        d.remove("__pycache__")
      if "__init__.py" in f:
        f.remove("__init__.py")
      for fName in f:
        if ".py" in fName:
          include_modules.append(r.replace(os.sep,'.').replace("..",'') + '.' + fName.replace(".py",''))

  DISTILLER_EXECUTABLE = "cxfreeze"
  args = [
    "SpriteSomething.py",
    "--include-modules=" + ",".join(include_modules)
  ]
  print("Distiller args: %s" % " ".join(args))
  subprocess.check_call([DISTILLER_EXECUTABLE,*args])

  for f in os.listdir(os.path.join(".","build")):
    for g in os.listdir(os.path.join(".","build",f)):
      move(
        os.path.join(".","build",f,g),
        os.path.join(".")
      )


if __name__ == "__main__":
    run_build()
