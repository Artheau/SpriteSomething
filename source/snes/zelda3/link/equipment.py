#pylint: disable=invalid-name
'''
Load Equipment Props
'''
import os
from PIL import Image
from source.meta.common import common

def coord_calc(origin,dims):
    '''
    Calculate coordinates given origin point and dimensions
    '''
    x1, x2 = origin
    w, h = dims
    return (x1,x2,w+x1,h+x2)

def get_doi_equipement(save=False):
    '''
    Run equipment splitter
    '''
    icon_specs = {}
    for filename in ["doi-swords.png","doi-shields.png"]:
        #get equipment image
        with Image.open(
            common.get_resource(
                [
                    "snes",
                    "zelda3",
                    "link",
                    "sheets"
                ],
                filename
            )
        ) as equipment_image:
            if "swords" in filename:
                #the swords are at the same x-coordinate but have differing y-values, set up these y-values
                swords = [
                    ("basic",   32*0),
                    ("iron",    32*1),
                    ("long",    32*2),
                    ("dragon",  32*3),
                    ("blood",   32*4),
                    ("master2", 32*5),
                ]

                #tuples for fun stuff; first is top-left origin, second is width,height
                coords = [
                    ((  0,0),( 8,16)),
                    ((  8,0),( 8,16)),
                    (( 16,0),(16,16)),
                    (( 32,0),(16,16)),
                    (( 48,0),(19, 8)),
                    (( 48,8),(16, 8)),
                    (( 64,8),(16, 8)),
                    (( 80,0),(16,16)),
                    (( 96,0),(16,16)),
                    ((112,6),(16,18)),
                    ((128,3),( 8,21)),
                    ((136,0),( 8,16)),
                    ((144,0),(16,16)),
                    ((160,0),(16, 8))
                ]
                #cycle through coordinate info
                for i,_ in enumerate(coords):
                    #cycle through swords and y-offsets
                    for j,_ in enumerate(swords):
                        origin,dims = coords[i]
                        x,y = origin
                        level,y_offset = swords[j]
                        icon_specs[level + "_sword" + str(i)] = [
                            filename,
                            coord_calc(
                                (
                                    x,
                                    y+y_offset
                                ),
                                dims
                            )
                        ]

            if "shields" in filename:
                #shields
                shields = [
                    ("wooden",      16*0),
                    ("triforce",    16*1),
                    ("mirror2",     16*2),
                    ("golden",      16*3),
                ]
                #cycle through x-coordinates
                for i in range(4):
                    #cycle through shields and y-offsets
                    for j,_ in enumerate(shields):
                        level,y_offset = shields[j]
                        origin = (i*16,0+y_offset)
                        icon_specs[level + "_shield" + str(i)] = [
                            filename,
                            coord_calc(origin,(16,16))
                        ]
    return icon_specs

