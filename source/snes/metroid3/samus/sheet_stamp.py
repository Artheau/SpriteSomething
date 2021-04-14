import os

from PIL import Image
import PIL.ImageOps
from string import ascii_uppercase

m3sheets = os.path.join("resources","app","snes","metroid3","samus","sheets")

rowIMG = {
  "name": Image.open(os.path.join(m3sheets,"uppercase.png")),
  "author": Image.open(os.path.join(m3sheets,"lowercase.png")),
}
charmap = {
  "name": [
    ascii_uppercase,
    ".,?!_#%()+-/:<=>[] "
  ],
  "author": [
    ascii_uppercase,
    "0123456789 "
  ]
}

spritedata = {
  "name": "Sprite Name",
  "author": "Sprite Author"
}

stamped = Image.new("RGBA", (332,142), (0,0,0))
dims = {
  "name": {
    "width": 8,
    "height": 12
  },
  "author": {
    "width": 7,
    "height": 7
  }
}
coords = {
  "dest": {
    "x": 0,
    "y": 0
  },
  "src": {
    "x": 0,
    "y": 0
  }
}
for row in ["name","author"]:
  for i,ltr in enumerate(spritedata[row][:(26+15)]):
    found = False
    ltr = ltr.upper()
    for ltrs in [row,"name","author"]:
      for j,line in enumerate(charmap[ltrs]):
        if not found and ltr in line:
          found = True
          print(ltr,line.find(ltr),j)
          coords["src"]["x"] = (line.find(ltr) * (dims[ltrs]["width"] + 1))
          coords["src"]["y"] = j * dims[ltrs]["height"]
          ltrIMG = rowIMG[ltrs].crop(
            (
              coords["src"]["x"],
              coords["src"]["y"],
              coords["src"]["x"] + dims[ltrs]["width"],
              coords["src"]["y"] + dims[ltrs]["height"] + 1
            )
          )
          ltrIMG = Image.alpha_composite(Image.new("RGBA", ltrIMG.size, (255,255,255)), ltrIMG).convert("RGB")
          ltrIMG = PIL.ImageOps.invert(ltrIMG)
          (x,y) = (
            coords["dest"]["x"],
            coords["dest"]["y"]
          )
          if row == "name" and ltrs == "author":
            y += 4
          stamped.paste(ltrIMG, (x,y))
          coords["dest"]["x"] += dims[ltrs]["width"]
          if ltrs == "author":
            coords["dest"]["x"] += 1
  coords["dest"]["x"] = 0
  coords["dest"]["y"] += dims[row]["height"] + 1

stamped.save(os.path.join(m3sheets,"stamped.png"), "PNG")
