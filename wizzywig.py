#This is more or less a scratch work file
#I am trying to get an estimate of the size and approximate layout of a potential WYSIWYG PNG file
#but probably, some of the code written here will become part of the end result

import os
import json
from PIL import Image, ImageOps, ImageDraw
from lib.metroid3.metroid3 import M3Samus, Metroid3

layout_data = {}
reverse_layout_data = {}

def main():
    global layout_data
    global reverse_layout_data

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

    all_collages = []

    with open("resources/layout.json") as inFile:
        layout_data = json.load(inFile)
        reverse_layout_data = get_reverse_layout()

    for animation, pose in get_all_poses(samus):
        if (pretty_hex(animation),pose) not in reverse_layout_data:
            print(f"Logan 3, IDENTIFY: animation {pretty_hex(animation)[2:]}, pose {pose}")
            image, _ = samus.get_sprite_frame(animation, pose)
            image.show()
            exit()

    for i,row in enumerate(layout_data["layout"]):
        this_row_images = []
        for image_name in [x for x in row]:   #for every image referenced explicitly in the layout
            animation, pose = layout_data["images"][image_name]["used by"][0]   #import a representative animation and pose
            if type(animation) is str and animation[0:2] == "0x":                #convert from hex if needed
                animation = int(animation[2:], 16)

            force = get_property_from_layout_data("force", image_name)
            if force:
                if force.lower() == "upper":
                    image, origin = samus.get_sprite_frame(animation, pose, lower=False)
                elif force.lower() == "lower":
                    image, origin = samus.get_sprite_frame(animation, pose, upper=False)
                else:
                    raise AssertionError(f"received call to force something in pose {image_name}, but did not understand command '{force}'")
            else:
                image, origin = samus.get_sprite_frame(animation, pose)

            if image:
                bordered_image, new_origin = add_borders(image, origin, image_name)

                shift = get_property_from_layout_data("shift", image_name)
                if shift is not None:
                    new_origin = tuple(new_origin[i] - shift[i] for i in range(2))    
                
                this_row_images.append((bordered_image, new_origin))

        collage = make_horizontal_collage(this_row_images)
        all_collages.append(collage)

    full_layout = make_vertical_collage(all_collages)
    full_layout.save("images/layout.png")


def add_borders(image, origin, image_name):
    original_dimensions = get_property_from_layout_data("dimensions", image_name)
    extra_area = get_property_from_layout_data("extra area", image_name)

    dimensions = original_dimensions
    if extra_area is not None:     #there's patches over the top of this pose to fill it out
        for x0,x1,y0,y1 in extra_area:
            dimensions = (min(dimensions[0],x0),max(dimensions[1],x1),min(dimensions[2],y0),max(dimensions[3],y1))

    border = ( \
                -origin[0]-dimensions[0],   #left
                -origin[1]-dimensions[2],   #top,
                dimensions[1] - (image.size[0] - origin[0]), #right,
                dimensions[3] - (image.size[1] - origin[1])  #bottom
            )
    image_with_border = ImageOps.expand(image,border=border,fill=(0,0,0x7F,0x3F))      #fill in a psuedo-transparency for now
    origin = (origin[0] + border[0], origin[1] + border[1])
    if extra_area is not None:   #we need to block off some areas that can't actual be used
        mask = Image.new("RGBA", (dimensions[1]-dimensions[0],dimensions[3]-dimensions[2]), (0,0,0x7F,0xFF))
        x0,x1,y0,y1 = original_dimensions
        ImageDraw.Draw(mask).rectangle((x0+origin[0],y0+origin[1],x1+origin[0]-1,y1+origin[1]-1), fill = 0)
        for x0,x1,y0,y1 in extra_area:
            ImageDraw.Draw(mask).rectangle((x0+origin[0],y0+origin[1],x1+origin[0]-1,y1+origin[1]-1), fill = 0)

        image_with_border.paste(mask,mask=mask)


    image_with_border = ImageOps.expand(image_with_border,border=1,fill=(0,0,0x7F,0xFF))   #hard border around the actual draw space
    origin = tuple(x+1 for x in origin)
    

    return image_with_border, origin


