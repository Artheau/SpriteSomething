#This is the giant gambit for Super Metroid
#In total, this code is intended to take a ROM and modify it for wizzywig insertion

import itertools   #for iterating over multiple iterables
import copy   #for safety right now we are going to deepcopy the ROM, in case we need to bail

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
    
    #TODO: "just" the stuff in this list, in addition to the things that I haven't thought of yet
    #
    #fix the lower tilemap locked poses (also fix the stupid tile while you're in this part of the code)
    #
    #I anticipate the following animations having things that are stupid that will need fixing:
    # crystal flash (morph/unmorph needs to be upper, bubble lower, etc., also the bubble needs a special tilemap)
    # screw attack (space jump needs to be lower, sparks upper, etc.)
    # grapple (need to mirror the tilemaps for the upper semicircle, and then copy the first 32 poses to the next 32)
    #
    #screw attack without space jump -- a lot of things need to happen here
    # make a new control code to check for space jump only
    # feed it into the frame delay lists for screw attack animations, so that the new animation is first (shorter), and the old animation is next (longer)
    # might need to fix the positioning of wall jump pose
    # might need to fix the palette assignments so that everything glows green that is supposed to glow green, and also the reverse
    # expand the above code for DMA and tilemap stuff for animations 0x81 and 0x82 and the walljump versions
    #  so that we have the new poses included correctly
    #
    #write the death animation DMA data in a space worthy of its importance in my personal gameplay
    #move the DMA pointers accordingly, and increase the DMA load size
    #re-write the death tilemaps from layout info
    #
    #at this point there are a couple animations that are intertwined with Samus, like splashing and bubbles, that will need repair
    #
    #don't need to modify file select -- this will be modified in-place by the ZSPR data
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
    PLACE_TO_PUT_GUN_DMA_POINTERS = 0x90F640   #as good a place as any, I guess, since bank $90 is pretty compact, and the end is all junk fill
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
        freespace = FreeSpace([(bank * 0x10000,bank * 0x10000 + 0x8000) for bank in it.chain(range(0x44,0x4C),range(0x54,0x5C))])
    else:
        #in this case, the only person that will slap my hand is me, and I'm not feeling it at the moment
        #so we're just going to take up the upper halves of half of the new banks that we just added (0xE8-0xF7)
        freespace = FreeSpace([(bank * 0x10000 + 0x8000,bank * 0x10000 + 0x10000) for bank in range(0xE8,0xF8)])

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
            address_to_write = freespace.get(size)
            rom.bulk_write_to_snes_address(address_to_write,DMA_data,size)

            DMA_dict[image_name] = (address_to_write, size)

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
    for animation, pose in samus.get_all_poses():
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

    #leaving TM_006 alone because its auxiliary uses in-game are not clear, but the rest can go
    freespace = FreeSpace([(0x929663,0x92C580)])   #this used to contain all the tilemaps, and again it will!

    #need a null map to prevent terrible lag parties from happening when vanilla glitches rear their head
    null_map_location = freespace.get(2)
    rom.write_to_snes_address(null_map_location, 0, 2)   #write 0x0000 to state that there are zero tiles mapped here

    animation_lookup = {}   #will contain a list of the poses each animation has
    for animation, pose in samus.get_all_poses():
        if animation in animation_lookup:
            animation_lookup[animation].append(pose)
        else:
            animation_lookup[animation] = [pose]

    master_tilemap_location_dict = {}

    for animation,pose_list in animation_lookup.items():
        max_pose = max(pose_list)+1   #+1 because zero index is a thing
        for pose in range(max_pose):
            upper_list_address = 0x92808D + 2*rom.read_from_snes_address(0x929263+2*animation,2)
            lower_list_address = 0x92808D + 2*rom.read_from_snes_address(0x92945D+2*animation,2)
            if pose in pose_list:
                #default to null map
                rom.write_to_snes_address(upper_list_address+2*pose, null_map_location % 0x10000, 2)
                rom.write_to_snes_address(lower_list_address+2*pose, null_map_location % 0x10000, 2)

                image_names = samus._layout.get_all_image_names(animation,pose)
                for image_name in image_names:
                    dimensions = samus._layout.get_property("dimensions", image_name)
                    extra_area = samus._layout.get_property("extra area", image_name)
                    palette = samus._layout.get_property("palette", image_name)
                    tilemap = get_tilemap_from_dimensions(dimensions, extra_area, palette)
                    if tuple(tilemap) in master_tilemap_location_dict:
                        tilemap_location = master_tilemap_location_dict[tuple(tilemap)]
                    else:
                        tilemap_location = freespace.get(len(tilemap)+2)
                        rom.write_to_snes_address(tilemap_location, len(tilemap)//5, 2)  #write how many tiles are mapped
                        rom.bulk_write_to_snes_address(tilemap_location+2, tilemap, len(tilemap))  #and then the maps
                        master_tilemap_location_dict[tuple(tilemap)] = tilemap_location
                    #see if this has to go in the lower tilemap, and if so, do that
                    force = samus._layout.get_property("force", image_name)
                    if force == "lower":
                        rom.write_to_snes_address(lower_list_address+2*pose, tilemap_location % 0x10000, 2)
                    else:
                        rom.write_to_snes_address(upper_list_address+2*pose, tilemap_location % 0x10000, 2)
            else:
                rom.write_to_snes_address(upper_list_address+2*pose, null_map_location % 0x10000, 2)
                rom.write_to_snes_address(lower_list_address+2*pose, null_map_location % 0x10000, 2)

    return True

def get_tilemap_from_dimensions(dimensions, extra_area, palette):
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
    current_index = 0x00
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

if __name__ == "__main__":
    raise AssertionError(f"Called main() on utility library {__file__}")
