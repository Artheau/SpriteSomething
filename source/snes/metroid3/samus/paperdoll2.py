# pylint: disable=invalid-name,
'''
New image splicer
'''
import os
from string import ascii_uppercase
from PIL import Image

export_folder = ""

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

arimaCells = [
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

mirrorCells = {
                                "A3":"A4",
  "B0":"B7","B1":"B6","B2":"B5","B3":"B4",
  "C0":"C7","C1":"C6","C2":"C5","C3":"C4",
  "DD":"DD",
  "E0":"E7","E1":"E6","E2":"E5","E3":"E4",
  "F0":"F7","F1":"F6","F2":"F5","F3":"F4",
            "G1":"G6","G2":"G5",
                                "H3":"H4",
                      "I2":"I5","I3":"I4",
                      "J2":"J5","J3":"J4",
                      "K2":"K5","K3":"K4",
            "L1":"L6","L2":"L5","L3":"L4",
            "M1":"M6","M2":"M5","M3":"M4",
                      "N2":"N5","N3":"N4",
            "O1":"O6","O2":"O5",
                      "P2":"P5","P3":"P4",
  "Q0":"Q7",          "Q2":"Q5"
}

# Power -> Power Boots
# Power -> Varia
# Varia -> Varia Boots
arimaSuits = {
  "power": [
    #   0    1    2    3    4    5    6    7
    [   0,   0,   0,  61 ],                     # A
    [  66,  67,  68,  72 ],                     # B
    [  81,  82,  82,  87 ],                     # C
    [  94,  95,  96, 109,  10,  11,  12,  13 ], # D
    [ 112, 113, 119, 120 ],                     # E
    [   1,   2,   3,   4,   5 ],                # F
    [  14,  15,  34,  17,  18,   6,  20,  21 ], # G
    [  30,  31,  50,  51,   0,  22,  36,  37 ], # H
    [  46,  47,  62,  63,   0,   0,  52,  53 ], # I
    [   0,  78,  73,  74 ],                     # J
    [   0,   0,  88,  89 ],                     # K
    [   0, 105,  64,  65 ],                     # L
    [   0, 116,  75,  76 ],                     # M
    [   0,   0,  90,  91 ],                     # N
    [   0,   0,  29,   0 ],                     # O
    [  28,  44,  45,   0,   0,   0, 110,  43 ], # P, 45,41,41,45
    [  58,  59,  60,   0,   0,   0, 121, 122 ]  # Q
  ],
  "powerboots": [
    [],                                         # A
    [],                                         # B
    [],                                         # C
    [],                                         # D
    [],                                         # E
    [],                                         # F
    [],                                         # G
    [],                                         # H
    [],                                         # I
    [],                                         # J
    [],                                         # K
    [],                                         # L
    [],                                         # M
    [   0,   0,  26,  27 ],                     # N
    [   0,  23,  24 ],                          # O
    [  38,  39,  40,  41,   0,   0,  42,  43 ], # P
    [  54,  55,  56,   0,   0,   0,  57,   0 ]  # Q
  ],
  "varia": [
    [],                                         # A
    [  69,  70,  71 ],                          # B
    [  84,  85,  86 ],                          # C
    [  97,  98,  99, 100, 101, 102, 103, 104 ], # D
    [ 112, 113, 114, 115],                      # E
    [   1,   2,   3,   4,   5],                 # F
    [  14,  15,  16,  17,  18,  19,  20,  21],  # G
    [  30,  31,  32,  33,   0,  35,  36,  37],  # H
    [  46,  47,  48,  49,   0,   0,  52,  53],  # I
    [   0,  78,  79,  80],                      # J
    [   0,   0,  92,  93],                      # K
    [   0, 105, 106, 107],                      # L
    [   0, 116, 117, 118],                      # M
    [   0,   0,   9],                           # N
    [   0,   0,  25],                           # O
    [  28,  44,  45,   0,   0,   0, 110,  43],  # P
    [  54,  55,  56,   0,   0,   0,  57, 122]   # Q
  ],
  "variaboots": [
    [],                                         # A
    [],                                         # B
    [],                                         # C
    [],                                         # D
    [],                                         # E
    [],                                         # F
    [],                                         # G
    [],                                         # H
    [],                                         # I
    [],                                         # J
    [],                                         # K
    [],                                         # L
    [],                                         # M
    [   0,   0,   8,  27 ],                     # N
    [   0,  23,  24 ],                          # O
    [  38,  39,  40,  41,   0,   0,  42,  43 ], # P
    [  54,  55,  56,   0,   0,   0,  57,   0 ]  # Q
  ]
}

arimaSuits = {
  "power": [
    [0,0,0,68],
    [77,78,79,84],
    [93,94,95,100],
    [109,110,125,126,13,14,15,16],
    [1,2,3,4,5],
    [17,18,37,20,21,9,23,24],
    [33,34,53,54],
    [49,50,69,70],
    [0,90,85,86],
    [0,0,101,102],
    [0,0,71,72],
    [0,0,87,88],
    [0,0,103,104],
    [0,0,32,0],
    [31,47,48,0,0,0,127,46],
    [62,63,64,0,0,0,143,0]
  ],
  "powerboots": [
    [],                                         # A
    [],                                         # B
    [],                                         # C
    [],                                         # D
    [],                                         # E
    [],                                         # F
    [],                                         # G
    [],                                         # H
    [],                                         # I
    [],                                         # J
    [],                                         # K
    [],                                         # L
    [],                                         # M
    [0,10,29,104],
    [0,26,27],
    [41,42,43,44],
    [57,58,59,0,0,0,61]
  ],
  "varia": [
    [],
    [81,82,83],
    [97,98,99],
    [113,114,115,116,117,118,119,120],
    [0,0,131,132],
    [0,0,19,0,0,22],
    [0,0,35,36,0,38,39,40],
    [0,0,51,52],
    [0,0,91,92],
    [0,0,0,107,108],
    [0,122,123,124],
    [0,138,139,140],
    [0,0,12],
    [0,0,28],
    [],
    [0,0,0,0,0,0,0,144]
  ],
  "variaboots": [
    [],                                         # A
    [],                                         # B
    [],                                         # C
    [],                                         # D
    [],                                         # E
    [],                                         # F
    [],                                         # G
    [],                                         # H
    [],                                         # I
    [],                                         # J
    [],                                         # K
    [],                                         # L
    [],                                         # M
    [0,10,11,0],
    [0,26,27],
    [41,42,43,44],
    [57,58,59,0,0,0,61]
  ]
}

cell_specs = {}
paperdoll = {}

def coord_calc(origin, dims):
    '''
    Calculate coordinates of a cell
    '''
    x1, x2 = origin
    w, h = dims
    return (x1, x2, w + x1, h+ x2)

def my_pad(input):
    '''
    strpad
    '''
    return str(input).strip().rjust(3, "0")

def make_cell_specs():
    '''
    Get cell placements within the binary sheet
    '''
    print("Identifying cells in binary sheet")
    print(" Input: Defined arrays in the code")
    print(" Output: Populated cell_specs object")
    for row in range(0, int(72/8)):
        for col in range(0, int(128/8)):
            cellID = arimaCells[row][col]
            if cellID != 0:
                cell_specs[cellID] = coord_calc((col * 8, row * 8), (8, 8))
    return cell_specs

def splice_up_binary(mode, sheet):
    '''
    Splice up the binary sheet
    '''
    if sheet is None:
        sheet = "binary-natural"
    print(f"Splicing binary sheet: {sheet}")
    print(f" Input: Imported binary sheets")
    print(f" Output: Populated paperdoll object")
    print(f" Optional Output: Individual cell images ({os.path.join(base_path_user,export_folder,'cells')})")
    blank_image = Image.new(
        mode="RGB",
        size=(8, 8),
        color=(0, 0, 0)
    )
    paperdoll["-1"] = blank_image
    if "save" in mode:
        print(f" Saving cells")
        blank_image.save(
            os.path.join(
                base_path_user,
                export_folder,
                "cells",
                "-1.png"
            )
        )
    for cellID, cell_coords in cell_specs.items():
        colorGoal = 5
        colorGoal = 2
        if sheet == "binary2":
            colorGoal = 2
        elif sheet == "binary3":
            colorGoal = 2
        elif sheet == "binary-natural":
            colorGoal = 2
        cropped_image = images[sheet].crop(cell_coords)
        cropped_image.convert(mode="RGB")
        colors = cropped_image.getcolors()
        if len(colors) >= colorGoal or cellID == 1:
            paperdoll[my_pad(cellID)] = cropped_image
            if "save" in mode:
                cropped_image.save(
                    os.path.join(
                        base_path_user,
                        export_folder,
                        "cells",
                        str(cellID) + ".png"
                    )
                )
        if len(colors) < colorGoal:
            print(f"  CellID: #{cellID} [Colors: {colors}] [# Colors: {len(colors)}] is invalid!")

def export_suit(suit_type):
    '''
    Export a suit
    '''
    print(f"Exporting Suit: {suit_type}")
    print(f" Input: Suit type; paperdoll object")
    print(f" Output: {os.path.join(base_path_user,export_folder,suit_type + '.png')}")
    display = "tileID"
    base_suits = [ "power" ]
    cellIDs = {}
    if "power" in suit_type:
        base_suits = [ "power" ]
    if "varia" in suit_type:
        base_suits = [ "power" ]
    if "variaboots" in suit_type:
        base_suits.append("varia")
    for base_suit in base_suits:
        print(f" Base Suit: {base_suit}")
        if base_suit in arimaSuits:
            for [row, arimaRow] in enumerate(arimaSuits[base_suit]):
                if row not in cellIDs:
                    cellIDs[row] = ["..." if display == "tileID" else ".."] * 8
                for [col, arimaCell] in enumerate(arimaRow):
                    if row < len(arimaSuits[suit_type]):
                        if len(arimaSuits[suit_type][row]) > 0:
                            if col < len(arimaSuits[suit_type][row]):
                                if arimaSuits[suit_type][row][col]:
                                    arimaCell = arimaSuits[suit_type][row][col]
                    cellID = f"{ascii_uppercase[row]}{col}"
                    if arimaCell != 0:
                        tileID = str(arimaCell).rjust(3)
                        cellIDs[row][col] = tileID
                        if cellID in mirrorCells:
                            colID = int("".join(filter(str.isdigit, mirrorCells[cellID])))
                            cellIDs[row][colID] = "M" + tileID.strip().rjust(3)
            this_image = Image.new(
                mode="RGB",
                size=(64, 136),
                color=(0, 0, 0)
            )
            for [rowID, cellRow] in cellIDs.items():
                for [colID, tileID] in enumerate(cellRow):
                    x = colID * 8
                    y = rowID * 8
                    cellImage = paperdoll["-1"]
                    tileID = str(tileID)
                    doMirror = False
                    if ".." not in tileID.strip() and \
                        tileID.strip() != "0":
                        doMirror = "M" in tileID
                        tileID = tileID.replace("M", "")
                        cellImage = paperdoll[my_pad(tileID)]
                    else:
                        tileID = tileID.replace("M", "")
                    this_image.paste(
                        cellImage.transpose(Image.FLIP_LEFT_RIGHT) if doMirror else cellImage,
                        (x, y)
                    )
                    print(tileID, end="|")
                print()
            this_image.save(
                os.path.join(
                    base_path_user,
                    export_folder,
                    "output",
                    suit_type + ".png"
                )
            )
    print()

def splice_suit(filename):
    suit_type = "power"
    base_suits = [ "power" ]
    for check_type in [
        "powerboots",
        "variaboots",
        "varia"
    ]:
        if check_type in filename:
            suit_type = check_type
            break
    if "power" in suit_type:
        base_suits = [ "power" ]
    if "varia" in suit_type:
        base_suits = [ "power" ]
    if "variaboots" in suit_type:
        base_suits.append("varia")

    print(f" Splicing suit: {suit_type}")
    this_image = Image.open(
        os.path.join(
            base_path_user,
            export_folder,
            filename + ".png"
        )
    )
    bin_image = Image.new(
        mode="RGB",
        size=(128, 72),
        color=(0, 0, 0)
    )

    cellIDs = {}
    for base_suit in base_suits:
        print(f"  Processing base: {base_suit}")
        for [row, arimaRow] in enumerate(arimaSuits[base_suit]):
            if row not in cellIDs:
                cellIDs[row] = [0] * 8
            for [col, arimaCell] in enumerate(arimaRow):
                if row < len(arimaSuits[suit_type]):
                    if len(arimaSuits[suit_type][row]) > 0:
                        if col < len(arimaSuits[suit_type][row]):
                            if arimaSuits[suit_type][row][col]:
                                arimaCell = arimaSuits[suit_type][row][col]
                cellIDs[row][col] = arimaCell

    # print(cellIDs)

    for [row, arimaRow] in cellIDs.items():
        for [col, tileID] in enumerate(arimaRow):
            x = col * 8
            y = row * 8
            rowID = ascii_uppercase[row]
            # print(f"{rowID}{col}[{my_pad(tileID)}]({my_pad(x)},{my_pad(y)})", end=" | ")
            tileX = -1
            tileY = -1
            for [binRowID, binRow] in enumerate(arimaCells):
                if tileID in binRow:
                    tileX = binRow.index(tileID) * 8
                    tileY = binRowID * 8
                    break
            if tileX > -1 and tileY > -1:
                bin_image.paste(
                    this_image.crop(coord_calc((x, y), (8, 8))),
                    (tileX, tileY)
                )
        # print()
    bin_image.save(
        os.path.join(
            base_path_user,
            export_folder,
            "output",
            suit_type + "-binary.png"
        )
    )

def combine_suits():
    combined_image = Image.new(
        mode="RGBA",
        size=(128, 72),
        color=(0, 0, 0, 255)
    )
    for filename in [
        "power",
        "powerboots",
        "varia",
        "variaboots"
    ]:
        this_image = Image.open(
            os.path.join(
                base_path_user,
                export_folder,
                filename + "-binary.png"
            )
        )
        newdata = []
        find = (0, 0, 0)
        this_image = this_image.convert("RGBA")
        for item in this_image.getdata():
            # print(item[:3] == find)
            append = (item[0], item[1], item[2], 255)
            if item[:3] == find:
                append = (0, 0, 0, 0)
            # print(append)
            newdata.append(append)
        this_image.putdata(newdata)
        combined_image.paste(
            this_image,
            (0, 0),
            this_image
        )
    combined_image.save(
        os.path.join(
            base_path_user,
            export_folder,
            "output",
            "combined.png"
        )
    )


def paperdoll_test(mode):
    '''
    Main Driver
    '''

    # Required
    make_cell_specs()

    # Optional section
    if True:
        # Take binary sheet and splice it into cells
        #  Optional: Save cells as images
        splice_up_binary(mode, "binary-clean")

    # Optional section
    if True:
        # Requires splice_up_binary()
        # Export suit from spliced-up binary sheet
        export_suit("power")
        export_suit("powerboots")
        export_suit("varia")
        export_suit("variaboots")

    # Optional section
    if False:
        # Convert composite suit into binary sheet
        splice_suit("power")
        splice_suit("powerboots")
        splice_suit("varia")
        splice_suit("variaboots")

        # Combine all binary sheets
        combine_suits()

        #TODO: Create MMX source and work with that for proof-of-concept

    print()


base_path_user = os.path.join(
    ".",
    "resources",
    "user",
    "snes",
    "metroid3",
    "samus",
    "sheets",
    "paperdoll",
    "labels"
)
for folder in ["cells", "output"]:
    if not os.path.isdir(
        os.path.join(
            base_path_user,
            export_folder,
            folder
        )
    ):
        os.makedirs(
            os.path.join(
                base_path_user,
                export_folder,
                folder
            )
        )

images = {}
print(f"Importing binary sheets: {os.path.join(base_path_user,'input')}")
for filename in [
    "binary2",
    "binary3",
    "binary-clean",
    "binary-natural"
]:
    if os.path.isfile(
        os.path.join(
            base_path_user,
            "input",
            f"{filename}.png"
        )
    ):
        print(f" Importing binary sheet: {filename}")
        images[filename] = Image.open(
            os.path.join(
                base_path_user,
                "input",
                f"{filename}.png"
            )
        )

paperdoll_test("")
# paperdoll_test("save")