def get_reverse_layout():
    reverse_layout = {}
    for image_name, image_dict in layout_data["images"].items():
        for animation, pose in image_dict["used by"]:
            reverse_layout[(animation.lower(), pose)] = image_name
    return reverse_layout

def get_property_from_layout_data(property, image_name):
    FAILSAFE = 100
    for _ in range(FAILSAFE):
        if property in layout_data["images"][image_name]:
            return layout_data["images"][image_name][property]
        elif "parent" in layout_data["images"][image_name]:
            image_name = layout_data["images"][image_name]["parent"]
        else:
            return None
    else:
        raise AssertionError(f"ncountered infinite parental loop in layout.json while investigating {image_name}")


def make_horizontal_collage(image_list,verbose=False):
    y_min = min([-origin[1] for image,origin in image_list])
    y_max = max([image.size[1]-origin[1] for image,origin in image_list])

    num_images = len(image_list)
    
    collage_width = sum([image.size[0] for image,_ in image_list])
    collage_y_size = y_max-y_min

    collage = Image.new("RGBA",(collage_width,collage_y_size),0)

    current_x_position = 0
    for image, origin in image_list:
        border =    ( \
                        0,                     #left
                        -origin[1]-y_min,     #top
                        0,                     #right
                        origin[1]+y_max-image.size[1]      #bottom
                    )
        bordered_image = ImageOps.expand(image,border=border,fill=(0,0,0x7F,0xFF))
        collage.paste(bordered_image, (current_x_position,0))
        current_x_position += image.size[0]

    return collage

