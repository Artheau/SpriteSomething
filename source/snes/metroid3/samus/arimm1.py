'''
My image reader
'''
import os
from string import ascii_uppercase
from PIL import Image, ImageChops

base_path_user = os.path.join(
    ".",
    "resources",
    "user",
    "snes",
    "metroid3",
    "samus",
    "sheets",
    "paperdoll",
    "arima"
)

arimaCells = [
    [   1,   2,   3,   4,   5,   0,   0,   0,   6,   7,   8,   9,  10,  11,  12,  13 ],
    [  14,  15,  16,  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,  27,  28,  29 ],
    [  30,  31,  32,  33,  34,  35,  36,  37,  38,  39,  40,  41,  42,  43,  44,  45 ],
    [  46,  47,  48,  49,  50,  51,  52,  53,  54,  55,  56,   0,  57,  58,  59,  60 ],
    [   0,   0,   0,  61,  62,  63,  64,  65,   0,   0,   0,   0,  66,  67,  68,   0 ],
    [  69,  70,  71,  72,  73,  74,  75,  76,  77,  78,  79,  80,  81,  82,  83,   0 ],
    [  84,  85,  86,  87,  88,  89,  90,  91,   0,   0,  92,  93,  94,  95,  96,   0 ],
    [  97,  98,  99, 100, 101, 102, 103, 104,   0, 105, 106, 107, 108, 109, 110, 111 ],
    [ 112, 113, 114, 115,   0,   0,   0,   0,   0, 116, 117, 118, 119, 120, 121, 122 ]
]

images = {}
differences = {}

def load_images(filenames):
    for filename in filenames:
        print(f"Loading: {filename}")
        if filename not in images:
            images[filename] = Image.open(
                os.path.join(
                    base_path_user,
                    filename + ".png"
                )
            )

def list_differences(filenames):
    print(f"Listing differences for: {filenames}")
    diffKey = "|".join(filenames)
    if diffKey not in differences:
        differences[diffKey] = []
    for row in range(0, 17):
        for col in range(0, 8):
            x = col * 8
            y = row * 8
            cellCoords = (x, y, x + 8, y + 8)
            tileOne = images[filenames[0]].crop(cellCoords)
            tileTwo = images[filenames[1]].crop(cellCoords)
            tileDiff = ImageChops.difference(tileOne, tileTwo)
            if tileDiff.getbbox():
                cellID = ascii_uppercase[row] + str(col)
                differences[diffKey].append(cellID)
                print(cellID, cellCoords)
    print(f"Total differences: {len(differences[diffKey])}")
    print()

def postpend(s):
    return s + "-mirrors"

filesets = [
  [ "power", "varia" ],
  [ "powerboots", "variaboots" ],
  [ "power", "powerboots" ],
  [ "varia", "variaboots" ],
  [ "power", "variaboots" ]
]

for filenames in filesets:
    load_images(filenames)
    list_differences(filenames)
    load_images(list(map(postpend, filenames)))
    list_differences(list(map(postpend, filenames)))

print(differences)