def equipment_test(save=False):
    '''
    Run equipment-splitter
    '''
    #get equipment image
    equipment_image = Image.open(
        common.get_resource(
            [
                "snes",
                "zelda3",
                "link",
                "sheets"
            ],
            "equipment.png"
        )
    )

    equipment = {}

    #collect icon names & coordinates
    icon_specs = {}

    #the swords are at the same x-coordinate but have differing y-values, set up these y-values
    swords = [
        ("fighter", 32*0),
        ("master",  32*1),
        ("tempered",32*2),
        ("gold",    32*3)
    ]

    #tuples for fun stuff; first is top-left origin, second is width,height
    coords = [
        ((  0,0),( 8,16)),
        ((  8,0),( 8,16)),
        (( 16,0),(16,16)),
        (( 32,0),(16,16)),
        (( 48,0),(19, 8)),
        (( 48,8),(16, 8)),
        (( 64,8),(16, 8)),
        (( 80,0),(16,16)),
        (( 96,0),(16,16)),
        ((112,6),(16,18)),
        ((128,3),( 8,21)),
        ((136,0),( 8,16)),
        ((144,0),(16,16)),
        ((160,0),(16, 8))
    ]
    #cycle through coordinate info
    for i,_ in enumerate(coords):
        #cycle through swords and y-offsets
        for j,_ in enumerate(swords):
            origin,dims = coords[i]
            x,y = origin
            level,y_offset = swords[j]
            icon_specs[level + "_sword" + str(i)] = coord_calc(
                (
                    x,
                    y+y_offset
                ),
                dims
            )

    #next row is some inventory stuff
    inventory = {
        "main_shadow":  (( 0,112),(16,16)),
        "small_shadow": ((16,112),(16,16)),
        "book":         ((32,112),(16,16)),
        "bush":         ((48,112),(16,16)),
        "pendant":      ((64,112),(16,16)),
        "crystal":      ((80,112),(16,16))
    }
    #add some inventory stuff
    for key in inventory:
        origin,dims = inventory[key]
        icon_specs[key] = coord_calc(origin,dims)

    #shields
    shields = [
        ("fighter",     0),
        ("fire",        16),
        ("mirror",    32)
    ]
    #cycle through x-coordinates
    for i in range(4):
        #cycle through shields and y-offsets
        for j,_ in enumerate(shields):
            level,y_offset = shields[j]
            origin = (i*16,128+y_offset)
            icon_specs[level + "_shield" + str(i)] = coord_calc(origin,(16,16))

    inventory = {
        "cane0": (( 0,176),( 8,16)), #vertical
        "cane1": (( 8,176),( 8,16)), #vertical
        "cane2": ((16,176),(16, 8)), #horizontal
        "cane3": ((32,176),(16,16)), #diagonal ltr
        "cane4": ((48,176),( 8,16)), #vertical
        "somaria_block": ((64,176),(16,16)),
        "rod0": (( 0,192),( 8,16)), #vertical
        "rod1": (( 8,192),( 8,16)), #vertical
        "rod2": ((16,192),(16, 8)), #horizontal
        "rod3": ((16,200),( 8, 8)), #fourth-wall NtS
        "rod4": ((32,192),(16,16)), #diagonal ltr
        "rod5": ((48,192),( 8,16)), #vertical
        "hammer0": (( 0,208),( 8,16)), #vertical ltr
        "hammer1": (( 8,208),( 8,16)), #vertical
        "hammer2": ((16,208),( 8,16)), #vertical
        "hammer3": ((24,208),( 8,16)), #vertical
        "hammer4": ((32,208),(16, 8)), #horizontal
        "hammer5": ((32,216),( 8, 8)), #vertical
        "hammer6": ((48,208),(16,16)), #diagonal ltr
        "hook0": (( 0,224),( 8, 8)), #horizontal
        "hook1": (( 8,224),( 8, 8)), #vertical
        "hook2": (( 0,232),(16, 8)), #vertical
        "hook3": ((16,232),( 8, 8)), #chainlink
        "hook4": ((24,224),( 8,16)), #horizontal
        "boomerang": ((32,224),(16,16)), #NE
        "bow0": (( 0,256),( 8,16)),
        "bow1": ((16,256),(16, 8)),
        "bow2": ((32,256),(16,16)),
        "shovel0": (( 0,272),( 8, 8)), #down
        "shovel1": ((16,272),( 8, 8)), #up
        "swagduck0": ((32,272),(16,16)),
        "swagduck1": ((48,272),(16,16)), #flap
        "bed0": (( 0,288),(32,32)),
        "bed1": ((32,288),(32,32)),
        "tall_grass0": (( 0,320),(16, 8)),
        "tall_grass1": (( 0,328),(16, 8)),
        "tall_grass2": ((16,320),(16, 8)),
        "shallow_water0": ((32,320),(16, 8)),
        "shallow_water1": ((32,328),(16, 8)),
        "shallow_water2": ((48,320),(16, 8)),
        "master_sword": (( 0,336),(16,32))
    }
    #add more inventory stuff
    for key in inventory:
        origin,dims = inventory[key]
        icon_specs[key] = coord_calc(origin,dims)

    #add bugnet
    for i in range(7):
        icon_specs["bugnet" + str(i)] = coord_calc((i*16,240),(16,16))

    #cycle through collected icons and write to disk
    for [icon, icon_coords] in icon_specs.items():
        cropped_image = equipment_image.crop(icon_coords)
        equipment[icon] = cropped_image
        if save:
            cropped_image.save(
                os.path.join(
                    ".",
                    "resources",
                    "user",
                    "snes",
                    "zelda3",
                    "link",
                    "sheets",
                    icon + ".png"
                )
            )

    icon_specs = get_doi_equipement(save)
    for [icon, iconData] in icon_specs.items():
        filename = iconData[0]
        icon_coords = iconData[1]
        cropped_image = Image.open(os.path.join(
            ".",
            "resources",
            "app",
            "snes",
            "zelda3",
            "link",
            "sheets",
            filename
        )).crop(icon_coords)
        equipment[icon] = cropped_image
        if save:
            cropped_image.save(
                os.path.join(
                    ".",
                    "resources",
                    "user",
                    "snes",
                    "zelda3",
                    "link",
                    "sheets",
                    icon + ".png"
                )
            )

    return equipment