def make_vertical_collage(image_list):
    width = max([image.size[0] for image in image_list])
    height = sum([image.size[1] for image in image_list])

    collage = Image.new("RGBA", (width,height), 0)
    current_y = 0
    for image in image_list:
        collage.paste(image, ((width-image.size[0])//2,current_y))
        current_y += image.size[1]
    return collage

def pretty_hex(x,digits=2):
    return '0x' + hex(x)[2:].zfill(digits)


def get_all_poses(samus):
    # STANDARD_ANIMATION_LIST = [ \
    #     0x00,0x9B,0x01,0x03,0x05,0x07,0x25,0x8B,0x9C,0x8D,0x02,0x04,0x06,0x08,0x26,0x8C,
    #     0x9D,0x8E,0x09,0x0F,0x0B,0x11,0x0A,0x10,0x0C,0x12,0x4B,0x55,0x57,0x59,0x4D,0x51,
    #     0x15,0x69,0x13,0x6B,0x17,0x2F,0x8F,0x9E,0x91,0xA4,0xE0,0xE2,0xE6,0xE4,0x4C,0x56,
    #     0x58,0x5A,0x4E,0x52,0x16,0x6A,0x14,0x6C,0x18,0x30,0x90,0x9F,0x92,0xA5,0xE1,0xE3,
    #     0xE7,0xE5,0x19,0x1B,0x83,0xA6,0x1A,0x1C,0x84,0xA7,0x37,0x1D,0x1E,0x31,
    #     0x3D,0x38,0x41,0x1F,0x32,0x3E,0x36,0xF1,0x79,0x7B,0x7D,0x7F,0x7A,0x7C,0x7E,0x80,
    #     0xF3,0xF5,0x27,0x85,0x71,0x73,0x43,0x97,0xA2,0x99,0x35,0xF7,0xF9,0xFB,0x35,0xF2,
    #     0xF4,0xF6,0x28,0x86,0x72,0x74,0x44,0x98,0xA3,0x9A,0x36,0xF8,0xFA,0xFC,0x29,0x2B,
    #     0x6D,0x67,0x6F,0x2D,0x87,0x93,0xA0,0x95,0x2A,0x2C,0x6E,0x68,0x70,0x2E,0x88,0x94,
    #     0xA1,0x96,0x4A,0x76,0x78,0xBF,0xC1,0xC3,0x49,0x75,0x77,0xC0,0xC2,0xC4,0x53,0x50,
    #     0x54,0x4F,0xB8,0xB9,0xEC,0xED,0xEE,0xEF,0xF0,0xBA,0xBB,0xBC,0xBD,0xBE,0xC7,0xCB,
    #     0xC9,0xC8,0xCC,0xCA,0xD3,0xD4,0xD5,0xD9,0xD6,0xDA,0xE8,0xEA,0xE9,0xEB
    # ]

    STANDARD_ANIMATION_LIST = [
        0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0A,0x0B,0x0C,0x0F,0x10,0x11,
        0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1D,0x1E,0x1F,0x25,0x26,
        0x27,0x28,0x29,0x2A,0x2B,0x2C,0x2D,0x2E,0x2F,0x30,0x31,0x32,0x35,0x36,0x37,0x38,
        0x3B,0x3C,0x3D,0x3E,0x41,0x43,0x44,0x49,0x4A,0x4B,0x4C,0x4D,0x4E,0x4F,0x50,0x51,
        0x52,0x53,0x54,0x55,0x56,0x57,0x58,0x59,0x5A,0x67,0x68,0x69,0x6A,0x6B,0x6C,0x6D,
        0x6E,0x6F,0x70,0x71,0x72,0x73,0x74,0x75,0x76,0x77,0x78,0x79,0x7A,0x7B,0x7C,0x7D,
        0x7E,0x7F,0x80,0x81,0x82,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8A,0x8B,0x8C,0x8D,
        0x8E,0x8F,0x90,0x91,0x92,0x93,0x94,0x95,0x96,0x97,0x98,0x99,0x9A,0x9B,0x9C,0x9D,
        0x9E,0x9F,0xA0,0xA1,0xA2,0xA3,0xA4,0xA5,0xA6,0xA7,0xB2,0xB3,0xB8,0xB9,0xBA,0xBB,
        0xBC,0xBD,0xBE,0xBF,0xC0,0xC1,0xC2,0xC3,0xC4,0xC7,0xC8,0xC9,0xCA,0xCB,0xCC,0xCD,
        0xCE,0xCF,0xD0,0xD1,0xD2,0xD3,0xD4,0xD5,0xD6,0xD7,0xD8,0xD9,0xDA,0xE0,0xE1,0xE2,
        0xE3,0xE4,0xE5,0xE6,0xE7,0xE8,0xE9,0xEA,0xEB,0xEC,0xED,0xEE,0xEF,0xF0,0xF1,0xF2,
        0xF3,0xF4,0xF5,0xF6,0xF7,0xF8,0xF9,0xFA,0xFB,0xFC
    ]

    EXCEPTION_LIST = []#get_exception_list()

    # for animation in [0xB2,0xB3]:   #grapple stuff
    #     for pose in range(16,32):   #the ones with legs straight are unused, 16 of the first 32 are flips
    #         yield animation, pose
    #     yield animation, 64
    #     yield animation, 65

    # for animation in [0x81,0x82]:   #sparks from screw attack
    #     for pose in [1,7,13,19]:
    #         yield animation, pose


    for animation, pose in [(animation, 0) for animation in STANDARD_ANIMATION_LIST]:
        FAILSAFE_COUNTER = 100
        kicks = 0
        if animation in [0x00,0x9B]:
            kicks += 1    #loader stuff after elevator
        elif animation in [0x29,0x2A,0x67,0x68]:
            kicks += 1    #falling far distances
        elif animation in [0x19,0x1A,0x1B,0x1C,0x81,0x82]:
            kicks += 1    #walljump cue
        elif animation in [0xD3,0xD4]:
            kicks += 2    #crystal flash
        elif animation in [0xE9]:
            kicks += 3    #mother brain sequence
        elif animation in [0xEA,0xEB]:
            kicks += 1    #different type of mother brain sequence

        for _ in range(FAILSAFE_COUNTER):
            control_code, *_ = samus.rom_data.get_pose_control_data(animation,pose)
            if control_code in [0xF6] or (animation,pose) in EXCEPTION_LIST:   #skip
                pose += 1
            elif control_code in [0xF7,0xFB]:   #supplication sequence or walljump sequence
                pose += 1
                kicks += 2
            elif control_code in [0xF8,0xFD,0xFE]:   #1-byte argument terminal
                pose += 2
                kicks -= 1
            elif control_code in [0xFA]:   #2-byte argument terminal
                pose += 3
                kicks -= 1
            elif control_code in [0xFC]:   #4-byte argument terminal
                pose += 5
                kicks -= 1
            elif control_code in [0xF9]:   #6-byte argument terminal
                pose += 7
                kicks -= 1
            elif control_code in [0xFF]:   #just terminal
                pose += 1
                kicks -= 1
            else:
                yield animation, pose
                pose += 1
            
            if kicks < 0:    #end of the line
                break
        else:
            raise AssertionError(f"Reached FAILSAFE_COUNTER in get_all_poses().  Animation {hex(animation)}, pose {hex(pose)}")

def get_exception_list():
    exceptions = []
    exceptions.extend([(i, j) for i in [0x00,0x9B] for j in range(2,96)])   #launcher poses
    for i in [0x00,0x9B]:
        exceptions.remove((i,2))
        exceptions.remove((i,3))  #no lightning
        exceptions.remove((i,4))
        exceptions.remove((i,6))
        exceptions.remove((i,80))
        exceptions.remove((i,82))
        exceptions.remove((i,84))
        exceptions.remove((i,86))
        exceptions.remove((i,88))
    exceptions.extend([(i,j) for i in [0x83,0x84] for j in range(1,47)])   #the "jumping" walljumps should share
    exceptions.extend([(i,j) for i in [0x26,0x8C,0x9D,0x8E] for j in range(0,3)])   #duplicate standing turns
    exceptions.extend([(i,j) for i in [0x30,0x90,0x9F,0x92] for j in range(0,3)])   #duplicate jumping turns
    exceptions.extend([(i,j) for i in [0x44,0x98,0xA3,0x9A] for j in range(0,3)])   #duplicate crouching turns
    exceptions.extend([(i,j) for i in [0x88,0x94,0xA1,0x96] for j in range(0,3)])   #duplicate falling turns
    exceptions.extend([(i,j) for i in [0xBF,0xC0,0xC1,0xC2,0xC3,0xC4] for j in range(0,3)])   #moonwalk turns
    exceptions.extend([(i,j) for i in [0x8B,0x8F,0x93,0x97] for j in range(0,3)])   #up turns are diag up turns
    exceptions.extend([(i,j) for i in [0x3D,0x3E] for j in range(0,2)])   #unmorph can just be reverse morph
    exceptions.extend([(i,0) for i in [0x1B,0x1C,0x81,0x82]])   #the "launch" frame for jump is same
    exceptions.extend([(i,11) for i in [0x1B,0x1C]])    #wallkick can be borrowed from spin jump
    exceptions.extend([(i,27) for i in [0x81,0x82]])    #wallkick can be borrowed from spin jump
    exceptions.extend([(i,0) for i in [0x35,0x36,0xF7,0xF8,0xF9,0xFA,0xFB,0xFC]])   #stand to crouch and crouch to stand are opposites
    exceptions.extend([(i,0) for i in [0xA4,0xA5,0xE0,0xE1,0xE2,0xE3,0xE4,0xE5,0xE6]])   #the "launch" frame is the same as the "land" frame
    exceptions.extend([(i,j) for i in [0xD3,0xD4] for j in [0,1,3,6,12,13,14]])  #explicitly duplicated
    exceptions.extend([(i,j) for i in [0xE8,0xE9] for j in range(6)])  #unmorph and bonk
    exceptions.extend([(i,0) for i in [0x05,0x06,0x57,0x58,0x69,0x6A,0x71,0x72,0x6D,0x6E,]])  #aim up diag duplications

    
    return exceptions

if __name__ == "__main__":
    main()