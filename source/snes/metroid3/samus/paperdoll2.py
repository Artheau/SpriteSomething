# pylint: disable=invalid-name,
'''
New image splicer
'''
import os
from string import ascii_uppercase
from PIL import Image

export_folder = ""

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
    [   0,   0,   0,  68 ],                     # A
    [  77,  78,  79,  84 ],                     # B
    [  93,  94,  95, 100 ],                     # C
    [ 109, 110, 125, 126,  13,  14,  15,  16 ], # D
    [ 129, 130, 141, 142 ],                     # E
    [   1,   2,   3,   4,   5 ],                # F
    [  17,  18,  37,  20,  21,   9,  23,  24 ], # G
    [  33,  34,  53,  54,   0,  25,  39,  40 ], # H
    [  49,  50,  69,  70,   0,   0,  55,  56 ], # I
    [   0,  90,  85,  86 ],                     # J
    [   0,   0, 101, 102 ],                     # K
    [   0,   0,  71,  72 ],                     # L
    [   0,   0,  87,  88 ],                     # M
    [   0,   0, 103, 104 ],                     # N
    [   0,   0,  32,   0 ],                     # O
    [  31,  47,  48,   0,   0,   0, 127,  46 ], # P
    [  62,  63,  64,   0,   0,   0, 143,   0 ]  # Q
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
    [   0,  10,  29, 104],                      # N
    [   0,  26,  27],                           # O
    [  41,  42,  43,  44],                      # P
    [  57,  58,  59,   0,   0,   0,  61]        # Q
  ],
  "varia": [
    [],                                         # A
    [  81,  82,  83 ],                          # B
    [  97,  98,  99 ],                          # C
    [ 113, 114, 115, 116, 117, 118, 119, 120 ], # D
    [ 129, 130, 131, 132 ],                     # E
    [   1,   2,   3,   4,   5 ],                # F
    [   0,   0,  19,   0,   0,  22 ],           # G
    [   0,   0,  35,  36,   0,  38,  39,  40 ], # H
    [   0,   0,  51,  52,   0,   0,  55,  56 ], # I
    [   0,  90,  91,  92 ],                     # J
    [   0,   0, 107, 108 ],                     # K
    [   0, 122, 123, 124 ],                     # L
    [   0, 138, 139, 140 ],                     # M
    [   0,   0,  12 ],                          # N
    [   0,   0,  28 ],                          # O
    [],                                         # P
    [   0,   0,   0,   0,   0,   0,   0, 144 ]  # Q
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
    [   0,  10,  11,   0 ],                     # N
    [   0,  26,  27 ],                          # O
    [  41,  42,  43,  44 ],                     # P
    [  57,  58,  59,   0,   0,   0,  61 ]       # Q
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

def my_pad(item):
    '''
    strpad
    '''
    return str(item).strip().rjust(3, "0")

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

def splice_up_binary(mode=None, workingdir=os.path.join("."), sheet=None):
    '''
    Splice up the binary sheet
    '''
    if sheet is None:
        sheet = "binary-natural"
    print(f"Splicing binary sheet: {sheet}")
    print( " Output: Populated paperdoll object")
    print(f" Optional Output: Individual cell images ({os.path.join(workingdir,'cells')})")
    blank_image = Image.new(
        mode="RGB",
        size=(8, 8),
        color=(0, 0, 0)
    )
    paperdoll["-1"] = blank_image
    if "save" in mode:
        print(" Saving cells")
        blank_image.save(
            os.path.join(
                workingdir,
                "cells",
                "-1.png"
            )
        )

    # import sheet
    images[sheet] = Image.open(
        os.path.join(
            workingdir,
            "input",
            "binary",
            f"{sheet}.png"
        )
    )
    sheet_size = images[sheet].size
    if sheet_size != (128, 72):
        print(f"{sheet} invalid size; is {sheet_size}; should be (128, 72)")
        return

    for cellID, cell_coords in cell_specs.items():
        colorGoal = 1
        cropped_image = images[sheet].crop(cell_coords)
        cropped_image.convert(mode="RGB")
        colors = cropped_image.getcolors()
        if len(colors) >= colorGoal or cellID == 1:
            paperdoll[my_pad(cellID)] = cropped_image
            if "save" in mode:
                cropped_image.save(
                    os.path.join(
                        workingdir,
                        "cells",
                        str(cellID) + ".png"
                    )
                )
        if len(colors) < colorGoal:
            print(f"  CellID: #{cellID} [Colors: {colors}] [# Colors: {len(colors)}] is invalid!")
    print(paperdoll.keys())

def export_suit(
    workingdir=os.path.join("."),
    suit_type="power"
):
    '''
    Export a suit
    '''
    print(f"Exporting Suit: {suit_type}")
    print( " Input: Suit type; paperdoll object")
    print(f" Output: {os.path.join(workingdir,'output',suit_type + '.png')}")
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
                    workingdir,
                    "output",
                    "composites",
                    f"{suit_type}.png"
                )
            )
    print()

