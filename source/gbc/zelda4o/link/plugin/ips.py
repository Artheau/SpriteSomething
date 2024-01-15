import os   # manage filesystem operations

from hashlib import md5 # get standin encoding function

import numpy as np  # get numpy to zero-fill arrays

from PIL import Image    # get Pillow to open the image

# these are the vanilla locations in the game file
vanillaAddrs = {
    "link": 0xCA195F8A,
    "baby": 0xEDA1184A
}

ipsHeader = [0x50,0x41,0x54,0x43,0x48]
ipsFooter = [0x45, 0x4F, 0x46]

# these are the recepticles or the patch data
patches = {
    "link": np.zeros((1,0x22E0), dtype=int)[0],
    "baby": np.zeros((1,0x0100), dtype=int)[0],
    "ages": [*ipsHeader],
    "seasons": [*ipsHeader]
}

# port of appendBlock function
def appendBlock(img, byteArr, x, y):
    row = np.zeros((1, 8), dtype=int)[0]
    for j in range(0, 8):
        for i in range(0, 8):
            row[i] = x + i + y + j
        rowLow = 0
        rowHigh = 0
        for i in range(0, 8):
            rowLow = (row[i] & 1) << (7 - i)
            rowHigh = ((row[i] & 2) >> 1) << (7 - i)
            byteArr = [*byteArr, rowLow, rowHigh]
    return byteArr

# port of encode function
def encode(byteArr):
    return str(
        md5(
            str(
                byteArr
            ).encode("utf-8")
        ).hexdigest()
    )

def doTheThing(filename):
    # make output dir
    outputDir = os.path.join(
        "resources",
        "user",
        "gbc",
        "zelda4o",
        "link",
        "sheets"
    )

    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    # get input image
    img = Image.open(
        os.path.join(
            "resources",
            "app",
            "gbc",
            "zelda4o",
            "link",
            "sheets",
            filename
        )
    )
    print(f"Opening: {filename}")

    basename = os.path.splitext(os.path.basename(filename))[0]

    # build Link patch
    print("Building Link")
    for y in range(0, 288, 16):
        for x in range(0, 128, 8):
            for y2 in range(0, 16, 8):
                if y == 272 and x >= 56:
                    continue
                patches["link"] = appendBlock(
                    img,
                    patches["link"],
                    x,
                    y + y2
                )

    # check to see if it's different from the vanilla data
    modifiedLink = patches["link"] != vanillaAddrs["link"]

    # if it's different from vanilla, dump the binary for Link
    if modifiedLink:
        print("Link has been modded")
        with open(
            os.path.join(
                outputDir,
                f"{basename}_link.bin"
            ),
            "wb"
        ) as linkBin:
            linkBin.write(bytes(patches["link"]))

    # build Baby patch
    print("Building Baby")
    for y in range(272, 288, 16):
        for x in range(64, 128, 8):
            for y2 in range(0, 16, 8):
                patches["baby"] = appendBlock(
                    img,
                    patches["baby"],
                    x,
                    y + y2
                )

    # check to see if it's different from vanilla data
    modifiedBaby = patches["baby"] != vanillaAddrs["baby"]

    # if it's different from vanilla, dump the binary for Baby
    if modifiedBaby:
        print("Baby has been modded")
        with open(
            os.path.join(
                outputDir,
                f"{basename}_baby.bin"
            ),
            "wb"
        ) as babyBin:
            babyBin.write(bytes(patches["baby"]))

    # if we didn't change anything, bounce
    if not (modifiedLink and modifiedBaby):
        exit()

    # if we got this far, let's build some stuff

    # build game patches
    if modifiedLink:
        print("Building Link IPS")
        linkHeader = [0x06, 0x80, 0x00, 0x22, 0xE0]
        for gameID in ["ages", "seasons"]:
            patches[gameID] = [*patches[gameID], *linkHeader]
            patches[gameID] = [*patches[gameID], *patches["link"]]

    if modifiedBaby:
        print("Building Baby IPS")
        babyHeader = [0x06, 0xAC, 0xA0, 0x22, 0xE0]
        for gameID in ["ages", "seasons"]:
            if gameID == "seasons":
                babyHeader[2] = 0x40
            patches[gameID] = [*patches[gameID], *babyHeader]
            patches[gameID] = [*patches[gameID], *patches["baby"]]

    # put footer on patches
    for gameID in ["ages", "seasons"]:
        patches[gameID] = [*patches[gameID], *ipsFooter]
        with open(
            os.path.join(
                outputDir,
                f"{basename}_{gameID}.ips"
            ),
            "wb"
        ) as ipsFile:
            ipsFile.write(bytes(patches[gameID]))

    # build YAML patch file
    with open(
        os.path.join(
            outputDir,
            f"{basename}.yaml"
        ),
        "w"
    ) as yamlFile:
        print("Building YAML Patch File")
        yamlFile.write("common:" + "\n")
        if modifiedLink:
            yamlFile.write("  spr_link:" + "\n")
            yamlFile.write("    0x0: " + encode(patches["link"]) + "\n")
        if modifiedBaby:
            yamlFile.write("  spr_baby:" + "\n")
            yamlFile.write("    0x0: " + encode(patches["baby"]) + "\n")

if __name__ == "__main__":
    # doTheThing("linkwhite.png")
    pass
