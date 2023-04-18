# pylint: disable=invalid-name
'''
Item Overworld Icons
'''
import os
from string import ascii_letters
from PIL import Image

export_folder = ""

itemCells = [
    [   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,  16 ],
    [  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,  27,  28,  29,  30,  31,  32 ],
    [  33,  34,  35,  36,  37,  38,  39,  40,  41,  42,  43,  44,  45,  46,  47,  48 ],
    [  49,  50,  51,  52,  53,  54,  55,  56,  57,  58,  59,  60,  61,  62,  63,  64 ],
    [  65,  66,  67,  68,  69,  70,  71,  72,  73,  74,  75,  76,  77,  78,  79,  80 ],
    [  81,  82,  83,  84,  85,  86,  87,  88,  89,  90,  91,  92,  93,  94,  95,  96 ],
    [  97,  98,  99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112 ],
    [ 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128 ],
    [ 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144 ]
]

items = [
    "bomb",
    "gravity",
    "spring",
    "varia",
    "boots",
    "screw",
    "space",
    "morph",
    "grapple",
    "xray",
    "speed",
    "charge",
    "ice",
    "wave",
    "plasma",
    "spazer",
    "reserve"
]

itemSets = {}

i = 0
for item in items:
    if item != "":
        one = "on"
        two = "off"
        if item in [
            "spring",
            "boots",
            "screw",
            "xray",
            "speed"
        ]:
            one = "off"
            two = "on"
        itemSets[item] = {
            one: [i + 1, i + 2, i + 3, i + 4],
            two: [i + 5, i + 6, i + 7, i + 8]
        }
        i += 8

def coord_calc(origin, dims):
    '''
    Calculate coordinates of a cell
    '''
    x1, x2 = origin
    w, h = dims
    return (x1, x2, w + x1, h+ x2)

def my_pad(item):
    '''
    strpad
    '''
    return str(item).strip().rjust(3, "0")

def setupDirs(workingdir=os.path.join(".")):
    '''
    Create subdirs
    '''
    for folder in [
        "cells",
        "output"
    ]:
        if not os.path.isdir(
            os.path.join(
                workingdir,
                folder
            )
        ):
            os.makedirs(
                os.path.join(
                    workingdir,
                    folder
                )
            )

def applyItemSprites(workingdir):
    '''
    Apply Item Sprites
    '''
    sprite_map = Image.new(
        mode="RGB",
        size=(128, 72),
        color=(0, 0, 0)
    )
    for [itemName, item] in itemSets.items():
        if itemName != "":
            for [state, cellIDs] in item.items():
                item_path = os.path.join(
                    workingdir,
                    "input",
                    "items",
                    "sprites",
                    f"{itemName}_{state}.png"
                )
                if not os.path.isfile(item_path):
                    item_path = os.path.join(
                        ".",
                        "resources",
                        "app",
                        "snes",
                        "metroid3",
                        "samus",
                        "sheets",
                        "paperdoll",
                        "samus",
                        "input",
                        "items",
                        "sprites",
                        f"{itemName}_{state}.png"
                    )
                item_img = Image.open(item_path)
                for [i, cellID] in enumerate(cellIDs):
                    x = 0
                    y = 0
                    if i in [1, 3]:
                        x = 1
                    if i in [2, 3]:
                        y = 1
                    item_slice = item_img.crop(
                        coord_calc(
                            ( x * 8, y * 8),
                            (    16,     8)
                        )
                    )
                    for [j, row] in enumerate(itemCells):
                        if cellID in row:
                            k = row.index(cellID)
                            print(f"{i}, {j}, {k}, {cellID}")
                            sprite_map.paste(
                                item_slice,
                                (k * 8, j * 8)
                            )

    sprite_map.save(
        os.path.join(
            workingdir,
            "output",
            "items.png"
        )
    )

def doTheThing(
    mode=None,
    workingdir=os.path.join(".")
):
    '''
    Do The Thing
    '''
    baseoutput = os.path.join(
        ".",
        "resources",
        "user",
        "snes",
        "metroid3",
        "samus",
        "sheets",
        "items"
    )
    mode = "" if mode is None else mode
    workingdir = os.path.join(baseoutput,workingdir) \
        if workingdir is not None \
        else baseoutput
    setupDirs(
        workingdir
    )
    applyItemSprites(workingdir)

doTheThing(
    "save",
    "samus"
)
