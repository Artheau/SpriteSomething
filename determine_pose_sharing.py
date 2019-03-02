#Written by Artheau
#between Feb. 2019 and March 3019
#although mostly in the days closer to the former and further from the latter

import os
import re
import json
import argparse
from itertools import chain

import util
from constants import *

data = None


def get_all_tile_locations(this_tile):
    #go looking through all the poses and figure out where this tile appears
    all_locations_dict = {}
    for (i,animation) in enumerate(data.animations):
        for (j,pose) in enumerate(animation.poses):
            location_list = locate_tile_in_pose(this_tile,pose)    #list of (ref_index,supertile_index)
            if location_list:
                all_locations_dict[(i,j)] = location_list
    return all_locations_dict

def locate_tile_in_pose(this_tile,pose):
    returnvalue = []
    for (i,tile_ref) in enumerate(pose.tiles):
        for (j,addr) in enumerate(tile_ref.real_tile.addresses):
            if addr == this_tile:
                returnvalue.append((i,j))
    return returnvalue


################################################################################

def process_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom",
                        dest=ROM_FILENAME_ARG_KEY,
                        help="Location of the rom file; e.g. /my_dir/sm_orig.sfc",
                        metavar="<rom_filename>",
                        default='sm_orig.sfc')
    
    command_line_args = vars(parser.parse_args())

    return command_line_args


def get_pose_association_dict(command_line_args):
    global data
    association_dict = {}

    for tile_type in ["upper","lower"]:

        util.tile_type_restriction = tile_type

        data = util.Samus(command_line_args[ROM_FILENAME_ARG_KEY],load_supertiles=False,report_tiles=False)

        association_dict[tile_type] = {}

        for tile in util.global_tiles:
            location_dict = get_all_tile_locations(tile)
            if location_dict:
                first_key = next(iter(location_dict.keys()))
                indices_of_exemplar_tile = location_dict[first_key]
                location = data.animations[first_key[0]].poses[first_key[1]].tiles[indices_of_exemplar_tile[0][0]].location

                pose_ID_list = sorted([data.animations[animation_number].poses[pose_number].ID for animation_number, pose_number in location_dict.keys()])
                lowest_ID = min(pose_ID_list)

                if lowest_ID in association_dict[tile_type]:
                    if pose_ID_list in association_dict[tile_type][lowest_ID]:
                        pass
                    else:
                        association_dict[tile_type][lowest_ID].append(pose_ID_list)
                else:
                    association_dict[tile_type][lowest_ID] = [pose_ID_list]
    return association_dict

def regex_parse(s):
    coord = re.match("(?P<anim_num>.*),P(?P<pose_num>.*)", s)
    if coord:
        return coord.groups()
    else:
        raise AssertionError(f"Bad pose ID in regex_parse: {s}")

def export_specific_pose(animation_number, pose_number, subdir, palette_name='standard', zoom=1):
    pose = data.animations[animation_number].poses[pose_number]
    img = pose.to_image(data.palettes[palette_name],zoom=zoom)
    if img:
        if not os.access(f'tiles/{subdir}', os.F_OK):
            os.mkdir(f'tiles/{subdir}')
        img.save(f"tiles/{subdir}/pose_{pose.ID}.png")
    else:
        pass


def main():
    if not os.access('tiles', os.F_OK):
        os.mkdir('tiles')

    command_line_args = process_command_line_args()

    association_dict = get_pose_association_dict(command_line_args)

    #record the pose associations
    with open(f'pose_sharing.json', 'w') as file:
        file.write(json.dumps(association_dict,indent=5))

    global data

    for tile_type in association_dict.keys():
        util.tile_type_restriction = tile_type
        #print(util.tile_type_restriction)
        data = util.Samus(command_line_args[ROM_FILENAME_ARG_KEY],load_supertiles=False,report_tiles=False)
        for key in association_dict[tile_type]:
            hex_anim_num, str_pose_num = regex_parse(key)
            anim_num = int(hex_anim_num, 16)
            pose_num = int(str_pose_num)
            export_specific_pose(anim_num, pose_num, tile_type)

    
if __name__ == "__main__":
    main()