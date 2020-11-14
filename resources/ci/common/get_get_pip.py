import common
import urllib.request, ssl
import subprocess # do stuff at the shell level

env = common.prepare_env()

def get_get_pip():
  print("Getting pip getter!")
  #make the request!
  url = "https://bootstrap.pypa.io/get-pip.py"
  context = ssl._create_unverified_context()
  req = urllib.request.urlopen(url, context=context)
  got_pip = req.read().decode("utf-8")

  with open("get-pip.py", "w") as g:
    req = urllib.request.Request(
      url,
      data=None,
      headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
      }
    )
    req = urllib.request.urlopen(req, context=context)
    data = req.read().decode("utf-8")
    g.write(data)

  # get executables
  #  python
  #   linux/windows: python
  #   macosx:        python3
  PYTHON_EXECUTABLE = "python3" if "osx" in env["OS_NAME"] else "python"
  print("Getting pip!")
  subprocess.check_call([PYTHON_EXECUTABLE,"get-pip.py"])

if __name__ == "__main__":
 try:
   import pip
 except ImportError:
    get_get_pip()
