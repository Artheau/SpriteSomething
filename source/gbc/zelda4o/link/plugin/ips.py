import os   # manage filesystem operations

from base64 import b64encode    # for YAML file
from binascii import crc32      # for vanilla check

from PIL import Image    # get Pillow to open the image

importedCRCs = {}   # calculate imported CRCs for comparison

# these are the vanilla CRCs for the sprite data
vanillaCRCs = {
    "baby": int(0xEDA1184A),
    "link": int(0xCA195F8A)
}

# this is the wrapper for IPS files
ipsParts = {
    "header": bytes(ord(x) for x in "PATCH"),
    "footer": bytes(ord(x) for x in "EOF")
}

# vanilla palette for Link sprites
vanillaPalette = [
    (0xFF, 0xFF, 0xFF, 0xFF),
    (0x00, 0x00, 0x00, 0xFF),
    (0x10, 0xAD, 0x42, 0xFF),
    (0xFF, 0xD6, 0x8C, 0xFF)
]

# port of appendBlock function
def appendBlock(img, byteArr, x, y):
    for j in range(0, 8):
        row = []
        for i in range(0, 8):
            pixel = img.getpixel((x + i, y + j))
            if pixel in vanillaPalette:
                row.append(vanillaPalette.index(pixel))
            elif pixel == (0,0,0,0):
                row.append(0)
            else:
                row.append(pixel)
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
    ret = ret.decode()
    return ret

# do the thing
def doTheThing(filename, verbose=False):
    # gather all the things!
    megadata = {
        "modified": False,
        "sprites":{
            "baby": {
                "patch": [],
                "range": {
                    "y":    range(272, 288,  16),
                    "x":    range( 64, 128,   8),
                    "y2":   range(  0,  16,   8)
                },
                "modified": False
            },
            "link": {
                "patch": [],
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

    spriteIDs = list(megadata["sprites"].keys())    # get sprite names
    gameIDs = list(megadata["games"].keys())        # get game names

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
    imgpath = os.path.join(
        "resources",
        "app",
        "gbc",
        "zelda4o",
        "link",
        "sheets",
        filename
    )
    if os.path.isfile(imgpath):
        print(f"Opening: {filename}")
    else:
        print(f"{filename} not found!")
        return

    imgfile = Image.open(imgpath)
    imgfile = imgfile.convert("RGBA")

    # get a slug for naming stuff
    basename = os.path.splitext(os.path.basename(filename))[0]

    # get pixel data
    # build patch files
    for sprite in spriteIDs:
        print(f"Examining {sprite.capitalize()} Data")
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

    # check to see if it's modded data
    for sprite in spriteIDs:
        importedCRCs[sprite] = crc32(bytes(megadata["sprites"][sprite]["patch"]))
        megadata["sprites"][sprite]["modified"] = importedCRCs[sprite] != vanillaCRCs[sprite]
        # if it's been modded, print a message
        if megadata["sprites"][sprite]["modified"]:
            print(f"Modded {sprite.capitalize()}")
            megadata["modified"] = True
        # output binary data if verbose for good measure
        if megadata["sprites"][sprite]["modified"] or verbose:
            with open(
                os.path.join(
                    outputDir,
                    f"{basename}_{sprite}.bin"
                ),
                "wb"
            ) as spriteBin:
                spriteBin.write(bytes(megadata["sprites"][sprite]["patch"]))

    # if we got this far, let's build some stuff
    if megadata["modified"]:
        print({"vanilla":vanillaCRCs,"imported":importedCRCs})

    # if modified, build game patches
    spriteHeaders = {
        "link": [0x06, 0x80, 0x00, 0x22, 0xE0],
        "baby": [0x06, 0xAC, 0xA0, 0x01, 0x00]
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
    # if modified, write patches
    for gameID in gameIDs:
        megadata["games"][gameID]["patch"] = [
            *megadata["games"][gameID]["patch"],
            *ipsParts["footer"]
        ]
        if megadata["sprites"][sprite]["modified"]:
            with open(
                os.path.join(
                    outputDir,
                    f"{basename}_{gameID}.ips"
                ),
                "wb"
            ) as ipsFile:
                ipsFile.write(bytes(megadata["games"][gameID]["patch"]))

    # if it's been modded, build YAML patch file
    if megadata["modified"]:
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
                    print(f" Adding {sprite.capitalize()}")
                    spriteHandle = sprite
                    if spriteHandle == "baby":
                        spriteHandle = "link_baby"
                    yamlFile.write(f"  spr_{spriteHandle}:" + "\n")
                    yamlFile.write("    0x0: " + encode(megadata["sprites"][sprite]["patch"]) + "\n")
    print()

if __name__ == "__main__":
    for filename in [
        "linkwhite.png"
    ]:
        doTheThing(filename)
        pass
    pass
