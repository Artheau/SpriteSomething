# pylint: disable=invalid-name, line-too-long
'''
Manage Paper Doll imagery
'''
# load bases image
# chop it up into cells
# figure out which cells go where
# list of cells for base
# list of cells for boots
# list of cells for varia
import os
from PIL import Image
# from source.meta.common import common

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

if not os.path.isdir(os.path.join(base_path_user, "cells")):
    os.makedirs(os.path.join(base_path_user, "cells"))

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

# VariaBoots -> Power -> PowerBoots
# VariaBoots -> Varia

arimaSuits = {
    "variaboots": [
        [   0,   0,   0,  61 ],
        [  69,  70,  71,  72 ],
        [  84,  85,  86,  87 ],
        [  97,  98,  99, 100, 101, 102, 103, 104 ],
        [ 112, 113, 114, 115 ],
        [   1,   2,   3,   4,   5 ],
        [  14,  15,  16,  17,  18,  19,  20,  21 ],
        [  30,  31,  32,  33,   0,  35,  36,  37 ],
        [  46,  47,  48,  49,   0,   0,  52,  53 ],
        [   0,  78,  79,  80 ],
        [   0,   0,  92,  93 ],
        [   0, 105, 106, 107 ],
        [   0, 116, 117, 118 ],
        [   0,   7,   8 ],
        [   0,  23,  24 ],
        [  38,  39,  40,  41,   0,   0,  42,  43 ],
        [  54,  55,  56,   0,   0,   0,  57 ]
    ],
    "power": [
        [ ],
        [  66,  67,  68 ],
        [  81,  82,  83 ],
        [  94,  95,  96, 109,  10,  11,  12,  13 ],
        [   0,   0, 119, 120 ],
        [ ],
        [   0,   0,  34,   0,   0,   6 ],
        [   0,   0,  50,  51,   0,  22 ],
        [   0,   0,  62,  63 ],
        [   0,   0,  73,  74 ],
        [   0,   0,  88,  89 ],
        [   0,   1,  64,  65 ],
        [   0,   1,  75,  76 ],
        [   0,   1,  90,  91 ],
        [   0,   1,  29 ],
        [  28,  44,  45,   1,   0,   0, 110 ],
        [  58,  59,  60,   0,   0,   0, 121, 122 ]
    ],
    "powerboots": [
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [   0,   7,  26,  27 ],
        [   0,  23,  24],
        [  38,  39,  40,  41,  0,   0,  42 ],
        [  54,  55,  56,   0,  0 ]
    ],
    "varia": [
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [ ],
        [   0,   1,  9 ],
        [   0,   1, 25 ],
        [  28,  44,  45,   1,   0,   0, 110 ],
        [  58,  59,  60,   0,   0,   0, 121, 122 ]
    ]
}

def coord_calc(origin, dims):
    '''
    Calculate coordinates of a cell
    '''
    x1, x2 = origin
    w, h = dims
    return (x1, x2, w + x1, h+ x2)

def paperdoll_test(mode):
    '''
    Splice up cells
    '''
    with Image.open(os.path.join(
            "resources",
            "app",
            "snes",
            "metroid3",
            "samus",
            "sheets",
            "paperdoll",
            "arima",
            "base.png"
        )
    ) as paperdoll_image:
        paperdoll = {}
        cell_specs = {}

        for row in range(0, int(72/8)):
            for col in range(0, int(128/8)):
                cellID = arimaCells[row][col]
                if cellID != 0:
                    cell_specs[cellID] = coord_calc((col * 8, row * 8), (8, 8))

        for cellID, cell_coords in cell_specs.items():
            cropped_image = paperdoll_image.crop(cell_coords)
            colors = cropped_image.getcolors()
            paperdoll[cellID] = cropped_image
            if "save" in mode:
                cropped_image.save(
                    os.path.join(base_path_user, "cells", str(cellID) + ".png")
                )
        # VariaBoots -> Power -> PowerBoots
        # VariaBoots -> Varia
        for suit_type in ["variaboots", "varia", "power", "powerboots"]:
            base_image = None
            # print(suit_type)
            if suit_type == "variaboots":
                base_image = Image.new(
                    mode="RGB",
                    size=(64, 136),
                    color=(0, 0, 0)
                )
            elif suit_type in ["power", "varia"]:
                base_image = Image.open(
                    os.path.join(base_path_user, "variaboots" + ("-mirrors" if "mirror" in mode else "") + ".png")
                )
            elif suit_type == "powerboots":
                base_image = Image.open(
                    os.path.join(base_path_user, "power" + ("-mirrors" if "mirror" in mode else "") + ".png")
                )
            y = 0
            didMirror = False
            for arimaRow in arimaSuits[suit_type]:
                x = 0
                for cellID in arimaRow:
                    if cellID != 0:
                        base_image.paste(
                            paperdoll[cellID],
                            (x, y)
                        )
                        doMirror = len(arimaRow) <= 4
                        row = int(y / 8)
                        col = int(x / 8)
                        mirXes = {
                          "do": [
                              "6:2",
                              "6:3",
                              "8:4",
                              "9:3",
                              "9:4",
                              "16:3",
                              "16:4",
                              "17:1",
                              "17:3"
                          ],
                          "dont": [
                              "10:2"
                          ]
                        }
                        if not doMirror:
                            doMirror = f"{row+1}:{col+1}" in mirXes["do"]
                        if doMirror:
                            doMirror = f"{row+1}:{col+1}" not in mirXes["dont"]

                        if "mirror" in mode and doMirror:
                            didMirror = True
                            mirCol = 7 - col
                            # print(f"MIRROR: {str(col)} <-> {str(mirCol)} {cellID}")
                            mX = mirCol * 8
                            mY = y
                            base_image.paste(
                                paperdoll[cellID].transpose(Image.FLIP_LEFT_RIGHT),
                                (mX, mY)
                            )
                    x += 8
                y += 8
            if "save" in mode:
                base_image.save(
                    os.path.join(
                        base_path_user,
                        suit_type + ("-mirrors" if didMirror else "") + ".png"
                    )
                )
            # print()
    if "mirror" not in mode:
        bin_image = Image.new(
            mode="RGB",
            size=(128, 72),
            color=(0, 0, 0)
        )
        for suit_type in ["variaboots","varia","power","powerboots"]:
            base_image = None
            base_image = Image.open(
                os.path.join(base_path_user, suit_type + ".png")
            )
            # print(suit_type)
            for [row, arimaRow] in enumerate(arimaSuits[suit_type]):
                for [col, cellID] in enumerate(arimaRow):
                    if cellID != 0:
                        binCol = 0
                        binRow = 0
                        for [r, rr] in enumerate(arimaCells):
                            if cellID in rr:
                                binCol = rr.index(cellID)
                                binRow = r
                        x = binCol * 8
                        y = binRow * 8
                        bin_image.paste(
                            paperdoll[cellID],
                            (x, y)
                        )
                        # print(row, col, cellID)
            # print()
        bin_image.save(
            os.path.join(
                base_path_user,
                "binary.png"
            )
        )

# paperdoll_test("")
paperdoll_test("save")
paperdoll_test("savemirror")
