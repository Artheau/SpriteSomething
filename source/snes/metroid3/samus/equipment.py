# pylint: disable=invalid-name
import os
from PIL import Image
from source.meta.common import common

def coord_calc(origin,dims):
    x1, x2 = origin
    w, h = dims
    return (x1,x2,w+x1,h+x2)

def equipment_test(save=False):
    #get equipment image
    with(
        Image.open(
            common.get_resource(
                [
                    "snes",
                    "metroid3",
                    "samus",
                    "sheets"
                ],
                "equipment.png"
            )
        )
    ) as equipment_image:
        equipment_image = equipment_image.convert("RGBA")
        equipment = {}

        #collect icon names & coordinates
        icon_specs = {}

        #lemons, missiles, supers
        projectiles = {
            "lemon_right":      [(  0, 0),(16,16)], #left: h-flip
            "lemon_upright":    [( 16, 0),(16,16)], #downright: v-flip; upleft: h-flip; downleft: both
            "lemon_up":         [( 32, 0),(16,16)], #down: v-flip
            "missile_right":    [( 48, 0),(16,16)], #left: h-flip
            "missile_upright":  [( 64, 0),(16,16)], #downright: v-flip, upleft: h-flip; downleft: both
            "missile_up":       [( 80, 0),(16,16)], #down: v-flip
            "super_right":      [( 96, 0),(16,16)], #left: h-flip
            "super_upright":    [(112, 0),(16,16)], #downright: v-flip; upleft: h-flip; downleft: both
            "super_up":         [(128, 0),(16,16)] #down: v-flip
        }
        for k,v in projectiles.items():
            icon_specs[k] = coord_calc(v[0],v[1])

        #morph ball bombs
        for i in range(3):
            icon_specs["mbb" + str(i)] = coord_calc((144+(8*i),0),(8,8))

        #powerbombs
        for i in range(3):
            icon_specs["pb" + str(i)] = coord_calc((144+(8*i),8),(8,8))

        #poof cloud
        for i in range(3):
            icon_specs["poof" + str(i)] = coord_calc((144+(8*i),16),(8,8))

        #morph ball bombs blast
        for i in range(3):
            for j in range(2):
                w = 32
                h = 32
                x1 = 176 + (w * j)
                x2 = 0 + (h * i)
                itemID = (i*2)+(j*1)
                if itemID < 5:
                    icon_specs["mbb_blast" + str(itemID)] = coord_calc(
                        (x1, x2),
                        (w, h)
                    )

        #charg[ing|ed] lemon
        for i in range(6):
            w = 16
            h = 16
            x1 = 0 + (w * i)
            x2 = 16
            icon_specs["charge" + str(i)] = coord_calc((x1,x2),(w,h))

        #iced lemon
        for i in range(3):
            w = 16
            h = 16
            x1 = 64 + (w * i)
            x2 = 48
            icon_specs["ice" + str(i)] = coord_calc((x1,x2),(w,h))

        #iced particles
        for i in range(4):
            w = 16
            h = 16
            x1 = 80 + (w * i)
            x2 = 32
            icon_specs["ice_particle" + str(i)] = coord_calc((x1,x2),(w,h))

        #charged ice
        for i in range(2):
            w = 16
            h = 16
            x1 = 112 + (w * i)
            x2 = 48
            icon_specs["charge_ice" + str(i)] = coord_calc((x1,x2),(w,h))

        #spazer
        icon_specs["spazer0"] = coord_calc((112,16),( 9,2)) #from blaster
        icon_specs["spazer1"] = coord_calc((112,19),(18,2)) #repeated; # FIXME: Get number of repeats

        #plasma
        icon_specs["plasma0"] = coord_calc((128,16),(5,3)) #from blaster
        icon_specs["plasma1"] = coord_calc((134,16),(4,3)) #repeated; # FIXME: Get number of repeats

        #charged spazer
        icon_specs["charge_spazer0"] = coord_calc((112,22),(5,2)) #from blaster

        #charged plasma

        #charged spazer/plasma (none/ice/wave)
        icon_specs["charge_special0"] = coord_calc((128,22),(8,7)) #repeated; # FIXME: Get number of repeats

        #wave lemon
        for i in range(5):
            w = 16
            h = 16
            x1 = 0 + (w * i)
            x2 = 32
            icon_specs["wave" + str(i)] = coord_calc((x1,x2),(w,h))

        #save chamber
        icon_specs["save_chamber"] = coord_calc((0,64),(32,96))
        #save ripple
        icon_specs["save_ripple"] = coord_calc((32,64),(32,6))

        #cycle through collected icons and write to disk
        for icon in icon_specs:
            icon_coords = icon_specs.get(icon)
            cropped_image = equipment_image.crop(icon_coords)
            equipment[icon] = cropped_image
            if save:
                cropped_image.save(
                    os.path.join(
                        ".",
                        "resources",
                        "user",
                        "snes",
                        "metroid",
                        "samus",
                        "sheets"
                    ) + icon + ".png"
                )

    ship_dir = os.path.join(
        ".",
        "resources",
        "app",
        "snes",
        "metroid3",
        "samus",
        "sheets",
        "ship"
    )
    for file in os.listdir(ship_dir):
        icon = "optional_ship_" + file[:file.rfind('.')]
        with(Image.open(os.path.join(ship_dir,file))) as img:
            equipment[icon] = img

    return equipment
