import install
import get_get_pip

import argparse

def local_install():
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('--py', default=0)
  parser.add_argument('--user', default=False, action="store_true")
  command_line_args = parser.parse_args()
  PY_VERSION = vars(command_line_args)["py"]
  USER = vars(command_line_args)["user"]

  # get & install pip
  get_get_pip.get_get_pip(PY_VERSION)

  # run installer
  install.run_install(PY_VERSION,USER)


def main():
  local_install()

if __name__ == "__main__":
  main()
