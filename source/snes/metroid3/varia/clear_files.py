import json
import os

files_path = os.path.join(
  ".",
  "source",
  "snes",
  "metroid3",
  "varia"
)

with(open(os.path.join(files_path,"varia-files.json"))) as files_list:
  files = json.load(files_list)
  for srcfile in files:
    print(os.path.join(files_path,srcfile))
    if os.path.exists(os.path.join(files_path,srcfile)):
      os.remove(os.path.join(files_path,srcfile))
