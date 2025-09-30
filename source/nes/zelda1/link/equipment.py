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
                "nes",
                "zelda1",
                "link",
                "sheets"
            ],
            "equipment.png"
        )
    )

    equipment = {}

    #collect icon names & coordinates
    icon_specs = {}

    inventory = {
        "pop_small":    (( 0, 0),(16,16)),
        "pop_big":      ((16, 0),(16,16)),
        "tfp_gold":     (( 0,16),(16,16)),
        "tfp_blue":     ((16,16),(16,16))
    }
    #add more inventory stuff
    for key in inventory:
        origin,dims = inventory[key]
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
                    "nes",
                    "zelda1",
                    "link",
                    "sheets",
                    icon + ".png"
                )
            )

    return equipment
