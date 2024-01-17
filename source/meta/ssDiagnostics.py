import os
import platform
import subprocess
import sys
import source.meta.common.constants as CONST
from datetime import datetime

hasUTC = True
try:
    from datetime import UTC
except ImportError as e:
    hasUTC = False

if "windows" in platform.system().lower():
  import pkg_resources

def diagpad(inbound):
  return inbound.ljust(len("SpriteSomething Version") + 5,'.')

def output():
  lines = [
    "SpriteSomething Diagnostics",
    "===========================",
    diagpad("UTC Time") + (str(datetime.now(UTC))[:19] if hasUTC else (str(datetime.utcnow()))),
    diagpad("SpriteSomething Version") + CONST.APP_VERSION,
    diagpad("Python Version") + platform.python_version()
  ]
  lines.append(diagpad("OS Version") + "%s %s" % (platform.system(), platform.release()))
  if hasattr(sys, "executable"):
    lines.append(diagpad("Executable") + sys.executable)
  lines.append(diagpad("Build Date") + platform.python_build()[1])
  lines.append(diagpad("Compiler") + platform.python_compiler())
  if hasattr(sys, "api_version"):
    lines.append(diagpad("Python API") + str(sys.api_version))
  if hasattr(os, "sep"):
    lines.append(diagpad("Filepath Separator") + os.sep)
  if hasattr(os, "pathsep"):
    lines.append(diagpad("Path Env Separator") + os.pathsep)

  if("windows" in platform.system().lower() and hasattr(pkg_resources,"working_set") and (len(list(pkg_resources.working_set)) > 0)):
    lines.append("")
    lines.append("Packages")
    lines.append("--------")
    pkgs = {}
    longest_pkg = 0
    filler = '.'
    installed_packages = [str(d) for d in list(pkg_resources.working_set)]   #this doesn't work from the .exe either, but it doesn't crash the program
    installed_packages.sort()
    for pkg in installed_packages:
      pkg = pkg.split(' ')
      if len(pkg[0]) > longest_pkg:
        longest_pkg = len(pkg[0])
      pkgs[pkg[0]] = pkg[1]
    for pkg_name,pkg_ver in pkgs.items():
      lines.append(pkg_name.ljust(longest_pkg + 5).replace(' ', filler) + pkg_ver)

  return lines


def main():
    raise AssertionError(f"Called main() on utility library {__file__}")

if __name__ == "__main__":
    main()
