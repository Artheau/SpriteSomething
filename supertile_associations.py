#Written by Artheau
#between Feb. 2019 and March 3019
#although mostly in the days closer to the former and further from the latter

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



def main():
    command_line_args = process_command_line_args()

    global data
    data = util.Samus(command_line_args[ROM_FILENAME_ARG_KEY],load_supertiles=True)

    with open('supertile_locations.txt', 'w') as file:
        for tile in util.global_tiles:
            location_dict = get_all_tile_locations(tile)
            first_key = next(iter(location_dict.keys()))
            indices_of_exemplar_tile = location_dict[first_key]
            location = data.animations[first_key[0]].poses[first_key[1]].tiles[indices_of_exemplar_tile[0][0]].location
            file.write(f"Locations of Tile {hex(location)}:\n")
            for animation_number, pose_number in location_dict.keys():
                file.write(f"{data.animations[animation_number].poses[pose_number].ID}\n")
            file.write("\n")


    with open('pose_makeup.txt', 'w') as file:
        for animation in data.animations:
            for pose in animation.poses:
                file.write(f"In pose {pose.ID}:\n")
                for tile in pose.tiles:
                    file.write(f"{hex(tile.location)}\n")
                file.write("\n")


    
if __name__ == "__main__":
    main()