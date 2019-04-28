#This is the giant gambit for Super Metroid
#In total, this code is intended to take a ROM and modify it for wizzywig insertion

import itertools
import copy

SIGNATURE_ADDRESS_EXHIROM = None
SIGNATURE_ADDRESS_LOROM = None
SIGNATURE_MESSAGE = "ART WAS HERE 0000"

def upgrade_to_wizzywig(old_rom, samus):
    rom = copy.deepcopy(old_rom)  #for safety right now we are going to deepcopy the ROM, in case we need to bail

    #check to see if this rom has already been modified, in which case, we don't do anything.
    #TODO
    #SIGNATURE_ADDRESS_EXHIROM
    #SIGNATURE_ADDRESS_LOROM
    #SIGNATURE_MESSAGE

    if rom._type.name == "EXHIROM":
        pass    #if this is a SMaLttPR combo rom, then we're fine, because there's plenty of space in the low banks
    else:
        rom.expand(32)   #otherwise, we need to expand the rom to 4MB  (32 MBits)

    #previously, the upper tilemaps were loaded before the lower tilemaps, but the lower tiles were displayed before
    # the upper tiles.  This would not otherwise have caused problems, but the extent to which we are pushing this
    # old engine requires that we sometimes use larger DMA writes that overwrite (and obviate the need for) DMAs

    print("Swapping DMA load order...", end="")
    success_code = swap_DMA_order(rom,samus)
    print("done" if success_code else "FAIL")

    #to break symmetry, we will need to rearrange where the gun port tile data is,
    # and correspondingly make sure that it is loaded correctly during DMA
    #Thankfully, there's plenty of room in ROM because they were
    # super super wasteful with the organization in this part.

    print("Moving gun tiles...", end="")
    success_code = move_gun_tiles(rom,samus)
    print("done" if success_code else "FAIL")

    #I can see how it was a good idea at the time to put the cannon port as tile $1F,
    # but this is also limiting (because it limits us to 31 tiles instead of 32).
    # Since now that we know in retrospect that the person
    # who was in charge of the Mode 7 section was not greedy with the tile space,
    # we can move the gun port over to tile $DF which is unused throughout the game
    #While we're in there, we should remove the mirroring effects on the tiles,
    # since that is no longer necessary given the symmetry fix from move_gun_tiles()

    print("Re-assigning gun tilemaps...", end="")
    success_code = reassign_gun_tilemaps(rom,samus)
    print("done" if success_code else "FAIL")

    #write all the new graphics data from base images and layout information
    print("Writing new image data...", end="")
    DMA_dict, success_code = write_dma_data(rom,samus)
    print("done" if success_code else "FAIL")

    #maximally expand/relocate the existing DMA tables, and then add the new load data into them
    print("Writing new DMA tables...", end="")
    DMA_upper_table_indices, DMA_lower_table_indices, success_code = write_new_DMA_tables(DMA_dict,rom,samus)
    print("done" if success_code else "FAIL")

    #update the table/index references to these new DMA tables
    print("Linking new tables to animations...", end="")
    success_code = link_tables_to_animations(DMA_upper_table_indices, DMA_lower_table_indices, rom,samus)
    print("done" if success_code else "FAIL")

    #write and link all the new tilemaps (use a pointer to nullmap instead of $0000 since $0000 lags the game because reasons) using the layout info
    print("Assigning new tilemaps...", end="")
    success_code = assign_new_tilemaps(rom,samus)
    print("done" if success_code else "FAIL")

    #connect the death animation correctly
    print("Re-connecting death sequence...", end="")
    success_code = connect_death_sequence(DMA_dict,rom,samus)
    print("done" if success_code else "FAIL")

    #get rid of the stupid tile
    print("Stupid tile...", end="")
    success_code = no_more_stupid(rom,samus)
    print("stupid" if success_code else "FAIL")
    
    #because a DMA of zero bytes is essentially a guaranteed game crash, the designers had to make separate subroutines
    # that made the upper tilemap not display in certain cases.  These subroutines are no longer necessary, because we
    # fixed the issue in the DMA swap order code, and so now we need to get rid of the subroutines because they break
    # a few animations in the form that they now exist

    print("Disabling upper half bypass routine...", end="")
    success_code = disable_upper_bypass(rom,samus)
    print("done" if success_code else "FAIL")

    #now we're going to get set up for screw attack without space jump
    #first off, we need a new control code that checks for space jump, so that we can gate the animation appropriately

    print("Creating new control code...", end="")
    success_code = create_new_control_code(rom,samus)
    print("done" if success_code else "FAIL")

    #now we need to insert this control code into the animation sequence for screw attack, and its counterpart in walljump

    print("Implementing spin attack...", end="")
    success_code = implement_spin_attack(rom,samus)
    print("done" if success_code else "FAIL")


    #TODO
    #
    #write the death animation DMA data in a space worthy of its importance in my personal gameplay
    #move the DMA pointers accordingly, and increase the DMA load size
    #re-write the death tilemaps from layout info
    #
    #check to see how the organization of bank $92 is coming along at this point,
    # and try to keep things confined to their original spaces if possible,
    # so that this patch is more robust to other types of rom hacks
    #
    #as a separate project, need to fix all the gun placements (do this in the base rom patch)



    #pee on the tree
    #TODO
    #SIGNATURE_ADDRESS_EXHIROM
    #SIGNATURE_ADDRESS_LOROM
    #SIGNATURE_MESSAGE

    #now GET OUT
    return rom



def swap_DMA_order(rom,samus):
    success_code = True
    #The sum total of this function is to effectively swap the commands in the range $809382-$8093CA with the commands
    # in the range $8093CB-$809413.  Mostly, these commands are identical, except for the following changes:
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x809382, [0xAC,0x1D,0x07], [0xAC,0x1E,0x07], "111")
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x809389, [0xAD,0x1F,0x07], [0xAD,0x21,0x07], "111")
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x80938E, [0xA9,0x00,0x60], [0xA9,0x80,0x60], "111")
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093B6, [0xA9,0x00,0x61], [0xA9,0x80,0x61], "111")
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093CB, [0xAC,0x1E,0x07], [0xAC,0x1D,0x07], "111")
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093D2, [0xAD,0x21,0x07], [0xAD,0x1F,0x07], "111")
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093D7, [0xA9,0x80,0x60], [0xA9,0x00,0x60], "111")
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093FF, [0xA9,0x80,0x61], [0xA9,0x00,0x61], "111")

    return success_code

