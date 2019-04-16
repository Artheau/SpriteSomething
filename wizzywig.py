#This is more or less a scratch work file
#I am trying to get an estimate of the size and approximate layout of a potential WYSIWYG PNG file
#but probably, some of the code written here will become part of the end result

import os
from PIL import Image, ImageOps
from lib.metroid3.metroid3 import M3Samus, Metroid3

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

    total_size_esimate = 0
    amalgate_images = {}

    for animation, pose in get_all_poses(samus):
        if animation in [0xD3,0xD4,0x81,0x82]:
            image, origin = samus.get_sprite_frame(animation, pose, lower=False)
        else:
            image, origin = samus.get_sprite_frame(animation, pose)

        if image:
            x_img, y_img = image.size
            x_0, y_0 = origin
            x_borders = (-x_0, -x_0 + x_img)
            y_borders = (-y_0, -y_0 + y_img)

            map_name, map_dimensions = assign_to_tilemap(x_borders,y_borders)
            if map_name:
                pass#print(f"Assigned animation {hex(animation)}, pose {hex(pose)} to map '{map_name}'")
            else:
                pass#print(f"Could not assign animation {hex(animation)}, pose {hex(pose)} with dimensions x {x_borders}, y {y_borders}")
            size_estimate = ((map_dimensions[1]-map_dimensions[0])*(map_dimensions[3]-map_dimensions[2]))//2

            total_size_esimate += size_estimate

            border =( \
                         x_borders[0]-map_dimensions[0],     #left
                         y_borders[0]-map_dimensions[2],     #top
                        -x_borders[1]+map_dimensions[1],     #right
                        -y_borders[1]+map_dimensions[3]      #bottom
                    )
            image_with_border = ImageOps.expand(image,border=border,fill=(0,0,0x7F,0x1F))
            image_with_border = ImageOps.expand(image_with_border,border=1,fill=(0,0,0x7F,0xFF))
            #image_with_border.save(f"images/a_{pretty_hex(animation)[2:]}_p_{pose}.png")

            new_origin = (origin[0]+border[0]+1, origin[1]+border[1]+1)

            if animation in amalgate_images:
                amalgate_images[animation].append((image_with_border, new_origin))
            else:
                amalgate_images[animation] = [(image_with_border, new_origin)]

    print(f"Size estimate: {total_size_esimate//1024} kB")
    for animation,image_list in amalgate_images.items():
        verbose_condition = (animation == 0x55)
        collage = make_collage(image_list,verbose=verbose_condition)
        collage.save(f"images/collage_{pretty_hex(animation)[2:]}.png")


def make_collage(image_list,verbose=False):
    if verbose:
        print([[image.size, origin] for image,origin in image_list])
    x_min = min([-origin[0] for image,origin in image_list])
    x_max = max([image.size[0]-origin[0] for image,origin in image_list])
    y_min = min([-origin[1] for image,origin in image_list])
    y_max = max([image.size[1]-origin[1] for image,origin in image_list])
    
    if verbose:
        print(x_min,x_max,y_min,y_max)

    num_images = len(image_list)
    
    collage_x_size = x_max-x_min
    collage_y_size = y_max-y_min

    collage = Image.new("RGBA",(num_images*collage_x_size,collage_y_size),0)

    for i, (image, origin) in enumerate(image_list):
        border =    ( \
                        -origin[0]-x_min,     #left
                        -origin[1]-y_min,     #top
                        origin[0]+x_max-image.size[0],     #right
                        origin[1]+y_max-image.size[1]      #bottom
                    )
        bordered_image = ImageOps.expand(image,border=border,fill=(0,0,0x7F,0xFF))
        collage.paste(bordered_image, (i*collage_x_size,0))


    return collage

def pretty_hex(x,digits=2):
    return '0x' + hex(x)[2:].zfill(digits)


