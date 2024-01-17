import os   # manage filesystem operations

from base64 import b64encode
from binascii import crc32
from hashlib import md5 # get standin encoding function

import numpy as np  # get numpy to zero-fill arrays

from PIL import Image    # get Pillow to open the image

importedCRCs = {}   # calculate imported CRCs for comparison

# these are the vanilla locations in the game file
vanillaCRCs = {
    "link": int(0xCA195F8A),
    "baby": int(0xEDA1184A)
}

modifiedSprite = {}

ipsParts = {}
# header & footer for an IPS patch
for [section, byteStr] in {
    "header": "PATCH",
    "footer": "EOF"
}.items():
    byteStr = byteStr.encode("utf-8").hex()
    byteStr = list(
        zip(
            byteStr[0::2],
            byteStr[1::2]
        )
    )
    ipsParts[section] = [int(''.join(x), 16) for x in byteStr]

megadata = {
    "sprites":{
        "baby": {
            "patch": np.zeros((1, 0x0100), dtype=int)[0],
            "range": {
                "y":    range(272, 288,  16),
                "x":    range( 64, 128,   8),
                "y2":   range(  0,  16,   8)
            },
            "modified": False
        },
        "link": {
            "patch": np.zeros((1, 0x22E0), dtype=int)[0],
            "range": {
                "y":    range(  0, 288, 16),
                "x":    range(  0, 128,  8),
                "y2":   range(  0,  16,  8)
            },
            "modified": False
        }
    },
    "games": {
        "ages": {
            "patch": [*ipsParts["header"]]
        },
        "seasons": {
            "patch": [*ipsParts["header"]]
        }
    }
}

spriteIDs = list(megadata["sprites"].keys())
gameIDs = list(megadata["games"].keys())

# port of appendBlock function
def appendBlock(img, byteArr, x, y):
    row = np.zeros((1, 8), dtype=int)[0]
    for j in range(0, 8):
        for i in range(0, 8):
            pixel = img.getpixel((x + i, y + j))
            row[i] = pixel
        rowLow = 0
        rowHigh = 0
        for i in range(0, 8):
            rowLow |= (row[i] & 1) << (7 - i)
            rowHigh |= ((row[i] & 2) >> 1) << (7 - i)
            byteArr = [*byteArr, rowLow, rowHigh]
    return byteArr

# port of encode function
def encode(byteArr):
    ret = byteArr
    ret = bytes(ret)
    ret = b64encode(ret)
    ret = str(ret)
    return ret

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
    imgfile = Image.open(
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

    # build patches
    for sprite in spriteIDs:
        print(f"Extracting {sprite.capitalize()} Data")
        for y in megadata["sprites"][sprite]["range"]["y"]:
            for x in megadata["sprites"][sprite]["range"]["x"]:
                for y2 in megadata["sprites"][sprite]["range"]["y2"]:
                    if sprite == "link":
                        if y == 272 and x >= 56:
                            continue
                    megadata["sprites"][sprite]["patch"] = appendBlock(
                        imgfile,
                        megadata["sprites"][sprite]["patch"],
                        x,
                        y + y2
                    )

    for sprite in spriteIDs:
        importedCRCs[sprite] = crc32(bytes(megadata["sprites"][sprite]["patch"]))
        megadata["sprites"][sprite]["modified"] = importedCRCs[sprite] != vanillaCRCs[sprite]
        if megadata["sprites"][sprite]["modified"]:
            print(f"{sprite.capitalize()} has been modded")
            with open(
                os.path.join(
                    outputDir,
                    f"{basename}_{sprite}.bin"
                ),
                "wb"
            ) as spriteBin:
                spriteBin.write(bytes(megadata["sprites"][sprite]["patch"]))

    # if we got this far, let's build some stuff
    print({"vanilla":vanillaCRCs,"imported":importedCRCs})

    # build game patches
    spriteHeaders = {
        "link": [0x06, 0x80, 0x00, 0x22, 0xE0],
        "baby": [0x06, 0xAC, 0xA0, 0x22, 0xE0]
    }
    for sprite in spriteIDs:
        if megadata["sprites"][sprite]["modified"]:
            print(f"Building {sprite.capitalize()} IPS")
            for gameID in gameIDs:
                if sprite == "baby":
                    spriteHeaders["baby"][2] = 0xA0 if gameID == "ages" else 0x40
                megadata["games"][gameID]["patch"] = [
                    *megadata["games"][gameID]["patch"],
                    *spriteHeaders[sprite]
                ]
                megadata["games"][gameID]["patch"] = [
                    *megadata["games"][gameID]["patch"],
                    *megadata["sprites"][sprite]["patch"]
                ]

    # put footer on patches
    for gameID in gameIDs:
        megadata["sprites"][sprite]["patch"] = [
            *megadata["sprites"][sprite]["patch"],
            *ipsParts["footer"]
        ]
        with open(
            os.path.join(
                outputDir,
                f"{basename}_{gameID}.ips"
            ),
            "wb"
        ) as ipsFile:
            ipsFile.write(bytes(megadata["games"][gameID]["patch"]))

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
        for sprite in spriteIDs:
            if megadata["sprites"][sprite]["modified"]:
                spriteHandle = sprite
                if spriteHandle == "baby":
                    spriteHandle = "link_baby"
                yamlFile.write(f"  spr_{spriteHandle}:" + "\n")
                yamlFile.write("    0x0: " + encode(megadata["sprites"][sprite]["patch"]) + "\n")

if __name__ == "__main__":
    # doTheThing("linkwhite.png")
    pass