def move_gun_tiles(rom,samus):
    #move the actual tile data
    # Probably the easiest place to locate this is somewhere in $9A9A00-$9AB200, since that's where they lived before
    PLACE_TO_PUT_GUN_TILES = 0x9A9A00
    # there was already a bunch of blank tile space there, so this seems like a good repurposing of the local space
    for direction in range(10):   #there are ten directions for every port
        for level in range(3):    #and there are three levels of gun port opening
            reference_number = direction+level*10  #this matches up reversibly with the code in samus.get_sprite_pose()
            name_of_gun_image = samus._layout.get_image_name("gun", reference_number)
            raw_tile = samus.get_raw_pose(name_of_gun_image)   #go get the gun image from the ZSPR
            rom.bulk_write_to_snes_address(PLACE_TO_PUT_GUN_TILES+0x20*reference_number,raw_tile,0x20)  #just line 'em up.  Nothing fancy.

    #move the DMA pointers
    # at $90C7A5
    # there are pointers DW VUR_GFX, AUR_GFX, HR_GFX, ADR_GFX, VDR_GFX, VDL_GFX, ADL_GFX, HL_GFX, AUL_GFX, VUL_GFX (direction based)
    # they point to DMA locations in bank $9A, e.g. DW $0000, $9A00, $9C00, $9E00
    #I need a place with room, preferably in bank $90, for a few more pointers to accomodate all ten directions,
    # so that I can have ten pointers to ten different DMA sets of this type
    #It just so happens that I'm going to free up $9086A3-$9087BC with some other changes that I'm making, so hooray!
    PLACE_TO_PUT_GUN_DMA_POINTERS = 0x9086A3      #otherwise, if this is a problem, can default to the end of the bank
    for direction in range(10):
        gfx_pointer = PLACE_TO_PUT_GUN_DMA_POINTERS+8*direction
        rom.write_to_snes_address(0x90C7A5+2*direction, gfx_pointer % 0x10000, 2)
        rom.write_to_snes_address(gfx_pointer, 0x0000, 2)   #first gun pointer is always null in the vanilla ROM -- let's just keep doing that
        for level in range(3):
            reference_number = direction+level*10
            rom.write_to_snes_address(gfx_pointer+2*(1+level), (PLACE_TO_PUT_GUN_TILES+0x20*reference_number) % 0x10000, 2)

    return True

def reassign_gun_tilemaps(rom,samus):
    TILE = 0xDF   #the new location for the gun tile
    PAL = 0x28   #unmirrored palette code
    success_codes = []

    #first, need to make sure the tile data is loaded into the new location during DMA loads
    OLD_LOC = 0x61F0                 #this is 0x6000 + 0x10*old_index, where old_index = 0x1F
    NEW_LOC = 0x6000 + (0x10*TILE)   #e.g. for tile index 0xDF, this is 0x6DF0
    success_codes.append(  rom._apply_single_fix_to_snes_address(0x90C786, OLD_LOC, NEW_LOC, 2)  )

    #now, need to update the tilemaps to reference the new location.  Also, no more mirroring because we fixed that in the source tiles
    OLD_DATA = [0x1F, 0x28, 0x1F, 0x28, 0x1F, 0x28, 0x1F, 0x68, 0x1F, 0xA8, 0x1F, 0xE8, 0x1F, 0x28, 0x1F, 0x68, 0x1F, 0x68, 0x1F, 0x68]
    NEW_DATA = [TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL ]
    success_codes.append(  rom._apply_single_fix_to_snes_address(0x90C791, OLD_DATA, NEW_DATA, "1"*len(OLD_DATA))  )
    
    return all(success_codes)

#TODO: factor this out to RomHandler
class FreeSpace():
    def __init__(self, mem_blocks):
        #expects mem_blocks as a list of tuples of form (start_mem_address, end_mem_address), last address is not inclusive
        self.mem_blocks = mem_blocks
        self.current_block = 0
        self.offset = 0

    def get(self, size):
        if self.mem_blocks[self.current_block][0] + self.offset + size <= self.mem_blocks[self.current_block][1]:
            free_location = self.mem_blocks[self.current_block][0] + self.offset
            self.offset += size
            return free_location
        else:  #go to the next block and try again
            self.current_block += 1
            if self.current_block < len(self.mem_blocks):
                self.offset = 0
                return self.get(size)
            else:
                raise AssertionError("ran out of memory to allocate")

def write_dma_data(rom,samus):
    if rom._type.name == "EXHIROM":
        #until my hand is slapped I am going to just take up all of the lower halves of banks 0x44-0x4B and 0x54-0x5B
        freespace = FreeSpace([(bank * 0x10000,bank * 0x10000 + 0x8000) for bank in itertools.chain(range(0x44,0x4C),range(0x54,0x5B))])
        #the death DMA data needs to all be in the same bank
        death_freespace = FreeSpace([(0x5B0000,0x5B8000)])
    else:
        #in this case, the only person that will slap my hand is me, and I'm not feeling it at the moment
        #so we're just going to take up the upper halves of half of the new banks that we just added (0xE8-0xF7)
        freespace = FreeSpace([(bank * 0x10000 + 0x8000,bank * 0x10000 + 0x10000) for bank in range(0xE8,0xF7)])
        #the death DMA data needs to all be in the same bank
        death_freespace = FreeSpace([(0xF78000, 0xF80000)])

    DMA_dict = {}  #have to keep track of where we put all this stuff so that we can point to it afterwards

    for image_name in samus._layout.data["images"]:
        if image_name[:6] in ["palett","file_s","gun_po"]:  #these are special cases which will go in other parts of memory
            pass
        else:
            force = samus._layout.get_property("import", image_name)
            if force:
                if force.lower() == "upper":
                    DMA_data = samus.get_raw_pose(image_name, lower=False)
                elif force.lower() == "lower":
                    DMA_data = samus.get_raw_pose(image_name, upper=False)
                else:
                    raise AssertionError(f"received call to force a half import for pose {image_name}, but did not understand command '{force}'")
            else:
                DMA_data = samus.get_raw_pose(image_name)

            size = len(DMA_data)
            if image_name[:5] in ["death"]:
                address_to_write = death_freespace.get(size)
            else:
                address_to_write = freespace.get(size)

            rom.bulk_write_to_snes_address(address_to_write,DMA_data,size)

            DMA_dict[image_name] = (address_to_write, size)

    print(hex(death_freespace.get(0)))

    return DMA_dict, True

