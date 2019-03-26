import argparse
import os
from PIL import Image

from lib import util
from lib.constants import *

data = None

def main():
    command_line_args = process_command_line_args()

    if USE_MODIFIED_ROM:
        command_line_args[ROM_FILENAME_ARG_KEY] = "sm_orig_modified.sfc"

    #main data
    global data
    data = util.Samus(command_line_args[ROM_FILENAME_ARG_KEY], load_supertiles=False)
    givenPal = command_line_args[PALETTE_ARG_KEY]
    givenAni = command_line_args[ANI_ARG_KEY]
    givenPose = command_line_args[POSE_ARG_KEY]


    export_specific_raw_animation(givenAni, givenPal)  #as (animation_number, palette_name)

    #export_specific_pose(givenAni, givenPose, givenPal)  #as (animation_number, pose_number, palette_name)

    #export_specific_animation_tiles(0x00, givenPal)  # as (animation_number, palette_name)

    #export_specific_pose_tiles(0x00, 1, givenPal)  # as (animation_number, pose_number, palette_name)

    #export_specific_pose_tile(0x00, 1, 1, givenPal)  # as (animation_numer, pose_number, tile_number, palette_name)

    #export_custom_sequence(givenPal)

    #export_all_raw_animations(givenPal)

    #export_all_poses(givenPal)

    #export_tiles(0x00, 1, givenPal)          #as (animation_number, pose_number, palette_name)

    #export_all_animation_tiles(givenPal)

    #export_all_pose_tiles(0x00, 1, givenPal)


def check_dirs(dirs=[]):
    if not isinstance(dirs,list):
        dirs = [dirs]
    for directory_name in dirs:
        if not os.access(directory_name, os.F_OK):
            os.mkdir(directory_name)

def export_custom_sequence(palette_name, zoom=2, quiet=False):
    check_dirs("animations")
    if not quiet:
        print(f"Exporting custom sequence with",palette_name[0].upper() + palette_name[1:],"Palette at Zoom Level",zoom)
    events = { 80:{'kick':True}, \
               200:{'heavy_breathing':True,'kick':True}, \
               400:{'new_animation':0x0A}, \
               500:{'new_animation':0x1A}}   #I'm thinking that this will eventually be JSON
    data.animation_sequence_to_gif('animations/test_sequence.gif', zoom=zoom, starting_animation=0xE9, \
        events=events, palette_type=palette_name)


def export_specific_raw_animation(animation_number=0x0B,palette_name="standard", zoom=2, quiet=False):
    check_dirs("animations")
    if not quiet:
        print(f"Exporting raw Animation #{animation_number} with",palette_name[0].upper() + palette_name[1:],"Palette at Zoom Level",zoom)
    if data.animations[animation_number].used:
        try:
            data.animations[animation_number].gif(f"animations/animation_raw_{hex(animation_number)[2:].zfill(2)}.gif", data.palettes[palette_name],zoom=zoom)
        except AssertionError as e:
            print(f"AssertionError on animation {hex(animation_number)}: {e.args}")


def export_all_raw_animations(palette_name="standard", zoom=2):
    print(f"Exporting all animations")
    for animation_number in range(len(data.animations)):
        export_specific_raw_animation(animation_number, palette_name, zoom, True)


def export_specific_pose(animation_number=0x0B, pose_number=9, palette_name="standard", zoom=3, quiet=False):
    check_dirs("images")
    if not quiet:
        print(f"Exporting specific pose from Animation #{animation_number}, Pose #{pose_number} with",palette_name[0].upper() + palette_name[1:],"Palette at Zoom Level",zoom)
    pose = data.animations[animation_number].poses[pose_number]
    img = pose.to_image(data.palettes[palette_name],zoom=zoom)
    #img.show()
    img.save(f"images/pose_{pose.ID}.png")


def export_all_poses(palette_name="standard", zoom=3):
    print(f"Exporting all poses")
    for anim in [anim for anim in range(len(data.animations)) if anim not in IGNORED_ANIMATIONS]:
        for pose in range(len(data.animations[anim].poses)):
            export_specific_pose(anim, pose, palette_name, zoom, True)  #as (animation_number, pose_number, palette_name, zoom)

def export_specific_animation_tiles(animation_number=0x0B, palette_name="standard", zoom=2):
    print(f"Exporting all tiles from Animation #{animation_number} with",palette_name[0].upper() + palette_name[1:],"Palette at Zoom Level",zoom)
    for pose in data.animations[animation_number].poses:
        export_specific_pose_tiles(animation_number, int(pose.ID.split(",P")[1]), palette_name, zoom, True)

def export_specific_pose_tiles(animation_number=0x0B, pose_number=0, palette_name="standard", zoom=2, quiet=False):
    if not quiet:
        print(f"Exporting all tiles from Animation #{animation_number}, Pose #{pose_number} with",palette_name[0].upper() + palette_name[1:],"Palette at Zoom Level",zoom)
    for tile in data.animations[animation_number].poses[pose_number].tiles:
        export_specific_pose_tile(animation_number, pose_number, int(tile.ID.split(",T")[1]), palette_name, zoom, True)

def export_specific_pose_tile(animation_number=0x0B, pose_number=0, tile_number=0, palette_name="standard", zoom=2, quiet=False):
    check_dirs("tiles")
    if not quiet:
        print(f"Exporting specific tile from Animation #{animation_number}, Pose #{pose_number}, Tile #{tile_number} with",palette_name[0].upper() + palette_name[1:],"Palette at Zoom Level",zoom)
    img = data.animations[animation_number].poses[pose_number].tiles[tile_number].to_image(data.palettes[palette_name],zoom=zoom)
    #img.show()
    if img:
        img.save(f"tiles/tile_0x{animation_number:02x},P{pose_number},T{tile_number}.png")

def export_all_animation_tiles(palette_name="standard", zoom=2):
    print(f"Exporting all tiles with",palette_name[0].upper() + palette_name[1:],"Palette at Zoom Level",zoom)
    for animation_number in range(len(data.animations)):
        export_specific_animation_tiles(animation_number, palette_name)

def export_tiles(animation_number=0x0B, pose_number=0, palette_name="standard", zoom=2):
    export_specific_pose_tiles(animation_number, pose_number, palette_name, zoom)

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
    parser.add_argument("--animation",
                        dest=ANI_ARG_KEY,
                        help="Which animation ID to export",
                        metavar="<animation>",
                        default=0x0B)
    parser.add_argument("--pose",
                        dest=POSE_ARG_KEY,
                        help="Which pose ID to export",
                        metavar="<pose>",
                        default=0)

    command_line_args = vars(parser.parse_args())

    return command_line_args



if __name__ == "__main__":
    main()
