#This is more or less a scratch work file
#I am trying to get an estimate of the size and approximate layout of a potential WYSIWYG PNG file
#but probably, some of the code written here will become part of the end result

import os
import json
from PIL import Image, ImageOps, ImageDraw
from lib.RomHandler import util
from lib.metroid3.metroid3 import M3Samus, Metroid3
from lib.layout import Layout

def main():
    if not os.path.isdir('images'):
        os.mkdir('images')
    def get_sfc_filename(path):
        for file in os.listdir(path):
            if file.endswith(".sfc") or file.endswith(".smc"):
                return os.path.join(path, file)
        else:
            raise AssertionError(f"There is no sfc file in directory {path}")

    game = Metroid3(get_sfc_filename(os.path.join("resources", "metroid3")),None)
    samus = M3Samus(game.rom_data, game.meta_data)

    layout = Layout("resources/metroid3/layout.json")
    all_images = import_all_images_from_ROM(samus,layout)

    full_layout = export_all_images_to_PNG(all_images, layout)
    full_layout.save("images/samus.png")

def import_all_images_from_ROM(samus,layout):
    all_images = {}
    for image_name in [name for row in layout.get_rows() for name in row]:  #for every image referenced explicitly in the layout
        animation, pose = layout.data["images"][image_name]["used by"][0]   #import a representative animation and pose
        if type(animation) is str and animation[0:2] == "0x":                #convert from hex if needed
            animation = int(animation[2:], 16)

        force = layout.get_property("force", image_name)
        if force:
            if force.lower() == "upper":
                image, origin = samus.get_sprite_pose(animation, pose, lower=False)
            elif force.lower() == "lower":
                image, origin = samus.get_sprite_pose(animation, pose, upper=False)
            else:
                raise AssertionError(f"received call to force something in pose {image_name}, but did not understand command '{force}'")
        else:
            image, origin = samus.get_sprite_pose(animation, pose)

        if image:
            #bordered_image, new_origin = layout.add_borders(image, origin, image_name)   
            
            all_images[image_name] = (image, origin)
        else:
            print(f"WARNING: Did not generate image for {image_name}")

    return all_images

def export_all_images_to_PNG(all_images, layout):
    all_collages = []
    for i,row in enumerate(layout.get_rows()):
        this_row_images = []
        for image_name in [x for x in row]:   #for every image referenced explicitly in the layout
            image, origin = all_images[image_name]

            if image:
                bordered_image, new_origin = layout.add_borders(image, origin, image_name)

                shift = layout.get_property("shift", image_name)
                if shift is not None:
                    new_origin = tuple(new_origin[i] - shift[i] for i in range(2))    
                
                this_row_images.append((bordered_image, new_origin))
            else:
                print(f"WARNING: Did not generate image for {image_name}")

        collage = layout.make_horizontal_collage(this_row_images)
        all_collages.append(collage)

    full_layout = layout.make_vertical_collage(all_collages)
    return full_layout

if __name__ == "__main__":
    main()