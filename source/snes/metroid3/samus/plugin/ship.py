from PIL import Image
import os

SHIP_RESOURCES_PATH = os.path.join(
  ".",
  "resources",
  "app",
  "snes",
  "metroid3",
  "samus",
  "sheets",
  "ship"
)

ship = {}

for part in [ "body", "structure", "thrusters", "window" ]:
    ship[part] = Image.open(os.path.join(SHIP_RESOURCES_PATH, f"{part}.png"))

for [ part, img ] in ship.items():
    numcolors = len(img.getcolors())
    numpalette = len(img.getpalette())
    nompalette = img.getpalette()[:numcolors*3]
    l = nompalette
    n = 3
    nompalette2 = [tuple(l[i:i+n]) for i in range(0, (len(l) - n + 1), n)]
    print(
      part,
      nompalette2
    )
    if part == "window":
        np = nompalette2
        np[0] = (255, 255, 255)
        newpalette = []
        for color in np:
            for c in color:
                newpalette.append(c)
        img.putpalette(newpalette)
        img.show()