def assign_to_tilemap(x_borders,y_borders):
    TILEMAPS = { \
        "tiny":                    (-12, 12, -12, 12),
        "half":                    (-16, 16, -16, 16),
        "half, tight fit":         (-19, 19, -19, 19),   #need a workaround
        "standard":                (-20, 20, -23, 25),
        "tall":                    (-16, 16, -27, 29),
        "tall up":                 (-16, 16, -32, 24),
        "tall down":               (-16, 16, -24, 32),
        "supertall":               (-12, 12, -32, 32),
        "wide":                    (-24, 24, -20, 20),
        "narrow":                  (-28, 28, -16, 16),
        "narrow right":            (-25, 31, -16, 16),
        "narrow left":             (-31, 25, -16, 16),
        "elevator":                (-16, 16, -24, 32),
        "tall right":              (-11, 21, -24, 32),
        "tall left":               (-21, 11, -24, 32),
        "standard down 1":         (-20, 20, -22, 26),
        "standard down 2":         (-20, 20, -21, 27),
        "standard down 4":         (-20, 20, -19, 29),
        "standard right 2 down 2": (-18, 22, -21, 27),
        "standard left 2 down 2":  (-22, 18, -21, 27),
        "tall left, tight fit":    (-21, 12, -27, 29),  #need additional tiles along right side to make this work
        "tall right, tight fit":   (-12, 21, -27, 29),  #need additional tiles along left side to make this work
        #need special arrangements for
        #death
        #crystal flash bubble
        #spin attack (this does not exist in vanilla, but it will)
        #grapple (grapple deserves my greatest ire)
        #cannon ports
        #palettes
        #file select menu
    }

    for map_name, map_dimensions in TILEMAPS.items():
        x_min, x_max, y_min, y_max = map_dimensions
        if x_borders[0] >= x_min and x_borders[1] <= x_max and \
           y_borders[0] >= y_min and y_borders[1] <= y_max:

           return map_name, map_dimensions
    else:
        return None, (x_borders[0], x_borders[1], y_borders[0], y_borders[1])


def get_all_poses(samus):
    STANDARD_ANIMATION_LIST = [ \
        0x00,0x9B,0x01,0x03,0x05,0x07,0x25,0x8B,0x9C,0x8D,0x02,0x04,0x06,0x08,0x26,0x8C,
        0x9D,0x8E,0x09,0x0F,0x0B,0x11,0x0A,0x10,0x0C,0x12,0x4B,0x55,0x57,0x59,0x4D,0x51,
        0x15,0x69,0x13,0x6B,0x17,0x2F,0x8F,0x9E,0x91,0xA4,0xE0,0xE2,0xE6,0xE4,0x4C,0x56,
        0x58,0x5A,0x4E,0x52,0x16,0x6A,0x14,0x6C,0x18,0x30,0x90,0x9F,0x92,0xA5,0xE1,0xE3,
        0xE7,0xE5,0x19,0x1B,0x83,0xA6,0x1A,0x1C,0x84,0xA7,0x37,0x1D,0x1E,0x31,
        0x3D,0x38,0x41,0x1F,0x32,0x3E,0x36,0xF1,#0x79,0x7B,0x7D,0x7F,0x7A,0x7C,0x7E,0x80,
        0xF3,0xF5,0x27,0x85,0x71,0x73,0x43,0x97,0xA2,0x99,0x35,0xF7,0xF9,0xFB,0x35,0xF2,
        0xF4,0xF6,0x28,0x86,0x72,0x74,0x44,0x98,0xA3,0x9A,0x36,0xF8,0xFA,0xFC,0x29,0x2B,
        0x6D,0x67,0x6F,0x2D,0x87,0x93,0xA0,0x95,0x2A,0x2C,0x6E,0x68,0x70,0x2E,0x88,0x94,
        0xA1,0x96,0x4A,0x76,0x78,0xBF,0xC1,0xC3,0x49,0x75,0x77,0xC0,0xC2,0xC4,0x53,0x50,
        0x54,0x4F,0xB8,0xB9,0xEC,0xED,0xEE,0xEF,0xF0,0xBA,0xBB,0xBC,0xBD,0xBE,0xC7,0xCB,
        0xC9,0xC8,0xCC,0xCA,0xD3,0xD4,0xD5,0xD9,0xD6,0xDA,0xE8,0xEA,0xE9,0xEB
    ]

    EXCEPTION_LIST = get_exception_list()

    for animation in [0xB2,0xB3]:   #grapple stuff
        for pose in range(16,32):   #the ones with legs straight are unused, the first 16 are flips
            yield animation, pose
        yield animation, 64
        yield animation, 65

    for animation in [0x81,0x82]:   #sparks from screw attack
        for pose in [1,7,13,19]:
            yield animation, pose


    for animation, pose in [(animation, 0) for animation in STANDARD_ANIMATION_LIST]:
        FAILSAFE_COUNTER = 100
        kicks = 0  #TODO: fix
        if animation in [0x00,0x9B]:
            kicks += 1    #loader stuff after elevator
        elif animation in [0x19,0x1A,0x1B,0x1C,0x29,0x2A,0x67,0x68,0x81,0x82]:
            kicks += 1    #landing after a jump, or walljump
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