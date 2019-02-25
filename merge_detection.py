#Written by Artheau
#over several days in Feb. 2019
#while suffering from mild indigestion
#don't look through this code for too long or you will catch indigestion too
#that's how it works, right?

#TODO: Some supertile merging is disrupting frame drawing order (e.g. shoulderpad in 0xF2)


import json
import argparse
from itertools import chain

import util
from constants import *

data = None


def supertile_simplification():
    #go see who the consistent neighbors of each tile are
    identified_neighbors = make_identified_neighbors_list()

    #record your findings
    write_to_json(identified_neighbors)

    #brag
    print(f"Found {sum([len(group) - 1 for group in identified_neighbors])} tiles that can be removed by merging")


def make_identified_neighbors_list():
    all_locations_all_tiles_dict = {}
    for tile in util.global_tiles:
        all_locations_all_tiles_dict[tile] = get_all_tile_locations(tile)
    return find_neighbors(all_locations_all_tiles_dict)


def get_all_tile_locations(this_tile):
    #go looking through all the poses and figure out where this tile appears
    all_locations_dict = {}
    for (i,animation) in enumerate(data.animations):
        for (j,pose) in enumerate(animation.poses):
            location_list = locate_tile_in_pose(this_tile,pose)    #list of (ref_index,supertile_index)
            if location_list:
                all_locations_dict[(i,j)] = location_list
    return all_locations_dict

def find_neighbors(master_location_dict):
    neighbor_groups = []
    dict_keys = list(master_location_dict.keys()).copy()
    while dict_keys:
        tile1 = dict_keys.pop()
        this_neighbor_group = []
        for tile2 in dict_keys:
            if ratio_test(master_location_dict,tile1,tile2):    #see if these tiles even appear in the same proportions consistently
                relative_offset = get_relative_offset(master_location_dict,tile1,tile2)   #see if they appear in the same relation to each other
                if relative_offset:
                    this_neighbor_group.append((tile2,relative_offset))

        for (neighbor,_) in this_neighbor_group:     #these are definitely linked, so we don't need to check the other way around
            dict_keys.remove(neighbor)

        if this_neighbor_group:
            neighbor_groups.append([(tile1, (0,0))] + this_neighbor_group)

    return neighbor_groups



def locate_tile_in_pose(this_tile,pose):
    returnvalue = []
    for (i,tile_ref) in enumerate(pose.tiles):
        for (j,addr) in enumerate(tile_ref.real_tile.addresses):
            if addr == this_tile:
                returnvalue.append((i,j))
    return returnvalue

def ratio_test(master_location_dict,tile1,tile2):
    for location in chain(master_location_dict[tile1],master_location_dict[tile2]):
        if location not in master_location_dict[tile1] or location not in master_location_dict[tile2]:
            return False
        #conceivably there is a way later to do things like 2 of this tile for every 1 of another,
        # but this is outside the scope of the present push
        if len(master_location_dict[tile1][location]) != len(master_location_dict[tile2][location]):
            return False
        else:
            pass   #continue checking the other poses
    else:
        return True

def get_relative_offset(master_location_dict,tile1,tile2):
    offset_set = set()
    for location in master_location_dict[tile1]:
        this_offset = get_relative_offset_in_one_pose(location, master_location_dict[tile1][location],master_location_dict[tile2][location])
        if this_offset:
            offset_set.add(this_offset)
        else:
            return None
    if len(offset_set) == 1:
        return offset_set.pop()
    else:
        return None

def get_relative_offset_in_one_pose(location, tilelist_1, tilelist_2):
    possible_offset_list = []
    for tile1 in tilelist_1:
        this_offset_set = set()
        for tile2 in tilelist_2:
            new_offset = get_single_offset(location, tile1, tile2)
            if new_offset:
                this_offset_set.add(new_offset)
        possible_offset_list.append(set(this_offset_set))
    intersection = set.intersection(*possible_offset_list)

    if len(intersection) == 1:
        return intersection.pop()
    else:
        return None

def get_single_offset(location, tile1_index, tile2_index):
    (animation_no, pose_no) = location
    this_pose = data.animations[animation_no].poses[pose_no]
    (ref_no_1,addr_no_1) = tile1_index
    (ref_no_2,addr_no_2) = tile2_index

    tile1 = this_pose.tiles[ref_no_1]
    tile2 = this_pose.tiles[ref_no_2]

    offset1 = tile1.real_tile.offsets[addr_no_1]
    offset2 = tile2.real_tile.offsets[addr_no_2]

    if tile1.h_flip != tile2.h_flip or tile1.v_flip != tile2.v_flip:   #if flips don't match, bail now
        return None
    else:                    #else do the thing with the math  <-- shoutout to people who say "math" instead of "maths"
        x_distance = (tile2.x_offset - tile1.x_offset) * (-1 if tile1.h_flip else 1) + offset2[0] - offset1[0]
        y_distance = (tile2.y_offset - tile1.y_offset) * (-1 if tile1.v_flip else 1) + offset2[1] - offset1[1]
                                            
        return (x_distance,y_distance)
    
def write_to_json(bidirectional_neighbors):
    with open(SUPERTILE_JSON_FILENAME,"w") as file:
        json.dump(bidirectional_neighbors,file)
    with open(SUPERTILE_FRIENDLY_FILENAME,"w") as file:
        for group in bidirectional_neighbors:
            file.write("New Group:\n")
            for (addr,coord) in group:
                file.write("".join([hex(addr),": ",str(coord),"\n"]))
            file.write("\n\n")


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
    data = util.Samus(command_line_args[ROM_FILENAME_ARG_KEY],load_supertiles=False)

    supertile_simplification()
    
if __name__ == "__main__":
    main()