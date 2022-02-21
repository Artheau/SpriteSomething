import json
import os
import ssl
import urllib.request

source_path = "https://raw.githubusercontent.com/theonlydude/RandomMetroidSolver/master/"
files_path = os.path.join(
  ".",
  "source",
  "snes",
  "metroid3",
  "varia"
)

context = ssl._create_unverified_context()

with(open(os.path.join(files_path,"varia-files.json"))) as files_list:
  files = json.load(files_list)
  for srcfile in files:
    # print(source_path + srcfile)
    req = urllib.request.Request(
      source_path + srcfile,
      data=None,
      headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
      }
    )
    req = urllib.request.urlopen(req, context=context)
    if os.path.splitext(srcfile)[1] == ".py":
      with(open(os.path.join(files_path, srcfile), "w") as f):
        f.write(req.read().decode("utf-8"))
        print(os.path.join(files_path, srcfile))
    elif os.path.splitext(srcfile)[1] == ".png":
      with(open(os.path.join(files_path, srcfile), "wb") as f):
        f.write(req.read())
        print(os.path.join(files_path, srcfile))
