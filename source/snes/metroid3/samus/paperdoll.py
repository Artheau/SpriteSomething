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
import json
import os
from string import ascii_uppercase
from PIL import Image
# from source.meta.common import common

suit_defns = {
    "power": [
        [ "A0", "A1", "A2", "A3" ],
        [ "B0", "B1", "B2", "B3" ],
        [ "C0", "C1", "C2", "C3" ],
        [ "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7" ],
        [ "E0", "E1", "E2", "E3" ],
        [ "F0", "F1", "F2", "F3", "F4" ],
        [ "G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7" ],
        [ "H0", "H1", "H2", "H3", "  ", "H5", "H6", "H7" ],
        [ "I0", "I1", "I2", "I3", "  ", "  ", "I6", "I7" ],
        [ "  ", "J1", "J2", "J3" ],
        [ "  ", "  ", "K2", "K3" ],
        [ "  ", "  ", "L2", "L3" ],
        [ "  ", "  ", "M2", "M3" ],
        [ "  ", "  ", "N2", "N3" ],
        [ "  ", "O1", "O2", "  ", "  ", "  ", "  ", "O7" ],
        [ "P0", "P1", "P2", "  ", "  ", "  ", "P6", "P7" ],
        [ "Q0", "Q1", "Q2", "  ", "  ", "  ", "Q6", "Q7" ]
    ],
    "powerboots": [
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  ", "N1", "N2" ],
        [ "  ", "O1", "O2" ],
        [ "P0", "P1", "P2", "P3", "  ", "  ", "P6" ],
        [ "Q0", "Q1", "Q2", "  ", "  ", "  ", "Q6" ]
    ],
    "varia": [
        [ "  " ],
        [ "B0", "B1", "B2" ],
        [ "C0", "C1", "C2" ],
        [ "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7" ],
        [ "  ", "  ", "E2", "E3" ],
        [ "  " ],
        [ "  ", "  ", "G2", "  ", "  ", "G5" ],
        [ "  ", "  ", "H2", "H3", "  ", "H5" ],
        [ "  ", "  ", "I2", "I3", "  ", "  " ],
        [ "  ", "  ", "J2", "J3", "  ", "  " ],
        [ "  ", "  ", "K2", "K3", "  ", "  " ],
        [ "  ", "  ", "L2", "L3", "  ", "  " ],
        [ "  ", "  ", "M2", "M3", "  ", "  " ],
        [ "  ", "  ", "N2", "N3", "  ", "  " ],
        [ "  ", "  ", "O2", "  ", "  ", "  " ],
    ],
    "variaboots": [
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  " ],
        [ "  ", "N1", "N2" ], # just N2
        [ "  ", "O1", "O2" ],
        [ "P0", "P1", "P2", "P3", "  ", "  ", "P6" ],
        [ "Q0", "Q1", "Q2", "  ", "  ", "  ", "Q6" ]
    ]
}

mirrorCells = {
    "A3":"A4", "A2":"A5", "A1":"A6", "A0":"A7",
    "B3":"B4", "B2":"B5", "B1":"B6", "B0":"B7",
    "C3":"C4", "C2":"C5", "C1":"C6", "C0":"C7",
    "D":"0",
    "E3":"E4", "E2":"E5", "E1":"E6", "E0":"E7",
               "F2":"F5", "F1":"F6", "F0":"F7",
    "G":"0",
    "H3":"H4",
    "I3":"I4", "I2":"I5",
    "J3":"J4", "J2":"J5",
    "K3":"K4", "K2":"K5",
    "L3":"L4", "L2":"L5",
    "M3":"M4", "M2":"M5",
    "N3":"N4", "N2":"N5",
               "O2":"O5", "O1":"O6",
    "P3":"P4", "P2":"P5",
               "Q2":"Q5"
}

arimaCells = [
    [   1,   2,   3,   4,   5,   0,   0,   0,   6,   7,   8,   9,  10,  11,  12,  13 ],
    [  14,  15,  16,  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,  27,  28,  29 ],
    [  30,  31,  32,  33,  34,  35,  36,  37,  38,  39,  40,  41,  42,  43,  44,  45 ],
    [  46,  47,  48,  49,  50,  51,  52,  53,  54,  55,  56,   0,  57,  58,  59,  60 ],
    [  00,  00,  00,  61,  62,  63,  64,  65,   0,   0,   0,   0,  66,  67,  68,   0 ],
    [  69,  70,  71,  72,  73,  74,  75,  76,  77,  78,  79,  80,  81,  82,  83,   0 ],
    [  84,  85,  86,  87,  88,  89,  90,  91,   0,   0,  92,  93,  94,  95,  96,   0 ],
    [  97,  98,  99, 100, 101, 102, 103, 104,   0, 105, 106, 107, 108, 109, 110, 111 ],
    [ 112, 113, 114, 115,   0,   0,   0,   0,   0, 116, 117, 118, 119, 120, 121, 122 ]
]

