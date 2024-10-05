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
                "gbc",
                "zelda4o",
                "link",
                "sheets"
            ],
            "equipment.png"
        )
    )
    equipment_image = equipment_image.convert('RGBA')

    equipment = {}

    #collect icon names & coordinates
    icon_specs = {}

    #the weapons are at the same x-coordinate but have differing y-values, set up these y-values
    weapons = [
        ("wooden",      24 * 0),
        ("noble",       24 * 1),
        ("master",      24 * 2),
        ("charge",      24 * 3),
        ("rod",         24 * 4),
        ("cane",        24 * 5),
        ("seed",        24 * 6),
        ("biggoron",    24 * 7),
        ("ore",         24 * 8)
    ]

    #tuples for fun stuff; first is top-left origin, second is width,height
    coords = [
        ((  0,0),( 8,24)),
        ((  8,0),(16,24)),
        (( 24,0),(24,16))
    ]
    #cycle through coordinate info
    for i,_ in enumerate(coords):
        #cycle through swords and y-offsets
        for j,_ in enumerate(weapons):
            origin,dims = coords[i]
            x,y = origin
            level,y_offset = weapons[j]
            weapon_key = level + "_weapon" + str(i)
            icon_specs[weapon_key] = coord_calc(
                (
                    x,
                    y+y_offset
                ),
                dims
            )

    #the shields are at the same x-coordinate but have differing y-values, set up these y-values
    shields = [
        ("wooden",  214 + (12 * 0)),
        ("iron",    214 + (12 * 1)),
        ("mirror",  214 + (12 * 2)),
    ]

    #tuples for fun stuff; first is top-left origin, second is width,height
    coords = [
        ((  0,0),(12,12)),
        (( 12,0),(12,12)),
        (( 24,0),(12,12))
    ]
    #cycle through coordinate info
    for i,_ in enumerate(coords):
        #cycle through swords and y-offsets
        for j,_ in enumerate(shields):
            origin,dims = coords[i]
            x,y = origin
            level,y_offset = shields[j]
            shield_key = level + "_shield" + str(i)
            icon_specs[shield_key] = coord_calc(
                (
                    x,
                    y+y_offset
                ),
                dims
            )


    #next row is some inventory stuff
    inventory = {
        "blue_magnet0": (( 0,12 * 21),(16, 8)),
        "blue_magnet1": ((16,12 * 21),(16, 8)),
        "tall_grass":   ((32,12 * 21),(16,8)),
        "red_magnet0":  (( 0,(12 * 21) + (8 * 1)),(16, 8)),
        "red_magnet1":  ((16,(12 * 21) + (8 * 1)),(16, 8)),
        "blue_magnet2": (( 0,(12 * 21) + (8 * 2)),( 8,16)),
        "blue_magnet3": (( 8,(12 * 21) + (8 * 2)),( 8,16)),
        "red_magnet2":  ((16,(12 * 21) + (8 * 2)),( 8,16)),
        "red_magnet3":  ((24,(12 * 21) + (8 * 2)),( 8,16)),
        "minecart0":    (( 0,(12 * 21) + (8 * 4)),(16,16)),
        "minecart1":    ((16,(12 * 21) + (8 * 4)),(16,16)),
        "minecart2":    ((32,(12 * 21) + (8 * 4)),(16,16)),
        "blue_sling0":  (( 0,(12 * 21) + (8 * 6)),( 8,16)),
        "blue_sling1":  (( 8,(12 * 21) + (8 * 6)),( 8,16)),
        "blue_sling2":  ((16,(12 * 21) + (8 * 6)),(16,16)),
        "red_sling0":   (( 0,(12 * 21) + (8 * 8)),( 8,16)),
        "red_sling1":   (( 8,(12 * 21) + (8 * 8)),( 8,16)),
        "red_sling2":   ((16,(12 * 21) + (8 * 8)),(16,16)),
    }
    #add some inventory stuff
    for key in inventory:
        origin,dims = inventory[key]
        icon_specs[key] = coord_calc(origin,dims)

    icon_specs["normal_boomerang"] = coord_calc((31,300),(8,16))
    icon_specs["magical_boomerang"] = coord_calc((39,300),(8,16))

    # essences
    essence_start = (0,((16 * 20) + 4 + (8 * 1)))
    i = 0
    for row in range(6):
        for col in range(3):
            origin = (
                essence_start[0] + (col * 16),
                essence_start[1] + (row * 16)
            )
            icon_specs["essence" + str(i)] = coord_calc(origin,(16,16))
            i += 1

    # essence acquire
    essence_props = {
        "essence_bgorange": ((0,((16 * 26) + 4 + (8 * 1))),(32,32)),
        "essence_bgblue":   ((0,((16 * 28) + 4 + (8 * 1))),(32,32)),
    }
    for key in essence_props:
        origin,dims = essence_props[key]
        icon_specs[key] = coord_calc(origin,dims)

    # Ages: Time Travel stuff
    # portals
    portal_props = {
        "portal0": (( 0,((16 * 30) + 4 + (8 * 1))),(16,16)),
        "portal1": ((16,((16 * 30) + 4 + (8 * 1))),(16,16)),
        "portal2": (( 0,((16 * 31) + 4 + (8 * 1))),(32,16)),
        "portal3": (( 0,((16 * 32) + 4 + (8 * 1))),(32,16)),
        "portal4": (( 0,((16 * 33) + 4 + (8 * 1))),(32,16)),
        "portal5": (( 0,((16 * 34) + 4 + (8 * 1))),(32,16))
    }
    for key in portal_props:
        origin,dims = portal_props[key]
        icon_specs[key] = coord_calc(origin,dims)

    # halos
    halo_props = [
        ((0,((16 * 30) + 4 + (8 * 1))),( 4,2)),
        ((0,((16 * 30) + 4 + 3 + (8 * 1))),( 8,2)),
        ((9,((16 * 30) + 4 + 3 + (8 * 1))),( 8,2)),
        ((5,((16 * 30) + 4 + (8 * 1))),(12,2)),
        ((0,((16 * 30) + 4 + 6 + (8 * 1))),(15,8))
    ]
    for color in ["pink","blue"]:
        for [i, halo] in enumerate(halo_props):
            origin,dims = halo
            key = f"{color}_halo{i}"
            if color == "blue":
                new_origin = list(origin)
                new_origin[0] += 18
                origin = tuple(new_origin)
            icon_specs[key] = coord_calc(origin,dims)

    # auras
    aura_props = [
        (( 0,((16 * 36) + 4 + (8 * 1))),( 8,16)),
        (( 8,((16 * 36) + 4 + (8 * 1))),( 8,16)),
        ((16,((16 * 36) + 4 + (8 * 1))),( 8,16)),
        ((24,((16 * 36) + 4 + (8 * 1))),( 8,16)),
        ((32,((16 * 36) + 4 + (8 * 1))),( 8,16)),
        (( 0,((16 * 37) + 4 + (8 * 1))),(16,16)),
        ((16,((16 * 37) + 4 + (8 * 1))),(16,16)),
        (( 0,((16 * 38) + 4 + (8 * 1))),(16,16)),
        ((16,((16 * 38) + 4 + (8 * 1))),(16,16))
    ]
    for [i, coords] in enumerate(aura_props):
        key = "aura" + str(i)
        origin,dims = coords
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
                    "gbc",
                    "zelda4o",
                    "link",
                    "sheets",
                    icon + ".png"
                )
            )

    return equipment