def export_suits(workingdir=os.path.join(".")):
    '''
    Export one sheet with all four suits
    '''
    suits = Image.new(
        mode="RGBA",
        size=((64 * 4), 136),
        color=(0,0,0,0)
    )
    x = 0
    for suit_type in ["power", "powerboots", "varia", "variaboots"]:
        export_suit(workingdir, suit_type)
        img = Image.open(os.path.join(workingdir, "output", "composites", f"{suit_type}.png"))
        img_size = img.size
        if img_size != (64, 136):
            print(f"{suit_type} invalid size; is {img_size}; should be (64, 136)")
            return
        suits.paste(img, (x, 0, ))
        x += 64
    suits.save(os.path.join(workingdir, "output", "composites", "suits.png"))

def export_preview(workingdir=os.path.join(".")):
    '''
    Export Preview GIF
    '''
    print(" Exporting Preview GIF")

    image_list = []
    duration = .5
    gif_duration = 1000 * duration
    gif_durations = []
    print("  Getting base screen")
    for suit_type in ["power","powerboots","varia","variaboots"]:
        print(f"   Getting {suit_type}")
        suit_img = Image.open(
            os.path.join(
                workingdir,
                "output",
                "composites",
                f"{suit_type}.png"
            )
        )
        suit_img = suit_img.convert("RGBA")
        this_img = Image.open(
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
                "screen.png"
            )
        )
        this_img = this_img.convert("RGBA")
        this_img.paste(
            suit_img,
            (94,22,),
            suit_img
        )

        for label in [
            "samus-marquee",
            "suit",
            "misc",
            "boots",
            "beam",
            "samus-button"
        ]:
            label_path = os.path.join(
                workingdir,
                "input",
                "categories",
                f"{label}.png"
            )
            if not os.path.isfile(label_path):
                label_path = os.path.join(
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
                    f"{label}.png"
                )
            if os.path.isfile(label_path):
                label_img = Image.open(label_path)
                label_img.convert("RGBA")
                dest = (0,0)
                dests = {
                    "samus-marquee": (102,6),
                    "suit": (190,30),
                    "misc": (190,62),
                    "boots": (190,110),
                    "beam": (38,86),
                    "samus-button": (174,167)
                }
                if label in dests:
                    dest = dests[label]
                    print(f"    Pasting {label} label")
                    this_img.paste(
                        label_img,
                        dest
                    )

        for icon in [
            "boots",
            "varia"
        ]:
            if icon in suit_type:
                icon_img = Image.open(
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
                        "icons.png"
                    )
                )
                icon_img = icon_img.convert("RGBA")
                stats = {
                    "boots": {"origin": (16,0), "dest": (36,20)},
                    "varia": {"origin": (0,0), "dest": (20,20)}
                }
                icon_img = icon_img.crop(
                    coord_calc(
                        stats[icon]["origin"],
                        (16,16)
                    )
                )
                print(f"    Pasting {icon} icon")
                this_img.paste(
                    icon_img,
                    stats[icon]["dest"],
                    icon_img
                )

        image_list.append(this_img)
        gif_durations.append(gif_duration)
    image_list[0].save(
        os.path.join(
            workingdir,
            "output",
            "composites",
            "screen.gif"
        ),
        format="GIF",
        append_images=image_list[1:],
        save_all=True,
        transparency=255,
        disposal=2,
        duration=gif_durations,
        loop=0,
        optimize=False
    )