arimaSuits = {
    "power": [
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
        [   0,   0,  64,  65 ],
        [   0,   0,  75,  76 ],
        [   0,   0,  90,  91 ],
        [   0,   0,  29 ],
        [  28,  44,  45,   0,   0,   0, 110 ],
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
        [   0,   0,  26,  27 ]
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
        [   0,   0,  9 ],
        [   0,   0, 25 ]
    ],
    "variaboots": [
        [   0,   0,  61 ],
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
        [   0,  23,  34 ],
        [  38,  39,  40,  41,   0,   0,  42,  43 ],
        [  54,  55,  56,   0,   0,   0,  57 ]
    ]
}

binaryCells = [
    [ # 1
        "aA0", "pF1", "pF2", "pF3", "pF4", "aA0", "aA0", "aA0",
        "pG5", "bN1", "vbN2", "vN2", "pD4", "pD5", "pD6", "pD7"
    ],
    [ # 2
        "pG0", "pG1", "vG2", "pG3", "pG4", "vG5", "pG6", "pG7",
        "pH5", "bO1", "bO2", "vO2", "aA0", "vN3", "pO1", "pO2"
    ],
    [ # 3
        "pH0", "pH1", "vH2", "vH3", "pG2", "vH5", "pH6", "pH7",
        "bP0", "bP1", "bP2", "bP3", "aA0", "pP7", "pP1", "pP2"
    ],
    [ # 4
        "pI0", "pI1", "vI2", "vI3", "pH2", "pH3", "pI6", "pI7",
        "bQ0", "bQ1", "bQ2", "aA0", "aA0", "pQ0", "pQ1", "pQ2"
    ],
    [ # 5
        "aA0", "aA0", "aA0", "pA3", "pI2", "pI3", "pL2", "pL3",
        "aA0", "aA0", "aA0", "aA0", "pB0", "pB1", "pB2", "aA0"
    ],
    [ # 6
        "vB0", "vB1", "vB2", "pB3", "pJ2", "pJ3", "pM2", "pM3",
        "aA0", "pJ1", "vJ2", "vJ3", "pC0", "pC1", "pC2", "aA0"
    ],
    [ # 7
        "vC0", "vC1", "vC2", "pC3", "pK2", "pK3", "pN2", "pN3",
        "aA0", "aA0", "vK2", "vK3", "pD0", "pD1", "pD2", "aA0"
    ],
    [ # 8
        "vD0", "vD1", "vD2", "vD3", "vD4", "vD5", "vD6", "vD7",
        "aA0", "vL1", "vL2", "vL3", "pD2", "pD3", "pP6", "aA0"
    ],
    [ # 9
        "pE0", "pE1", "pE2", "vE3", "vE4", "aA0", "aA0", "aA0",
        "aA0", "vM1", "vM2", "vM3", "pE2", "pE3", "pQ6", "pQ7"
    ]
]

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
    # with Image.open(
    #     common.get_resource(
    #         [
    #             "app",
    #             "snes",
    #             "metroid3",
    #             "samus",
    #             "sheets",
    #             "paperdoll"
    #         ],
    #         "bases.png"
    #     )
    # ) as paperdoll_image:
    with Image.open(os.path.join(
            "resources",
            "app",
            "snes",
            "metroid3",
            "samus",
            "sheets",
            "paperdoll",
            "bases.png"
        )
    ) as paperdoll_image:
        paperdoll = {}
        cell_specs = {}
        used_bin = {}
        unused = []

        for row in range(0, 17):
            for col in range(0, 8 * 4):
                cellID = list(ascii_uppercase)[row]
                cellID = cellID + str(col)
                cell_specs[cellID] = coord_calc((col * 8, row * 8), (8, 8))

        for cellID, cell_coords in cell_specs.items():
            cropped_image = paperdoll_image.crop(cell_coords)
            colors = cropped_image.getcolors()
            if len(colors) == 1:
                unused.append(cellID)
            paperdoll[cellID] = cropped_image
            if "save" in mode:
                cropped_image.save(
                    os.path.join(
                        ".",
                        "resources",
                        "user",
                        "snes",
                        "metroid3",
                        "samus",
                        "sheets",
                        "paperdoll",
                        "cells",
                        cellID + ".png"
                    )
                )
        # print(json.dumps(cell_specs, indent=2))
        for [suit_type, cell_list] in suit_defns.items():
            baseID = "power"
            baseID = suit_type
            print(baseID)
            print(cell_list)
            base_image = None
            if suit_type == "power":
                base_image = Image.new(
                    mode="RGB",
                    size=(64, 136),
                    color=(0, 0, 0)
                )
            elif suit_type in [
                "powerboots",
                "varia",
                "final"
            ]:
                base_image = Image.open(
                    os.path.join(
                        "resources",
                        "user",
                        "snes",
                        "metroid3",
                        "samus",
                        "sheets",
                        "paperdoll",
                        "power" + ("-mirrors" if "mirror" in mode else "") + ".png"
                    )
                )
            elif suit_type in [
                "variaboots",
                "finalboots"
            ]:
                base_image = Image.open(
                    os.path.join(
                        "resources",
                        "user",
                        "snes",
                        "metroid3",
                        "samus",
                        "sheets",
                        "paperdoll",
                        "varia" + ("-mirrors" if "mirror" in mode else "") + ".png"
                    )
                )
            this_image = base_image
            didMirror = False
            for cellRow in cell_list:
                for cellID in cellRow:
                    if cellID.strip() != "":
                        y = ascii_uppercase.index(cellID[:1])
                        x = cellID[1:]
                        xOffset = 0
                        if baseID == "powerboots":
                            xOffset += 8
                        elif baseID == "varia":
                            xOffset += 8 * 2
                        elif baseID == "variaboots":
                            xOffset += 8 * 3
                        cellMsg = f"{suit_type} ({baseID}), {cellID}, ({x},{y})"
                        mirrorCellID = ""
                        if cellID in mirrorCells:
                            mirrorCellID = mirrorCells[cellID]
                            cellMsg += f" <-> ({mirrorCellID})"
                        print(cellMsg)
                        cellID = cellID[:1] + str(int(x) + xOffset)
                        this_image.paste(
                            paperdoll[cellID],
                            (int(x) * 8, int(y) * 8)
                        )
                        if "mirror" in mode and mirrorCellID != "":
                            didMirror = True
                            x = mirrorCellID[1:]
                            this_image.paste(
                                paperdoll[cellID].transpose(Image.FLIP_LEFT_RIGHT),
                                (int(x) * 8, int(y) * 8)
                            )
            saveName = os.path.join(
                "resources",
                "user",
                "snes",
                "metroid3",
                "samus",
                "sheets",
                "paperdoll"
            )
            saveName = os.path.join(saveName, suit_type + ("-mirrors" if didMirror else "") + ".png")
            this_image.save(saveName)

    bin_image = Image.new(
        mode="RGB",
        size=(128, 72)
    )

    for row, binaryRow in enumerate(binaryCells):
        for col, binaryCell in enumerate(binaryRow):
            if not binaryCell.startswith("a"):
                suit_type = "power"
                if "v" in binaryCell:
                    suit_type = "varia"
                if "b" in binaryCell:
                    suit_type += "boots"
                if not suit_type in used_bin:
                    used_bin[suit_type] = []
                x = col
                y = row
                cellID = binaryCell[1:]
                xOffset = 0
                if suit_type == "powerboots":
                    xOffset += 8
                elif suit_type == "varia":
                    xOffset += 8 * 2
                elif suit_type == "variaboots":
                    xOffset += 8 * 3
                cellY = "".join(filter(str.isupper, cellID))
                cellX = "".join(filter(str.isdigit, cellID))
                cellID = cellY + str(int(cellX) + xOffset)
                used_bin[suit_type].append(binaryCell)
                used_bin[suit_type].append(f"{cellY}{cellX}, {cellID}")
                used_bin[suit_type].sort()

                bin_image.paste(
                    paperdoll[cellID],
                    (x * 8, y * 8)
                )
                print(
                    ascii_uppercase[row] + str(col),
                    binaryCell,
                    suit_type,
                    cellID
                )
        print()
    saveName = os.path.join(".","resources","user","snes","metroid3","samus","sheets","paperdoll","binary.png")
    bin_image.save(saveName)
    for [used, usedB] in used_bin.items():
        print(used,usedB)
    for [used, usedB] in used_bin.items():
        print(used)
        topost = []
        for i in ascii_uppercase:
            if i == "R":
                break
            for j in range(0, 8):
                offset = 0
                if "powerb" in used:
                    offset = 8 * 1
                elif used[:1] == "p":
                    offset = 0
                elif "variab" in used:
                    offset = 8 * 3
                elif used[:1] == "v":
                    offset = 8 * 2
                check = i + str(j + offset)
                if (used[:1] + check) not in usedB and check not in unused:
                    topost.append(check)
        print(topost)


# paperdoll_test("")
# paperdoll_test("save")
paperdoll_test("savemirror")
