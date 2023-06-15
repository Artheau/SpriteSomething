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

def equipment_test(save=False):
    '''
    Run equipment-splitter
    '''
    #get equipment image
    equipment_image = Image.open(
        common.get_resource(
            [
                "snes",
                "ffmq",
                "benjamin",
                "sheets"
            ],
            "equipment.png"
        )
    )

    equipment = {}

    #collect icon names & coordinates
    icon_specs = {}

    inventory = {
        "sword0": (( 0,0),( 8,16)),
        "sword1": (( 9,8),(16, 8)),
    }
    #add inventory stuff
    for key in inventory:
        origin,dims = inventory[key]
        icon_specs[key] = coord_calc(origin,dims)

    for [i, key] in enumerate(["axe", "claw"]):
        for j in range(5):
            origin = ((17*j), (17 * (i+1)))
            dims = (16,16)
            icon_specs[key + str(j)] = coord_calc(origin,dims)
            # print(key + str(j), icon_specs[key + str(j)])

    for [i, key] in enumerate(["bomb", "jumbo", "mega"]):
        origin = ((36*i), 51)
        dims = (16, 23)
        icon_specs[key + str(0)] = coord_calc(origin,dims)
        # print(key + str(0), icon_specs[key + str(0)])

        origin = (((36*i) + 17), 51)
        dims = (18, 23)
        icon_specs[key + str(1)] = coord_calc(origin,dims)
        # print(key + str(1), icon_specs[key + str(1)])

    splodey = {
        "explode0": (( 0,76),(16,16)),
        "explode1": ((16,76),(16,16)),
        "explode2": ((34,76),(16,16)),
        "explode3": ((51,75),(18,17)),
        "explode4": ((89,76),(16,16)),
    }
    #add splodey stuff
    for key in splodey:
        origin,dims = splodey[key]
        icon_specs[key] = coord_calc(origin,dims)

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
                    "ffmq",
                    "benjamin",
                    "sheets",
                    icon + ".png"
                )
            )

    return equipment
