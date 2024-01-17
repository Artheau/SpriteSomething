# pylint: disable=invalid-name
'''
Inventory Items
'''
import os
from string import ascii_uppercase
from PIL import Image

export_folder = ""

inventoryCells = [
    [   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,  16 ],
    [  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,  27,  28,  29,  30,  31,  32 ],
    [  33,  34,  35,  36,  37,  38,  39,  40,  41,  42,  43,  44,  45,  46,  47,  48 ],
    [  49,  50,  51,  52,  53,  54,  55,  56,  57,  58,  59,  60,  61,  62,  63,  64 ],
    [  65,  66,  67,  68,  69,  70,  71,  72,  73,  74,  75,  76,  77,  78,  79,  80 ],
    [  81,  82,  83,  84,  85,  86,  87,  88,  89,  90,  91,  92,  93,  94,  95,  96 ],
    [  97,  98,  99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112 ]
]

inventorySets = {
    "suit":     [52, 53, 54],
    "gravity":  [1, 2, 3, 4, 5],
    "bomb":     [6, 7, 8],
    "charge":   [9, 10, 11, 24],
    "ice":      [12, 13],
    "wave":     [14, 15, 16],
    "screw":    [17, 18, 19, 20, 21, 22, 23, 34],
    "spazer":   [25, 26, 27, 28],
    "plasma":   [29, 30, 31, 32],
    "space":    [33, 34, 35, 36, 37, 38],
    "long":     [46, 55, 60],
    "varia":    [49, 50, 51],
    "spring":   [65, 66, 67, 68, 69, 70, 71],
    "morph":    [81, 82, 83, 84, 72, 73, 64, 80],
    "speed":    [85, 86, 87, 88, 89, 90, 91, 92],
    "hijump":   [97, 98, 99, 100, 101, 102, 103],
    "hyper":    [104, 105, 106, 96]
}

inventorySplits = [
    "gravity",
    "charge",
    "long",
    "varia",
    "morph",
    "hyper"
]

categories = {
    "suit":           [39, 40, 41],
    "beam":           [42, 43, 44],
    "samus-marquee":  [107, 108, 109, 110, 111, 112]
}

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

def applyInventoryLabels(workingdir):
    '''
    Apply Inventory Labels
    '''
    clean_img = Image.open(
        os.path.join(
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
            "binary-inventory-clean.png"
        )
    )
    clean_img = clean_img.convert("RGBA")
    for [item, cellIDs] in inventorySets.items():
        item_path = os.path.join(
            workingdir,
            "input",
            "items",
            f"{item}.png"
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
                f"{item}.png"
            )
        item_img = Image.open(item_path)
        if item not in inventorySplits:
            x = 0
            y = 0
            for [i, row] in enumerate(inventoryCells):
                for [j, col] in enumerate(row):
                    if col == cellIDs[0]:
                        y = i * 8
                        x = j * 8
            clean_img.paste(
                item_img,
                (x,y,)
            )
        else:
            x = 0
            y = 0
            for [i, row] in enumerate(inventoryCells):
                for [j, col] in enumerate(row):
                    if col in cellIDs:
                        destPixCoords = (j*8,i*8)
                        setIDX = cellIDs.index(col)
                        srcPixCoords = (setIDX*8,0)
                        segment_img = item_img.crop(
                            coord_calc(
                                srcPixCoords,
                                (8,8)
                            )
                        )
                        clean_img.paste(
                            segment_img,
                            destPixCoords
                        )
    for [cat, cellIDs] in categories.items():
        cat_path = os.path.join(
            workingdir,
            "input",
            "categories",
            f"{cat}.png"
        )
        if not os.path.isfile(cat_path):
            cat_path = os.path.join(
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
                "categories",
                f"{cat}.png"
            )
        cat_img = Image.open(cat_path)
        x = 0
        y = 0
        for [i, row] in enumerate(inventoryCells):
            for [j, col] in enumerate(row):
                if col in cellIDs:
                    destPixCoords = (j*8,i*8)
                    setIDX = cellIDs.index(col)
                    srcPixCoords = (setIDX*8,0)
                    segment_img = cat_img.crop(
                        coord_calc(
                            srcPixCoords,
                            (8,8)
                        )
                    )
                    clean_img.paste(
                        segment_img,
                        destPixCoords
                    )
    clean_img.save(
        os.path.join(
            workingdir,
            "output",
            "inventory.png"
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
        "paperdoll"
    )
    mode = "" if mode is None else mode
    workingdir = os.path.join(baseoutput, workingdir) \
        if workingdir is not None \
        else baseoutput
    setupDirs(
        workingdir
    )
    applyInventoryLabels(workingdir)

doTheThing(
    "save",
    "samus"
)