def write_new_DMA_tables(DMA_dict,rom,samus):
    #We'll need more room, since we have 637 unique images*7 bytes each = 0x116B amount of stuff (used 0x0BE5 previously)
    #for this, we're going to eat into some area that used to be reserved for death tilemaps ($92C580-$92CBED)
    # because we know we have to change those tilemaps later anyway

    #the lookup for the tables themselves are at 92:D91E (upper)
    #$92:D91E             dw CBEE, CCCE, CDA0, CE80, CEF7, CF6E, CFE5, D05C, D0E8, D12E, D613, D6A6, D74E
    #and at 92:D938 (lower)
    #$92:D938             dw D19E, D27E, D35E, D6D7, D406, D4A7, D54F, D786, D5F0, D79B, D605
    
    #freespace is from death tilemap region up through the usual DMA table region
    UPPER_LOC = 0x92C580
    LOWER_LOC = 0x92D600
    success_code = rom._apply_single_fix_to_snes_address(0x92D91E,
        [0xCBEE, 0xCCCE, 0xCDA0, 0xCE80, 0xCEF7, 0xCF6E, 0xCFE5, 0xD05C, 0xD0E8, 0xD12E, 0xD613, 0xD6A6, 0xD74E,  #old upper table
         0xD19E, 0xD27E, 0xD35E, 0xD6D7, 0xD406, 0xD4A7, 0xD54F, 0xD786, 0xD5F0, 0xD79B, 0xD605],  #old lower table
        [UPPER_LOC % 0x10000 for _ in range(13)] + \
        [LOWER_LOC % 0x10000 for _ in range(11)],     #new upper table is a failsafe in case of vanilla glitches, new lower table is intentionally simplified
          "2"*24)   #these are 24 big endian values to write
    freespace_upper = FreeSpace([(UPPER_LOC,LOWER_LOC)])
    freespace_lower = FreeSpace([(LOWER_LOC,0x92D7D2)])

    lower_table_fill = 0
    upper_table_fill = 0
    upper_table_number = 0
    DMA_upper_table_indices = {}
    DMA_lower_table_indices = {}
    for image_name,(image_location,size) in DMA_dict.items():
        if samus._layout.get_property("force",image_name) == "lower":   #here we actually want to force to the lower half
            address_to_write = freespace_lower.get(7)
            DMA_lower_table_indices[image_name] = (0,lower_table_fill)
            lower_table_fill += 1
        else:                                         #by default, force this to upper
            address_to_write = freespace_upper.get(7)
            if upper_table_fill > 0x30:  #when they get too full, make a new table (here 0x30 is fairly arbitrary)
                upper_table_number += 1
                upper_table_fill = 0
                rom.write_to_snes_address(0x92D91E+2*upper_table_number,address_to_write % 0x10000,2)  #index the new table
            DMA_upper_table_indices[image_name] = (upper_table_number,upper_table_fill)
            upper_table_fill += 1
        
        bottom_row_size = 0x20*(size//0x40)   #half of the tiles, floored (by the way we constructed the images originally)
        top_row_size = size - bottom_row_size

        rom.write_to_snes_address(address_to_write,[image_location,top_row_size,bottom_row_size],"322")

    #write the null images -- these are important because very few poses will have a strictly lower section anymore
    #lazily I am just going to let it point to the last true image location, but with a load size of 1.
    #SUPER IMPORTANT -- do NOT set these to load zero data.  DO NOT.
    #Because DMAing zero data actually means load 0x10000 data, and you will crash your game hard
    address_to_write = freespace_lower.get(7)
    rom.write_to_snes_address(address_to_write,[image_location,1,1],"322")
    DMA_lower_table_indices["null"] = (0,lower_table_fill)
    address_to_write = freespace_upper.get(7)
    rom.write_to_snes_address(address_to_write,[image_location,1,1],"322")
    DMA_upper_table_indices["null"] = (upper_table_number,upper_table_fill)

    return DMA_upper_table_indices, DMA_lower_table_indices, success_code

def link_tables_to_animations(DMA_upper_table_indices, DMA_lower_table_indices, rom,samus):
    #Here is the deal at this point -- at $92D94E there is a big table with exactly one pointer for every animation
    #ORG $92D94E        #DW AFP_T00, AFP_T01, AFP_T02, AFP_T03, ...
    #and then immediately following that is a big long list of 4 byte tuples, essentially
    #that correspond to (upper_table, upper_index, lower_table, lower_index)
    #so we need to populate this now, and might also expand the big long list
    #but if we do, we need to work OVER some code that might have something to do with loading from save points/fanfare related
    #and this code is at $92ED24-$EDF3
    #but after that, we have all the free space that we could want, right up to the end of the bank, if we so desired.
    freespace = FreeSpace([(0x92DB48,0x92ED24),(0x92EDF4,0x930000)])

    #as a failsafe against vanilla glitches, let's start by setting all the pointers to a null list
    NULL_SIZE = 0x40
    address_to_write = freespace.get(NULL_SIZE*4)   #going to fill the null list with the largest number of poses possible in an animation
    null_entries = [DMA_upper_table_indices["null"][0],
                    DMA_upper_table_indices["null"][1],
                    DMA_lower_table_indices["null"][0],
                    DMA_lower_table_indices["null"][1]]
    rom.write_to_snes_address(address_to_write,NULL_SIZE*null_entries, "1"*(4*NULL_SIZE))
    #now assign all the pointers to the null list
    rom.write_to_snes_address(0x92D94E,[address_to_write % 0x10000 for _ in range(0xFD)],"2"*0xFD)

    animation_lookup = {}   #will contain a list of the poses each animation has
    for animation, pose in get_numbered_poses_old_and_new(rom,samus):
        if animation in animation_lookup:
            animation_lookup[animation].append(pose)
        else:
            animation_lookup[animation] = [pose]

    for animation,pose_list in animation_lookup.items():   #the "used" animations
        max_pose = max(pose_list)+1   #+1 because zero index is a thing
        base_address = freespace.get(max_pose*4)   #allocate memory
        rom.write_to_snes_address(0x92D94E+2*animation, base_address % 0x10000, 2)  #set the pointer to this new stuff
        for pose in range(max_pose):
            if pose in pose_list:
                image_names = samus._layout.get_all_image_names(animation,pose)
                image_entries = null_entries.copy()   #default to null entries, unless there is image data here
                for image_name in image_names:
                    if image_name in DMA_upper_table_indices:
                        image_entries[0] = DMA_upper_table_indices[image_name][0]
                        image_entries[1] = DMA_upper_table_indices[image_name][1]
                    elif image_name in DMA_lower_table_indices:
                        image_entries[2] = DMA_lower_table_indices[image_name][0]
                        image_entries[3] = DMA_lower_table_indices[image_name][1]
                rom.write_to_snes_address(base_address+4*pose, image_entries,"1111")    #assign
            else:
                rom.write_to_snes_address(base_address+4*pose, null_entries, "1111")  #assign null tables

    return True

def assign_new_tilemaps(rom,samus):
    #my note to myself from early on in this process:
    #  The game stalls badly if there is a tilemap missing.  Don't use $0000 for missing tilemaps like in vanilla.
    #
    #Ok, so the offsets to the upper tilemaps are stored at $929263 in a table indexed by 2*animation number
    # Use that offset*2 + $92808D to get the list of pointers to the pose tilemaps (in bank $92)
    # These are the pointers that we need to change, so that they point at our new tilemaps
    #lower offsets are the same except start at $92945D

    #this was the old table full of TM pointers.  We navigate around the delicate areas and rearrange the remaining tilemap pointers
    lookup_table_freespace = FreeSpace([(0x928091,0x928390),(0x9283C1,0x9283E4),(0x9283e7,0x928a04),(0x928a0d,0x9290c4)])
    #leaving TM_006 alone because its auxiliary uses in-game are not clear, but the rest can go
    tilemap_freespace = FreeSpace([(0x929663,0x92BE00)])   #this used to contain all the tilemaps, and again it will!
    #reserving the space after $92BE00 for death tilemaps

    #need a null map to prevent terrible lag parties from happening when vanilla glitches rear their head
    null_map_location = tilemap_freespace.get(2)
    rom.write_to_snes_address(null_map_location, 0, 2)   #write zero to state that there are zero tiles mapped here

    #need a dumping ground for null maps if lower is not forced
    null_list_address = lookup_table_freespace.get(2*96)  #96 is the most poses of any animation

    animation_lookup = {}   #will contain a list of the poses each animation has
    for animation, pose in get_numbered_poses_old_and_new(rom,samus):
        if animation in animation_lookup:
            animation_lookup[animation].append(pose)
        else:
            animation_lookup[animation] = [pose]

    master_tilemap_location_dict = {}

    for animation,pose_list in animation_lookup.items():
        max_pose = max(pose_list)+1   #+1 because zero index is a thing

        #comb through first and see if we need a unique lower tilemap set
        need_lower_tilemaps = False
        for pose in range(max_pose):
            if pose in pose_list:
                for image_name in samus._layout.get_all_image_names(animation,pose):
                    if samus._layout.get_property("force", image_name) == "lower":
                        need_lower_tilemaps = True

        #need to make up lookup table pointers
        upper_list_address = lookup_table_freespace.get(2*max_pose)
        rom.write_to_snes_address(0x929263+2*animation,(upper_list_address-0x92808D)//2 ,2)
        if need_lower_tilemaps:
            lower_list_address = lookup_table_freespace.get(2*max_pose)
            rom.write_to_snes_address(0x92945D+2*animation,(lower_list_address-0x92808D)//2 ,2)
        else:
            lower_list_address = null_list_address
            rom.write_to_snes_address(0x92945D+2*animation,(null_list_address-0x92808D)//2 ,2)

        for pose in range(max_pose):
            if pose in pose_list:
                #default to null map
                rom.write_to_snes_address(upper_list_address+2*pose, null_map_location % 0x10000, 2)
                rom.write_to_snes_address(lower_list_address+2*pose, null_map_location % 0x10000, 2)

                image_names = samus._layout.get_all_image_names(animation,pose)
                for image_name in image_names:
                    force = samus._layout.get_property("force", image_name)
                    dimensions = samus._layout.get_property("dimensions", image_name)
                    extra_area = samus._layout.get_property("extra area", image_name)
                    palette = samus._layout.get_property("palette", image_name)
                    tilemap = get_tilemap_from_dimensions(dimensions, extra_area, palette, 0x08 if force=="lower" else 0x00)
                    if image_name[:14] == "crystal_bubble":
                        #have to make the huge bubble out of just a quarter bubble
                        tilemap = get_quadrated_tilemap(tilemap)
                    elif animation == 0xB2 and pose in itertools.chain(range(0,9),range(25,41),range(57,64)):  #0-8,25-40,57-63
                        #need to 180 rotate these grapple poses so that they appears as they did in classic for upside-down poses
                        tilemap = rotate_tilemap(tilemap)
                    elif animation == 0xB3 and pose in itertools.chain(range(0,8),range(24,40),range(56,64)):  #0-7,24-39,56-63
                        #need to 180 rotate these grapple poses so that they appears as they did in classic for upside-down poses
                        tilemap = rotate_tilemap(tilemap)

                    if tuple(tilemap) in master_tilemap_location_dict:
                        tilemap_location = master_tilemap_location_dict[tuple(tilemap)]
                    else:
                        tilemap_location = tilemap_freespace.get(len(tilemap)+2)
                        rom.write_to_snes_address(tilemap_location, len(tilemap)//5, 2)  #write how many tiles are mapped
                        rom.bulk_write_to_snes_address(tilemap_location+2, tilemap, len(tilemap))  #and then the maps
                        master_tilemap_location_dict[tuple(tilemap)] = tilemap_location
                    #see if this has to go in the lower tilemap, and if so, do that
                    if force == "lower":
                        rom.write_to_snes_address(lower_list_address+2*pose, tilemap_location % 0x10000, 2)
                    else:
                        rom.write_to_snes_address(upper_list_address+2*pose, tilemap_location % 0x10000, 2)
            else:
                rom.write_to_snes_address(upper_list_address+2*pose, null_map_location % 0x10000, 2)
                rom.write_to_snes_address(lower_list_address+2*pose, null_map_location % 0x10000, 2)

    return True

def connect_death_sequence(DMA_dict, rom,samus):
    #the death tilemaps are referenced by these offsets
    #$92:EDCF A9 1C 08    LDA #$081C                  ;this is an offset into the lower tilemap table for right facing death tilemaps
    #$92:EDDA A9 25 08    LDA #$0825                  ;this is an offset into the lower tilemap table for left facing death tilemaps
    #to dereference them, go to $92808D+2*offset
    #there you will find a list of the tilemaps for the death pose (9 in total for each side)
    #in this code we change those offsets

    freespace = FreeSpace([(0x92BE01,0x92C580)])   #starts where the other tilemaps end.
    #Needs to start on an odd number in order to index correctly from 0x92808D

    for direction,base_address in [("left",0x92EDD0),("right",0x92EDDB)]:
        death_list_location = freespace.get(18)
        rom.write_to_snes_address(base_address,(death_list_location-0x92808D)//2 ,2)
        for i in range(9):
            tilemap = []
            for image_name in samus._layout.reverse_lookup[f"death_{direction}",i]:
                force = samus._layout.get_property("force", image_name)
                dimensions = samus._layout.get_property("dimensions", image_name)
                extra_area = samus._layout.get_property("extra area", image_name)
                palette = samus._layout.get_property("palette", image_name)
                if force == "lower":
                    #prepend, so that the lower tilemaps are at the beginning of the list (and thus, get drawn first)
                    tilemap.extend(get_tilemap_from_dimensions(dimensions, extra_area, palette, 0x08))
                else:
                    #extend, so that the upper tilemaps are at the end of the list (and thus, get drawn last)
                    tilemap = get_tilemap_from_dimensions(dimensions, extra_area, palette, 0x00) + tilemap

            tilemap_location = freespace.get(len(tilemap)+2)
            rom.write_to_snes_address(tilemap_location, len(tilemap)//5, 2)  #write how many tiles are mapped
            rom.bulk_write_to_snes_address(tilemap_location+2, tilemap, len(tilemap))  #and then the maps

            #tie it into the list now
            rom.write_to_snes_address(death_list_location+2*i, tilemap_location % 0x10000, 2)

    #the old death DMA routine is wildly insufficient; we need to bypass it (replace with NOP commands)
    #$9B:B451 20 D8 B6    JSR $B6D8
    #$9B:B5B1 20 D8 B6    JSR $B6D8
    for addr in [0x9BB451,0x9BB5B1]:
        rom._apply_single_fix_to_snes_address(addr,[0x20,0xD8,0xB6], [0xEA,0xEA,0xEA],"111")


    #and because we bypassed it, we need a new subroutine!  Eek!  So let's give it a good college try
    '''
    ; hook this in as a JSR from $92:EDC4
    18           CLC
    AD E4 0D     LDA $0DE4    ;get the pose number
    0A           ASL A
    0A           ASL A
    0A           ASL A
    AD 1E 0A     ADC $0A1E    ;add the direction that Samus is facing
    29 FF 00     AND #$00FF   ;just the lower nybble of direction
    0A           ASL A
    A8           TAY          ;Y = 16*pose # + [8 (left) or 16 (right)]
    :loop
    88           DEY
    88           DEY
    AE 30 03     LDX $0330     ;get VRAM stack pointer
    A9 00 04     LDA #$0400   ;all DMA transfers will be 20 tiles each
    95 D0        STA $D0, x
    E8           INX
    E8           INX
    B9 ?? ??     LDA source_list, y    ;get the next DMA source address
    95 D0        STA $D0, x
    E8           INX
    E8           INX
    A9 ?? 00     LDA #bank   ;bank #
    95 D0        STA $D0, x
    E8           INX          ;intentionally shifting by only one here
    B9 ?? ??     LDA dest_list, y ;get the dest address
    95 D0        STA $D0, x
    E8           INX
    E8           INX
    8E 30 03     STX $330     ;replace stack pointer
    98           TYA
    89 07 00     BIT #$0007      ;see if we finished the pose
    D0 D8        BNE loop
    AD 1E 0A     LDA $0A1E       ;get the direction samus is facing
    29 FF 00     AND #$00FF
    60           RTS


    :source_list
    dw ??...??  ;9*[LEFT RIGHT] where each of LEFT/RIGHT is 4 pointers to DMA sources for that pose
    :dest_list
    dw ??...??  ;18*[6000, 6200, 6400, 6600]
    '''

    base_address = 0x92F600     #I'm not sure why I liked this particular address.  Maybe because probably no one else would use it?
    SUB_LEN = 63  #subroutine length
    source_list_addr = base_address + SUB_LEN
    dest_list_addr = source_list_addr + 144
    DMA_bank = DMA_dict["death_right"][0] // 0x10000

    NEW_SUBROUTINE = [0x18,0xAD,0xE4,0x0D,
                      0x0A,0x0A,0x0A,0xAD,0x1E,0x0A,0x29,0xFF,
                      0x00,0x0A,0xA8,0x88,0x88,0xAE,0x30,0x03,0xA9,0x00,
                      0x04,0x95,0xD0,0xE8,0xE8,0xB9,source_list_addr & 0xFF,(source_list_addr & 0xFF00)//0x100,
                      0x95,0xD0,0xE8,0xE8,0xA9,DMA_bank,0x00,0x95,
                      0xD0,0xE8,0xB9,dest_list_addr & 0xFF,(dest_list_addr & 0xFF00)//0x100,0x95,0xD0,0xE8,
                      0xE8,0x8E,0x30,0x03,0x98,0x89,0x07,0x00,
                      0xD0,0xD8,0xAD,0x1E,0x0A,0x29,0xFF,0x00,
                      0x60]

    success_code = rom._apply_single_fix_to_snes_address(base_address, SUB_LEN*[0xFF], NEW_SUBROUTINE,"1"*SUB_LEN)

    DMA_locations = []
    for i in range(9):
        for direction in ["left", "right"]:
            image_names = samus._layout.reverse_lookup[(f"death_{direction}",i)]
            body_names = [name for name in image_names if samus._layout.get_property("force",name) == "lower"]
            piece_names = [name for name in image_names if samus._layout.get_property("force",name) == "upper"]
            if body_names:
                body_loc = DMA_dict[body_names[0]][0]  % 0x10000
            else:
                key = next(iter(DMA_dict.keys()))
                body_loc = DMA_dict[key][0] % 0x10000  #not all death poses have "bodies", so we need a default memory address (to anywhere valid)
            if piece_names:
                pieces_loc = DMA_dict[piece_names[0]][0]  % 0x10000
            else:
                key = next(iter(DMA_dict.keys()))
                pieces_loc = DMA_dict[key][0] % 0x10000     #not all death poses have "pieces", so we need a default memory address (to anywhere valid)
                
            DMA_locations.extend([body_loc,pieces_loc,pieces_loc+0x0400,pieces_loc+0x0800])

    success_code = success_code and rom._apply_single_fix_to_snes_address(source_list_addr, 72*[0xFFFF], DMA_locations,"2"*72)
    success_code = success_code and rom._apply_single_fix_to_snes_address(dest_list_addr, 72*[0xFFFF], 18*[0x6000,0x6200,0x6400,0x6600],"2"*72)

    #hook it in
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x92EDC4,[0xAD,0x0A1E,0x29,0xFF,0x00],
                                                                                   [0x20, base_address % 0x10000,0xEA,0xEA,0xEA],"12111")

    return success_code

def get_tilemap_from_dimensions(dimensions, extra_area, palette, start_index=0x00):
    if palette is None:
        palette = 0x28   #default to normal Samus palette
    elif type(palette) is str and palette[:2] == "0x":
        palette = int(palette[2:],16)
    else:
        raise AssertionError(f"Did not recognize palette hex code {palette} in get_tilemap_from_dimensions()")

    big_tiles = []
    small_tiles = []
    for bounding_box in itertools.chain([dimensions],extra_area if extra_area else []):
        xmin,xmax,ymin,ymax = bounding_box
        x_chad = ((xmax-xmin) % 16) != 0   #True if there is a small tile hanging over in the x direction, False else
        y_chad = ((ymax-ymin) % 16) != 0   #True if there is a small tile hanging over in the y direction, False else
        for y in range(ymin,ymax-15,16):
            for x in range(xmin,xmax-15,16):
                big_tiles.append((x,y))
            if x_chad:
                small_tiles.append((xmax-8,y  ))
                small_tiles.append((xmax-8,y+8))
        if y_chad:
            for x in range(xmin,xmax-7,8):
                small_tiles.append((x,ymax-8))

    tilemap = []
    current_index = start_index
    for x,y in big_tiles:
        if x < 0:
            tilemap.extend([x % 0x100,0xC3, y % 0x100,current_index, palette])
        else:
            tilemap.extend([x % 0x100,0xC2, y % 0x100,current_index, palette])
        current_index += 0x02
    for x,y in small_tiles:
        if x < 0:
            tilemap.extend([x % 0x100,0x01, y % 0x100,current_index, palette])
        else:
            tilemap.extend([x % 0x100,0x00, y % 0x100,current_index, palette])
        if current_index//0x10 == 0:
            current_index += 0x10
        else:
            current_index -= 0x0F   #subtract 0x10 and add 0x01

    return tilemap

def get_quadrated_tilemap(tilemap):
    #takes the tilemap and quads it out by mirroring in all four possible manners
    #right now, this is implemented in a way that is specific to the crystal flash bubble only
    quad_tilemap = []
    for h_flip, v_flip in itertools.product([True,False],repeat=2):
        for i in range(0,len(tilemap),5):
            x,size,y,tile,palette = tilemap[i:i+5]
            if h_flip:
                x = 0xF0 - x
                size ^= 0x01     #flip the x sign bit
                palette ^= 0x40
            if v_flip:
                y = 0xF0 - y
                palette ^= 0x80
            if x < 0:
                x += 0x100
                size ^= 0x01
            if y < 0:
                y += 0x100
            quad_tilemap.extend([x,size,y,tile,palette])
    return quad_tilemap

def rotate_tilemap(tilemap):
    rotated_tilemap = []
    for i in range(0,len(tilemap),5):
        x,size,y,tile,palette = tilemap[i:i+5]
        if size & 0xC2 == 0:   #small tile
            flip_anchor = 0xF8  #math
        else:
            flip_anchor = 0xF0  #more math.  Learn algebra, kids; you'll need it at 4pm on a Thursday in April.
        x = flip_anchor - x
        y = flip_anchor - y
        size ^= 0x01
        palette ^= 0xC0
        if x < 0:
            x += 0x100     #hex stuff, happens when x is negative but close to zero
            size ^= 0x01   #more hex stuff.  Learn hexadecimal, kids; you'll need it at 4:15pm on a Thursday in April.
        if y < 0:
            y += 0x100
        rotated_tilemap.extend([x,size,y,tile,palette])
    return rotated_tilemap

def no_more_stupid(rom,samus):
    #in theory, I could just break the code that loads the stupid tile, but I won't rest at night until this tile is gone
    rom.bulk_write_to_snes_address(0x9AD620, [0 for _ in range(0x20)], 0x20)
    #somehow I have the feeling that it's going to come back for me,
    # chasing me down while giving an endless monologue on the health benefits of kombucha
    return True

def disable_upper_bypass(rom,samus):
    #so if you DMA zero bytes, you actually DMA an entire bank.  And trying to DMA an entire bank into the middle of VRAM
    # is super bad news.  But this also means that there's not a simple way to avoid DMA -- you have to write a bypass
    # routine.  This bypass routine served its purpose in the original game but now we've made improvements to the engine
    # and this routine is actually getting in our way.
    OLD_SUBROUTINES = [0x868D, 0x8686, 0x8686, 0x86C6, 0x8688, 0x8686, 0x8686, 0x8688,
                       0x8688, 0x8688, 0x86EE, 0x8686, 0x8686, 0x874C, 0x8686, 0x870C,
                       0x8686, 0x8688, 0x8688, 0x8688, 0x8768, 0x8686, 0x8686, 0x8686,
                       0x8686, 0x877C, 0x8686, 0x8790]
    NEW_SUBROUTINES = [0x8686 for _ in range(28)]   #these are just null routines
    success_code = rom._apply_single_fix_to_snes_address(0x90864E, OLD_SUBROUTINES, NEW_SUBROUTINES, "2"*28)
    return success_code

def create_new_control_code(rom,samus):
    #new control code: place at $908688-$9086A2 (0x1B bytes)
    SUBROUTINE_LOCATION = 0x908688
    '''
    ;I wrot this coed mysef
    AD A2 09   ;LDA $09A2       ;get item equipped info
    89 00 02   ;BIT #$0200      ;check for space jump equipped
    D0 09      ;BNE space_jump  ;if space jump, branch to space jump stuff
    AD 96 0A   ;LDA $0A96       ;get the pose number
    18         ;CLC             ;prepare to do math
    69 1B 00   ;ADC #$001B      ;skip past the old screw attack to the new stuff
    80 04      ;BRA get_out     ;then GET OUT after doing some important things after branching
    ;:space_jump
    AD 96 0A   ;LDA $0A96       ;get the pose number
    1A         ;INC A           ;just go to the next pose
    ;:get_out
    8D 96 0A   ;STA $0A96       ;store the new pose in the correct spot
    A8         ;TAY             ;transfer to Y because reasons
    38         ;SEC             ;flag the carry bit because reasons
    60         ;RTS             ;now GET OUT
    '''
    NEW_SUBROUTINE = [  0xAD, 0xA2, 0x09,
                        0x89, 0x00, 0x02,
                        0xD0, 0x09,
                        0xAD, 0x96, 0x0A,
                        0x18,
                        0x69, 0x1B, 0x00,
                        0x80, 0x04,
                        0xAD, 0x96, 0x0A,
                        0x1A,
                        0x8D, 0x96, 0x0A,
                        0xA8,
                        0x38,
                        0x60]

    rom.bulk_write_to_snes_address(SUBROUTINE_LOCATION, NEW_SUBROUTINE, 0x1B)

    #need to link up this subroutine to control code $F5
    success_code = rom._apply_single_fix_to_snes_address(0x90832E, 0x8344, SUBROUTINE_LOCATION % 0x10000, 2)

    #we're going to tie in the $F5 code to run right after the normal code in $FB.
    #"Waste not want not", as people imitating my mom used to say
    #In particular, here:
    '''
    OLD CODE
    $90:8482 69 15 00    ADC #$0015
    $90:8485 8D 96 0A    STA $0A96
    $90:8488 A8          TAY
    $90:8489 38          SEC
    $90:848A 60          RTS
    '''
    #the F5 control code adds 1 if space jump is equipeed, else adds 27.  Technically we want to add 0 or 26, so we do this:
    '''
    NEW CODE
    $90:8482 69 14 00    ADC #$0014
    $90:8485 8D 96 0A    STA $0A96
    $90:8488 4C ?? ??    JMP SUBROUTINE_LOCATION
    '''
    #because we're jumping straight-up instead of JSR, we end up returning correctly, with the correct final result

    success_code = success_code and rom._apply_single_fix_to_snes_address(0x908482,
        [0x69, 0x15, 0x00, 0x8D, 0x96, 0x0A, 0xA8, 0x6038],   #made the last two bytes a word for convenience in the next line
        [0x69, 0x14, 0x00, 0x8D, 0x96, 0x0A, 0x4C, SUBROUTINE_LOCATION % 0x10000],
         "11111112")
    
    return success_code

def implement_spin_attack(rom,samus):
    #here we adjust the timing sequence for screw attack, adding in the new control code
    # so that we have a new battery of poses which are used to implement spin attack

    #we're going to need some space in bank $91.  Bank $91 is super tight.
    
    #need to free up some space in $91812D-$91816E in order to relocate the screw attack sequence there.
    #don't actually need any new code for this, because so much code is duplicated -- just need to move some JSR pointers
    OLD_TABLE = [0x804D,0x8066,0x806E,0x8076,0x807E,0x8087,0x80B6,0x8086,
                 0x810A,0x8112,0x8113,0x812D,0x8132,0x813A,0x8142,0x8146,
                 0x8147,0x814F,0x8157,0x815F,0x8167,0x816F,0x8181,0x8189,
                 0x818D,0x8191,0x8199,0x81A1]
    NEW_TABLE = [0x804D,0x8066,0x806E,0x8076,0x807E,0x8087,0x80B6,0x8086,
                 0x810a,0x8112,0x8113,0x8066,0x8066,0x8066,0x8189,0x8086,
                 0x8066,0x8066,0x8066,0x8066,0x8066,0x816F,0x8181,0x8189,
                 0x818D,0x8191,0x8199,0x81A1]
    success_code = rom._apply_single_fix_to_snes_address(0x918014,OLD_TABLE,NEW_TABLE, "2"*28)
    #and here is our new timing/control sequence for screw attack, that includes our new $F5 control code
    NEW_SCREW_ATTACK = [0x04, 0xF5,    #F5 forces the decision about which sequence to draw
                        0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, #old screw attack
                        0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
                        0xFE, 0x18,
                        0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, #new spin attack
                        0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
                        0xFE, 0x18,
                        0x08, 0xFF]    #this gives the wall jump prompt in case Samus is close to a wall
    rom.bulk_write_to_snes_address(0x91812D,NEW_SCREW_ATTACK,56)   #should have ten bytes left to spare

    #the subroutine at 0x9180BE-0x918109 is unreachable.  We're going to relocate the walljump sequence there.
    NEW_WALLJUMP_SEQUENCE = [0x05, 0x05,    #lead up into a jump
                             0xFB,          #this chooses the type of jump -- we have augmented this subroutine
                             0x03, 0x02, 0x03, 0x02, 0x03, 0x02, 0x03, 0x02,   #spin jump
                             0xFE, 0x08,
                             0x02, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02, 0x01,   #space jump
                             0xFE, 0x08,
                             0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,  #old screw attack
                             0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
                             0xFE, 0x18,
                             0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,  #new spin attack
                             0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
                             0xFE, 0x18]
    rom.bulk_write_to_snes_address(0x9180BE,NEW_WALLJUMP_SEQUENCE,75)  #only one byte to spare

    #now need to point to these new sequences
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x91B010+2*0x81,
                                                                    [0xB39E,0xB39E,0xB491,0xB491],
                                                                    [0x812D,0x812D,0x80BE,0x80BE],
                                                                    "2222")

    #but because of this code here, Samus will not glow green during spin attack, so we fix this:
    #old code   $91:DA04 C9 1B 00    CMP #$001B    ;compare to 27 (near old location of the wall jump prompt)
    #new code   $91:DA04 C9 36 00    CMP #$0036    ;compare to 54 (near new location of the wall jump prompt)
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x91DA04,[0xC9,0x1B,0x00],[0xC9,0x36,0x00],"111")
    #also need to fix the walljump check similarly
    #old code   $90:9D63 C9 1B 00    CMP #$001B    ;compare to 27 (near old location of the wall jump prompt)
    #new code   $90:9D63 C9 36 00    CMP #$0036    ;compare to 54 (near new location of the wall jump prompt)
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x909D63,[0xC9,0x1B,0x00],[0xC9,0x36,0x00],"111")
    
    #we also need to relocate the walljump prompt correctly
    #old code   $90:9DD4 A9 1A 00    LDA #$001A    ;go to 26 (old location of the wall jump prompt)
    #old code   $90:9DD4 A9 35 00    LDA #$0035    ;go to 53 (new location of the wall jump prompt)
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x909DD4,[0xA9,0x1A,0x00],[0xA9,0x35,0x00],"111")

    #this breaks when Samus turns mid-air
    #here is the issue
    #$91:F634 A9 01 00    LDA #$0001
    #$91:F637 8D 9A 0A    STA $0A9A  [$7E:0A9A]
    #I need this to conditionally load this value based upon water mechanics, screw attack, and space jump
    #So I need to loop in some new code
    #And bank $91 is super tight still...I am going to have to JSL.  How about over to the death tiles,
    # which I'm going to relocate anyway?
    NEW_SUBROUTINE_LOCATION = 0x9B8000
    
    '''
    By and large this new subroutine borrows heavily from control code $FB, which has to do similar checks
    AD A2 09    LDA $09A2         ; get equipped items
    89 20 00    BIT #$0020        ; check for gravity suit
    D0 20       BNE equip_check   ; if gravity suit, underwater status is not important
    22 58 EC 90 JSL $90EC58       ; $12 / $14 = Samus' bottom / top boundary position
    AD 5E 19    LDA $195E         ; get [FX Y position]
    30 0E       BMI acid_check    ; If [FX Y position] < 0:, need to check for acid
    C5 14       CMP $14           ; Check FX Y position against Samus's position
    10 13       BPL equip_check   ; above water, so underwater status is not important
    AD 7E 19    LDA $197E         ; get physics flag
    89 04 00    BIT #$0004        ; If liquid physics are disabled, underwater status is not important
    D0 0B       BNE equip_check
    80 1D       BRA just_one_plz  ; ok, you're probably underwater at this point

    :;acid_check
    AD 62 19    LDA $1962
    30 04       BMI equip_check   ; If [lava/acid Y position] < 0, then there is no acid, so underwater status is not important
    C5 14       CMP $14           ;
    30 14       BMI just_one_plz  ; If [lava/acid Y position] < Samus' top boundary position, then you are underwater

    ;:equip_check
    AD A2 09        ;LDA $09A2        ;get equipped items
    89 08 00        ;BIT #$0008       ;check for screw attack equipped
    F0 0C           ;BEQ just_one_plz ;if screw attack not equipped, branch out
    89 00 02        ;BIT #$0200       ;check for space jump
    F0 0E           ;BEQ spin_attack  ;if space jump not equipped, branch out
    ;:screw_attack
    A9 02 00        ;LDA #0002        ;default to (new) second pose
    8D 9A 0A        ;STA $0A9A
    6B              ;RTL              ;GET OUT
    ;:just_one_plz
    A9 01 00        ;LDA #0001        ;default to first pose, as in classic
    8D 9A 0A        ;STA $0A9A
    6B              ;RTL              ;GET OUT
    ;:spin_attack
    A9 1C 00        ;LDA #001C        ;skip over to our new spin attack section
    8D 9A 0A        ;STA $0A9A
    6B              ;RTL              ;GET OUT
    '''
    NEW_CODE = [0xAD, 0xA2, 0x09, 
                0x89, 0x20, 0x00, 
                0xD0, 0x20, 
                0x22, 0x58, 0xEC, 0x90, 
                0xAD, 0x5E, 0x19, 
                0x30, 0x0E, 
                0xC5, 0x14, 
                0x10, 0x13, 
                0xAD, 0x7E, 0x19, 
                0x89, 0x04, 0x00, 
                0xD0, 0x0B, 
                0x80, 0x1D, 
                0xAD, 0x62, 0x19, 
                0x30, 0x04, 
                0xC5, 0x14, 
                0x30, 0x14, 
                0xAD, 0xA2, 0x09, 
                0x89, 0x08, 0x00, 
                0xF0, 0x0C, 
                0x89, 0x00, 0x02, 
                0xF0, 0x0E, 
                0xA9, 0x02, 0x00, 
                0x8D, 0x9A, 0x0A, 
                0x6B, 
                0xA9, 0x01, 0x00, 
                0x8D, 0x9A, 0x0A, 
                0x6B, 
                0xA9, 0x1C, 0x00, 
                0x8D, 0x9A, 0x0A, 
                0x6B]
    
    #put the new code in the ROM
    rom.bulk_write_to_snes_address(NEW_SUBROUTINE_LOCATION,NEW_CODE,74)

    #loop in the new code
    #previously: $91:F634 A9 01 00     LDA #$0001
    #            $91:F637 8D 9A 0A     STA $0A9A  [$7E:0A9A]
    #now:        $91:F634 22 ?? ?? ??  JSL NEW_SUBROUTINE_LOCATION
    #            $91:F638 EA EA        NOP NOP
    success_code = success_code and rom._apply_single_fix_to_snes_address(0x91F634,
                                                        [0xA9, 0x8D0001, 0x9A, 0x0A],
                                                        [0x22, NEW_SUBROUTINE_LOCATION, 0xEA, 0xEA],"1311")

    return success_code

def get_numbered_poses_old_and_new(rom,samus):
    for animation_string, pose in samus._layout.reverse_lookup:
        if animation_string[:2] == "0x":
            animation_int = int(animation_string[2:],16)
            yield animation_int, pose

if __name__ == "__main__":
    raise AssertionError(f"Called main() on utility library {__file__}")
