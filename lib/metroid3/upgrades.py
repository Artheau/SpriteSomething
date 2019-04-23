#This is the giant gambit for Super Metroid
#In total, this code is intended to take a ROM and modify it for wizzywig insertion

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
	

	#to break symmetry, we will need to rearrange where the gun port tile data is,
	# and correspondingly make sure that it is loaded correctly during DMA
	#Thankfully, there's plenty of room in ROM because they were
	# super super wasteful with the organization in this part.

	print("Moving gun tiles...", end=""); print("success" if move_gun_tiles(rom,samus) else "FAIL")

	#I can see how it was a good idea at the time to put the cannon port as tile $1F,
	# but this is also limiting (because it limits us to 31 tiles instead of 32).
	# Since now that we know in retrospect that the person
	# who was in charge of the Mode 7 section was not greedy with the tile space,
	# we can move the gun port over to tile $DF which is unused throughout the game
	#While we're in there, we should remove the mirroring effects on the tiles,
	# since that is no longer necessary

	print("Re-assigning gun tilemaps...", end=""); print("success" if reassign_gun_tilemaps(rom) else "FAIL")

		
	#pee on the tree
	#TODO
	#SIGNATURE_ADDRESS_EXHIROM
	#SIGNATURE_ADDRESS_LOROM
	#SIGNATURE_MESSAGE

	#now GET OUT
	return rom



def move_gun_tiles(rom,samus):
	#move the actual tile data
	# Probably the easiest place to locate this is somewhere in $9A9A00-$9AB200, since that's where they lived before
	PLACE_TO_PUT_GUN_TILES = 0x9A9A00
	# there was already a bunch of blank tile space there, so this seems like a good repurposing of the local space
	for direction in range(10):   #there are ten directions for every port
		for level in range(3):    #and there are three levels of gun port opening
			reference_number = direction+level*10  #this matches up reversibly with the code in samus.get_sprite_pose()
			image,_ = samus.get_sprite_pose("gun", reference_number)   #go get the gun image from the ZSPR
			#TODO: I need to implement convert_tile_to_bitplanes().  The image is already paletted, so I just need to arrange the bits (it's also already flipped)
			raw_tile = [0xFF for _ in range(0x20)]#util.convert_tile_to_bitplanes(image.getdata())
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

	return False

def reassign_gun_tilemaps(rom):
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

if __name__ == "__main__":
    raise AssertionError(f"Called main() on utility library {__file__}")
