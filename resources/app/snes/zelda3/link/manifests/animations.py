import json
import os
from json.decoder import JSONDecodeError

def comma(k,l,yes,no):
  if isinstance(l,int):
    return yes if k < l else no

  if isinstance(l,dict):
    l = l.keys()

  l = list(l)
  return yes if k != l[-1] else no

def makelist(l):
  ret = []

  for v in l:
    ret.append(str(v).rjust(4))

  return ret

animations = {}
manifest_path = os.path.join(".","resources","app","snes","zelda3","link","manifests","animations.json")
if (not os.path.isfile(manifest_path)):
  raise AssertionError("Manifest not found: " + manifest_path)
with(open(manifest_path)) as json_file:
  try:
    animations = json.load(json_file)
  except JSONDecodeError as e:
    raise ValueError("Animations file malformed: " + manifest_path)

toWrite = "{" + "\n"

for animationName,animation in animations.items():
  if isinstance(animation,str):
    toWrite += ('  "' + animationName + '": "' + animation + '",' + "\n")
  if isinstance(animation,dict):
    toWrite += ('  "' + animationName + '": {') + "\n"
    for dirNum,direction in enumerate(animation):
      toWrite += ('    "' + direction + '": [') + "\n"
      for frameNum,frame in enumerate(animation[direction]):
        toWrite += ("      {") + "\n"
        toWrite += ("        " + '"pose": ' + str(frameNum + 1) + ', "frames": ' + str(frame["frames"]) + ', "tiles": [') + "\n"
        for tileNum,tile in enumerate(frame["tiles"]):
          tText = "          { "
          for k,v in tile.items():
            tText += '"' + k + '": '
            if(isinstance(v,str)):
              w = 20 if k == "image" else 3
              v = ('"' + v + '"')
              v += (", " if k != list(tile.keys())[-1] else " ")
              tText += v.ljust(w)
            elif(isinstance(v,list)):
              tText += "[" + ",".join(makelist(v)) + "]"
              tText += comma(k,tile,", "," ")
          tText += "}"
          tText += comma(tileNum + 1, len(frame["tiles"]),", ","")
          toWrite += (tText) + "\n"
        toWrite += ("        ]") + "\n"
        toWrite += ("      }" + comma(frameNum + 1, len(animation[direction]),", ","")) + "\n"
      toWrite += ("    ]" + comma(dirNum + 1, len(animation),", ","")) + "\n"
    toWrite += ("  }" + comma(animationName, animations.items(),", ","")) + "\n"
toWrite += "}" + "\n"

with(open(os.path.join(".","resources","app","snes","zelda3","link","manifests","animations2.json"),"w+")) as json_file:
  json_file.write(toWrite)
