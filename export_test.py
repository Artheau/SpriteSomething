import argparse
import os
from PIL import Image

from lib import util
from lib.constants import *

data = None

def main():
    for directory_name in ["animations","images"]:
        if not os.access(directory_name, os.F_OK):
            os.mkdir(directory_name)

    command_line_args = process_command_line_args()

    if USE_MODIFIED_ROM:
        command_line_args[ROM_FILENAME_ARG_KEY] = "sm_orig_modified.sfc"

    #main data
    global data
    data = util.Samus(command_line_args[ROM_FILENAME_ARG_KEY], load_supertiles=False)
    pal = command_line_args[PALETTE_ARG_KEY]


    #export_specific_pose(0x1D, 0, pal)  #as (animation_number, pose_number, palette_name)

    #export_custom_sequence(pal)

    export_all_raw_animations(pal)

    for anim in [anim for anim in range(len(data.animations)) if anim not in IGNORED_ANIMATIONS]:
        for pose in range(len(data.animations[anim].poses)):
            export_specific_pose(anim, pose, pal)  #as (animation_number, pose_number, palette_name)

    #export_tiles(0x00, 1, pal)          #as (animation number, pose_number, palette_name)




def export_custom_sequence(palette_name, zoom=2):
    events = { 80:{'kick':True}, \
               200:{'heavy_breathing':True,'kick':True}, \
               400:{'new_animation':0x0A}, \
               500:{'new_animation':0x1A}}   #I'm thinking that this will eventually be JSON
    data.animation_sequence_to_gif('animations/test_sequence.gif', zoom=zoom, starting_animation=0xE9, \
        events=events, palette_type=palette_name)


def export_all_raw_animations(palette_name, zoom=2):
    for animation_number in range(len(data.animations)):
        if data.animations[animation_number].used:
            try:
                data.animations[animation_number].gif(f"animations/animation_raw_{hex(animation_number)[2:].zfill(2)}.gif", data.palettes[palette_name],zoom=zoom)
            except AssertionError as e:
                print(f"AssertionError on animation {hex(animation_number)}: {e.args}")


def export_specific_pose(animation_number, pose_number, palette_name, zoom=3):
    pose = data.animations[animation_number].poses[pose_number]
    img = pose.to_image(data.palettes[palette_name],zoom=zoom)
    #img.show()
    img.save(f"images/pose_{pose.ID}.png")


def export_tiles(animation_number, pose_number, palette_name, zoom=2):
    for tile in data.animations[animation_number].poses[pose_number].tiles:
        img = tile.to_image(data.palettes[palette_name],zoom=zoom)
        #img.show()
        img.save(f"tiles/tile_{tile.ID}.png")


def process_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom",
                        dest=ROM_FILENAME_ARG_KEY,
                        help="Location of the rom file; e.g. /my_dir/sm_orig.sfc",
                        metavar="<rom_filename>",
                        default='sm_orig.sfc')
    parser.add_argument("--palette",
                        dest=PALETTE_ARG_KEY,
                        help="Which palette to use; i.e. one of 'standard', 'varia', or 'gravity'",
                        metavar="<palette>",
                        default='standard')
    
    command_line_args = vars(parser.parse_args())

    return command_line_args
            


if __name__ == "__main__":
    main()