def splice_suit(
    workingdir=os.path.join("."),
    filename="power"
):
    '''
    Splice composite into binary sheet
    '''
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
            workingdir,
            "input",
            "composites",
            filename + ".png"
        )
    )

    this_size = this_image.size
    if this_size != (64, 136):
        print(f"{filename} invalid size; is {this_size}; should be (64, 136)")
        return

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
            workingdir,
            "output",
            "binary",
            f"binary-{suit_type}.png"
        )
    )

def combine_suits(workingdir):
    '''
    Combine spliced binary sheets into one binary sheet
    '''
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
                workingdir,
                "output",
                "binary",
                f"binary-{filename}.png"
            )
        )
        this_size = this_image.size
        if this_size != (128, 72):
            print(f"{filename} invalid size; is {this_size}; should be (128, 72)")
            return

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
    misc_image = Image.open(
        os.path.join(
            workingdir,
            "..",
            "samus",
            "input",
            "categories",
            "misc.png"
        ).replace("user","app"))
    if misc_image.size != (24, 8):
        print(f"misc.png invalid size; is {misc_image.size}; should be (24, 8)")
    combined_image.paste(
        misc_image,
        (0, 32)
    )
    combined_image.save(
        os.path.join(
            workingdir,
            "output",
            "binary",
            "combined.png"
        )
    )

images = {}

def setupDirs(workingdir=os.path.join(".")):
    '''
    Create subdirs
    '''
    for folder in [
        "cells",
        "output",
        os.path.join("output", "binary"),
        os.path.join("output", "composites")
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

def mandatory():
    '''
    Identify cells in binary sheet
    Just an array
    '''
    make_cell_specs()

def binSheetToCells(
    mode=None,
    workingdir=os.path.join("."),
    binfilename="binary"
):
    '''
    Take binary sheet and splice it into cells
    Optional: Save cells as images
    '''
    splice_up_binary(
        mode,
        workingdir,
        binfilename
    )

def compositesToBinSheet(
    workingdir=os.path.join(".")
):
    '''
    Take set of composite sheets
    Make a binary sheet for each
    Combine make binary sheets
    '''
    # IN:  cwd/input/composites
    # OUT: cwd/output/binary
    splice_suit(workingdir, "power")
    splice_suit(workingdir, "powerboots")
    splice_suit(workingdir, "varia")
    splice_suit(workingdir, "variaboots")
    # IN:  cwd/output/binary
    combine_suits(workingdir)

def compositeToBinSheet(workingdir):
    '''
    Take single composite sheet
    Make set of composite sheets
    Send to compositesToBinSheet()
    '''
    composite = Image.open(
        os.path.join(
            workingdir,
            "output",
            "composites",
            "suits.png"
        )
    )
    composite_size = composite.size
    if composite_size != (256, 136):
        print(f"suits.png invalid size; is {composite_size}; should be (256, 136)")
        return
    for [i, suit_type] in enumerate(["power", "powerboots", "varia", "variaboots"]):
        img = composite.crop(coord_calc((64 * i, 0), (64, 136)))
        img.save(os.path.join(workingdir, "input", "composites", f"{suit_type}.png"))

    compositesToBinSheet(workingdir)

def doTheThing(
    mode=None,
    workingdir=os.path.join("."),
    binfilename=None
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
    workingdir = os.path.join(baseoutput,workingdir) \
        if workingdir is not None \
        else baseoutput
    setupDirs(
        workingdir
    )
    mandatory()

    # requires binary sheet
    # cwd/input/binary
    binSheetToCells(
        mode,
        workingdir,
        binfilename
    )

    # requires 4 composites
    # cwd/input/composites
    # power.png
    # powerboots.png
    # varia.png
    # variaboots.png
    compositesToBinSheet(workingdir)

    # export suit
    # requires binSheetToCells()
    export_suit(workingdir, "power")
    export_suit(workingdir, "powerboots")
    export_suit(workingdir, "varia")
    export_suit(workingdir, "variaboots")

    # export suits
    # requires binSheetToCells()
    export_suits(workingdir)
    export_preview(workingdir)

    # requires 1 composite
    # cwd/input/composites
    # suits.png
    compositeToBinSheet(workingdir)

doTheThing(
    "save",
    "samus",
    "combined"
)
