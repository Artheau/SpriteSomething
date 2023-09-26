#This is the giant gambit for Super Metroid
#In total, this code takes a ROM and modifies it for wizzywig insertion

import itertools
import json
import os
import copy
from PIL import Image
from json.decoder import JSONDecodeError
from source.meta.common import common

# FIXME: English

def rom_inject(player_sprite, spiffy_dict, old_rom, verbose=False):
	rom = copy.deepcopy(old_rom)	#for safety we are going to deepcopy the ROM, in case we need to bail

	#this'll check VT rando Tournament Flag
	tournament_flag = (float(rom.get_size_in_MB()) > 1.5) and (rom.read(0x180213, 2) == 1)
	#this'll check combo Tournament Flag
	if rom.type() == "EXHIROM" and not tournament_flag:
		config = rom.read_from_snes_address(0x80FF52, 2)
		fieldvals = {}
		fieldvals["gamemode"] = [ "singleworld", "multiworld" ]
		fieldvals["z3logic"] = [ "normal", "hard" ]
		fieldvals["m3logic"] = [ "normal", "hard" ]
		field = {}
		field["race"] = ((config & (1 << 15)) >> 15) > 0 # 1 bit
		field["keysanity"] = ((config & (0b11 << 13)) >> 13) > 0 # 2 bits
		field["gamemode"] = ((config & (1 << 12)) >> 12) # 1 bit
		field["z3logic"] = ((config & (0b11 << 10)) >> 10) # 2 bits
		field["m3logic"] = ((config & (0b11 << 8)) >> 8) # 2 bits
		field["version"] = {}
		field["version"]["major"] = ((config & (0b1111 << 4)) >> 4) # 4 bits
		field["version"]["minor"] = ((config & (0b1111 << 0)) >> 0) # 4 bits

		field["gamemode"] = fieldvals["gamemode"][field["gamemode"]]
		field["z3logic"] = fieldvals["z3logic"][field["z3logic"]]
		field["m3logic"] = fieldvals["m3logic"][field["m3logic"]]

		tournament_flag = field["race"]

		# iddqd = False
		iddqd = True
		app_overrides_path = os.path.join(".","resources","user","meta","manifests","overrides.json")
		if os.path.exists(app_overrides_path):
			with open(app_overrides_path) as json_file:
				data = {}
				try:
					data = json.load(json_file)
				except JSONDecodeError as e:
					raise ValueError("User App Overrides manifest malformed!")
				if "iddqd" in data.keys():
					iddqd = data["iddqd"]

	if not tournament_flag or iddqd:
		#in case these were disabled in rom.py, we definitely need to do these before we convert to wizzywig
		rom._apply_bugfixes()
		rom._apply_improvements()

		if rom._type.name == "EXHIROM":
			pass		#if this is a SMaLttPR combo rom, then we're fine, because there's plenty of space in the low banks
		else:
			rom.expand(32)	 #otherwise, we need to expand the rom to 4MB	(32 MBits)

		#previously, the upper tilemaps were loaded before the lower tilemaps, but the lower tiles were displayed before
		# the upper tiles.	This would not otherwise have caused problems, but the extent to which we are pushing this
		# old engine requires that we sometimes use larger DMA writes that overwrite (and obviate the need for) DMAs

		if verbose:
			print("Swapping DMA load order...", end="")
		success_code = swap_DMA_order(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#to break symmetry, we will need to rearrange where the gun port tile data is,
		# and correspondingly make sure that it is loaded correctly during DMA
		#Thankfully, there's plenty of room in ROM because they were
		# super super wasteful with the organization in this part.

		if verbose:
			print("Moving gun tiles...", end="")
		success_code = move_gun_tiles(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#I can see how it was a good idea at the time to put the cannon port as tile $1F,
		# but this is also limiting (because it limits us to 31 tiles instead of 32).
		# Since now that we know in retrospect that the person
		# who was in charge of the Mode 7 section was not greedy with the tile space,
		# we can move the gun port over to tile $DF which is unused throughout the game
		#While we're in there, we should remove the mirroring effects on the tiles,
		# since that is no longer necessary given the symmetry fix from move_gun_tiles()

		if verbose:
			print("Re-assigning gun tilemaps...", end="")
		success_code = reassign_gun_tilemaps(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#write all the new graphics data from base images and layout information
		if verbose:
			print("Writing new image data...", end="")
		DMA_dict, death_DMA_loc, success_code = write_dma_data(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#maximally expand/relocate the existing DMA tables, and then add the new load data into them
		if verbose:
			print("Writing new DMA tables...", end="")
		DMA_upper_table_indices, DMA_lower_table_indices, success_code = write_new_DMA_tables(DMA_dict,player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#update the table/index references to these new DMA tables
		if verbose:
			print("Linking new tables to animations...", end="")
		success_code = link_tables_to_animations(DMA_upper_table_indices, DMA_lower_table_indices, player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#write and link all the new tilemaps (use a pointer to nullmap instead of $0000 since $0000 lags the game because reasons) using the layout info
		if verbose:
			print("Assigning new tilemaps...", end="")
		success_code = assign_new_tilemaps(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#connect the death animation correctly
		if verbose:
			print("Re-connecting death sequence...", end="")
		success_code = connect_death_sequence(DMA_dict,death_DMA_loc,player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#get rid of the stupid tile
		if verbose:
			print("Stupid tile...", end="")
		success_code = no_more_stupid(player_sprite,rom)
		if verbose:
			print("stupid" if success_code else "FAIL")

		#because a DMA of zero bytes is essentially a guaranteed game crash, the designers had to make separate subroutines
		# that made the upper tilemap not display in certain cases.	These subroutines are no longer necessary, because we
		# fixed the issue in the DMA swap order code, and so now we need to get rid of the subroutines because they break
		# a few animations in the form that they now exist

		if verbose:
			print("Disabling upper half bypass routine...", end="")
		success_code = disable_upper_bypass(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#now we're going to get set up for screw attack without space jump
		#apparently there was a riot over this not being a toggleable option, so HAR+Total proposed a control flag, which we now add
		if verbose:
			print("Writing spin_attack config value", end="")
		success_code = write_spin_attack_config(spiffy_dict,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#we need a new control code that checks for space jump, so that we can gate the animation appropriately

		if verbose:
			print("Creating new control code...", end="")
		success_code = create_new_control_code(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#now we need to insert this control code into the animation sequence for screw attack, and its counterpart in walljump

		if verbose:
			print("Implementing spin attack...", end="")
		success_code = implement_spin_attack(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#insert file select graphics
		if verbose:
			print("Injecting file select graphics...", end="")
		success_code = insert_file_select_graphics(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#assign all the palettes
		if verbose:
			print("Assigning palettes...", end="")
		success_code = assign_palettes(player_sprite,rom)
		if verbose:
			print("done" if success_code else "FAIL")

		#pee on the tree
		SIGNATURE_ADDRESS = 0x92C500
		SIGNATURE_MESSAGE = [ord(x) for x in "ART WAS HERE 000"]
		rom.write_to_snes_address(SIGNATURE_ADDRESS,SIGNATURE_MESSAGE,"1"*len(SIGNATURE_MESSAGE))

	else:
		# FIXME: English
		raise AssertionError(f"Cannot inject into a Race/Tournament ROM!")

	#now GET OUT
	return rom

def swap_DMA_order(samus,rom):
	success_code = True
	#The sum total of this function is to effectively swap the commands in the range $809382-$8093CA with the commands
	# in the range $8093CB-$809413.	Mostly, these commands are identical, except for the following changes:
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x809382, [0xAC,0x1D,0x07], [0xAC,0x1E,0x07], "111")
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x809389, [0xAD,0x1F,0x07], [0xAD,0x21,0x07], "111")
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x80938E, [0xA9,0x00,0x60], [0xA9,0x80,0x60], "111")
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093B6, [0xA9,0x00,0x61], [0xA9,0x80,0x61], "111")
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093CB, [0xAC,0x1E,0x07], [0xAC,0x1D,0x07], "111")
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093D2, [0xAD,0x21,0x07], [0xAD,0x1F,0x07], "111")
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093D7, [0xA9,0x80,0x60], [0xA9,0x00,0x60], "111")
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x8093FF, [0xA9,0x80,0x61], [0xA9,0x00,0x61], "111")

	return success_code

def move_gun_tiles(samus,rom):
	#move the actual tile data
	# Probably the easiest place to locate this is somewhere in $9A9A00-$9AB200, since that's where they lived before
	PLACE_TO_PUT_GUN_TILES = 0x9A9A00
	# there was already a bunch of blank tile space there, so this seems like a good repurposing of the local space
	for direction in range(10):	 #there are ten directions for every port
		for level in range(3):		#and there are three levels of gun port opening
			reference_number = direction+level*10	#this matches up reversibly with the code in samus.get_sprite_pose()
			name_of_gun_image = samus.layout.get_image_name("gun", reference_number)
			raw_tile = get_raw_pose(samus, name_of_gun_image)	 #go get the gun image
			rom.bulk_write_to_snes_address(PLACE_TO_PUT_GUN_TILES+0x20*reference_number,raw_tile,0x20)	#just line 'em up.	Nothing fancy.

	#move the DMA pointers
	# at $90C7A5
	# there are pointers DW VUR_GFX, AUR_GFX, HR_GFX, ADR_GFX, VDR_GFX, VDL_GFX, ADL_GFX, HL_GFX, AUL_GFX, VUL_GFX (direction based)
	# they point to DMA locations in bank $9A, e.g. DW $0000, $9A00, $9C00, $9E00
	#I need a place with room, preferably in bank $90, for a few more pointers to accomodate all ten directions,
	# so that I can have ten pointers to ten different DMA sets of this type
	#It just so happens that I'm going to free up $9086AF-$9087BC with some other changes that I'm making, so hooray!
	PLACE_TO_PUT_GUN_DMA_POINTERS = 0x9086AF			#otherwise, if this is a problem, can default to the end of the bank
	for direction in range(10):
		gfx_pointer = PLACE_TO_PUT_GUN_DMA_POINTERS+8*direction
		rom.write_to_snes_address(0x90C7A5+2*direction, gfx_pointer % 0x10000, 2)
		rom.write_to_snes_address(gfx_pointer, 0x0000, 2)	 #first gun pointer is always null in the vanilla ROM -- let's just keep doing that
		for level in range(3):
			reference_number = direction+level*10
			rom.write_to_snes_address(gfx_pointer+2*(1+level), (PLACE_TO_PUT_GUN_TILES+0x20*reference_number) % 0x10000, 2)

	return True

def get_raw_pose(samus, image_name):
	dimensions = samus.layout.get_property("dimensions",image_name)
	extra_area = samus.layout.get_property("extra area",image_name)
	xmin,ymin,_,_ = samus.layout.get_raw_bounding_box(image_name)
	return common.convert_to_4bpp(samus.images[image_name], (-xmin,-ymin), dimensions, extra_area)

def reassign_gun_tilemaps(samus,rom):
	TILE = 0xDF	 #the new location for the gun tile
	PAL = 0x28	 #unmirrored palette code
	success_codes = []

	#first, need to make sure the tile data is loaded into the new location during DMA loads
	OLD_LOC = 0x61F0								 #this is 0x6000 + 0x10*old_index, where old_index = 0x1F
	NEW_LOC = 0x6000 + (0x10*TILE)	 #e.g. for tile index 0xDF, this is 0x6DF0
	success_codes.append(	rom._apply_single_fix_to_snes_address(0x90C786, OLD_LOC, NEW_LOC, 2)	)

	#now, need to update the tilemaps to reference the new location.	Also, no more mirroring because we fixed that in the source tiles
	OLD_DATA = [0x1F, 0x28, 0x1F, 0x28, 0x1F, 0x28, 0x1F, 0x68, 0x1F, 0xA8, 0x1F, 0xE8, 0x1F, 0x28, 0x1F, 0x68, 0x1F, 0x68, 0x1F, 0x68]
	NEW_DATA = [TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL , TILE, PAL ]
	success_codes.append(	rom._apply_single_fix_to_snes_address(0x90C791, OLD_DATA, NEW_DATA, "1"*len(OLD_DATA))	)

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

		#go to the next block and try again
		self.current_block += 1
		if self.current_block < len(self.mem_blocks):
			self.offset = 0
			return self.get(size)
		raise AssertionError("ran out of memory to allocate")

def write_dma_data(samus,rom):
	if rom._type.name == "EXHIROM":		 #combo rom
		#until my hand is slapped I am going to just take up all of the lower halves of banks 0x44-0x4B and 0x54-0x5A
		freespace = FreeSpace([(bank * 0x10000,bank * 0x10000 + 0x8000) for bank in itertools.chain(range(0x44,0x4C),range(0x54,0x5A))])
		#the death DMA data needs to all be in the same bank
		death_freespace = FreeSpace([(0x5A0000,0x5A8000)])
	elif rom._type.name == "EXLOROM":
		#this is untested.	In theory works for oversized ROMs.	If not, please submit a bug report so that it can be fixed
		if rom.get_size_in_MB() >= 8.0:	 #use banks $73-$7D
			freespace = FreeSpace([(bank * 0x10000 + 0x8000,bank * 0x10000 + 0x10000) for bank in itertools.chain(range(0x9C,0xA0),range(0x73,0x7D))])
			death_freespace = FreeSpace([(0x7D8000, 0x7E0000)])
		elif rom.get_size_in_MB() >= 6.0:	 #use banks $35-$3F
			freespace = FreeSpace([(bank * 0x10000 + 0x8000,bank * 0x10000 + 0x10000) for bank in itertools.chain(range(0x9C,0xA0),range(0x35,0x3F))])
			death_freespace = FreeSpace([(0x3F8000, 0x400000)])
		else:
			raise AssertionError(f"Could not recognize size of ExLoRom: {rom.get_size_in_MB()}")
	else:		 #lorom: use banks $F5-$FF
		#we would like this to be as compatible with ROM hacks as possible, so that hackers can use this program to add new graphics to their hacks
		#so we will first use the original graphic space, and then work backwards from the end of the rom
		freespace = FreeSpace([(bank * 0x10000 + 0x8000,bank * 0x10000 + 0x10000) for bank in itertools.chain(range(0x9C,0xA0),range(0xF5,0xFF))])
		#the death DMA data needs to all be in the same bank (here placed in $FF)
		death_freespace = FreeSpace([(0xFF8000, 0x1000000)])

	DMA_dict = {}	#have to keep track of where we put all this stuff so that we can point to it afterwards


	#check to make sure "dma_sequence" in layout.json contains all the needed keys
	for image_name in samus.layout.data["images"]:
		if image_name not in samus.layout.data["dma_sequence"]:
			if image_name[:6] in ["palett","file_s","gun_po","death_"]:	#these are special cases which will go in other parts of memory
				pass
			else:
				raise AssertionError(f"Error in Samus layout.json: {image_name} not in dma_sequence key")

	for image_name in samus.layout.data["dma_sequence"]:
		DMA_data = get_raw_pose(samus, image_name)

		size = len(DMA_data)

		address_to_write = freespace.get(size)

		rom.bulk_write_to_snes_address(address_to_write,DMA_data,size)

		DMA_dict[image_name] = (address_to_write, size)

	death_image_left = compile_death_image("left",samus)
	death_image_right = compile_death_image("right",samus)

	death_DMA_loc = death_freespace.get(0)
	left_dest = death_freespace.get(0x4000)
	right_dest = death_freespace.get(0x4000)
	#wiring in the DMA this way so that it does not have to adhere to the top row/bottom row stuff
	left_DMA = list(itertools.chain.from_iterable(common.convert_to_4bpp(death_image_left, (0,0), (0,16*i,128,16*(i+1)),None) for i in range(16)))
	right_DMA = list(itertools.chain.from_iterable(common.convert_to_4bpp(death_image_right, (0,0), (0,16*i,128,16*(i+1)),None) for i in range(16)))
	rom.bulk_write_to_snes_address(left_dest, left_DMA, 0x4000)
	rom.bulk_write_to_snes_address(right_dest, right_DMA, 0x4000)

	return DMA_dict, death_DMA_loc, True

def compile_death_image(direction,samus):
	#the death DMA are special because they have to all be loaded at once as one image
	death_image = Image.new("P",(128,256),0)
	#bodies
	for i in range(8):
		this_image = samus.images[f"death_{direction}{i if i > 0 else ''}"]
		death_image.paste(this_image,(32*(i%4),64*(i//4)))	 #paste the body images over two rows

	#pieces indexed 0,1,3,4
	death_vram_locations = [(0,(0,128)),(1,(24,128)),(3,(0,176)),(4,(56,128))]
	for i,dest in death_vram_locations:
		this_image = samus.images[f"death_{direction}_pieces{i if i > 0 else ''}"]
		death_image.paste(this_image,dest)

	#have to really puzzle piece2 in there
	this_image = samus.images[f"death_{direction}_pieces2"]
	for src,dest in [(( 0, 0,40,32),(56,216)),	 #top 5x4
					 (( 0,32,32,64),(96,216)),	 #left bottom 4x4
					 ((32,32,40,40),(56,248)),
					 ((32,40,40,48),(64,248)),
					 ((32,48,40,56),(72,248)),
					 ((32,56,40,64),(80,248)),	 #right bottom pieces 4x 1x1
					]:
		piece_image = this_image.crop(src)
		death_image.paste(piece_image, dest)

	return death_image

def write_new_DMA_tables(DMA_dict,samus,rom):
	#We'll need more room, since we have 637 unique images*7 bytes each = 0x116B amount of stuff (used 0x0BE5 previously)
	#for this, we're going to eat into some area that used to be reserved for death tilemaps ($92C580-$92CBED)
	# because we know we have to change those tilemaps later anyway

	#the lookup for the tables themselves are at 92:D91E (upper)
	#$92:D91E						 dw CBEE, CCCE, CDA0, CE80, CEF7, CF6E, CFE5, D05C, D0E8, D12E, D613, D6A6, D74E
	#and at 92:D938 (lower)
	#$92:D938						 dw D19E, D27E, D35E, D6D7, D406, D4A7, D54F, D786, D5F0, D79B, D605

	#freespace is from death tilemap region up through the usual DMA table region
	UPPER_LOC = 0x92C580
	LOWER_LOC = 0x92D600
	success_code = rom._apply_single_fix_to_snes_address(0x92D91E,
		[0xCBEE, 0xCCCE, 0xCDA0, 0xCE80, 0xCEF7, 0xCF6E, 0xCFE5, 0xD05C, 0xD0E8, 0xD12E, 0xD613, 0xD6A6, 0xD74E,	#old upper table
		 0xD19E, 0xD27E, 0xD35E, 0xD6D7, 0xD406, 0xD4A7, 0xD54F, 0xD786, 0xD5F0, 0xD79B, 0xD605],	#old lower table
		[UPPER_LOC % 0x10000 for _ in range(13)] + \
		[LOWER_LOC % 0x10000 for _ in range(11)],		 #new upper table is a failsafe in case of vanilla glitches, new lower table is intentionally simplified
			"2"*24)	 #these are 24 big endian values to write
	freespace_upper = FreeSpace([(UPPER_LOC,LOWER_LOC)])
	freespace_lower = FreeSpace([(LOWER_LOC,0x92D7D2)])

	lower_table_fill = 0
	upper_table_fill = 0
	upper_table_number = 0
	DMA_upper_table_indices = {}
	DMA_lower_table_indices = {}
	for image_name,(image_location,size) in DMA_dict.items():
		if samus.layout.get_property("force",image_name) == "lower":	 #here we actually want to force to the lower half
			address_to_write = freespace_lower.get(7)
			DMA_lower_table_indices[image_name] = (0,lower_table_fill)
			lower_table_fill += 1
		else:																				 #by default, force this to upper
			address_to_write = freespace_upper.get(7)
			if upper_table_fill > 0x30:	#when they get too full, make a new table (here 0x30 is fairly arbitrary)
				upper_table_number += 1
				upper_table_fill = 0
				rom.write_to_snes_address(0x92D91E+2*upper_table_number,address_to_write % 0x10000,2)	#index the new table
			DMA_upper_table_indices[image_name] = (upper_table_number,upper_table_fill)
			upper_table_fill += 1

		bottom_row_size = 0x20*(size//0x40)	 #half of the tiles, floored (by the way we constructed the images originally)
		top_row_size = size - bottom_row_size

		rom.write_to_snes_address(address_to_write,[image_location,top_row_size,bottom_row_size],"322")

	#write the null images -- these are important because very few poses will have a strictly lower section anymore
	#lazily I am just going to let it point to the last true image location, but with a load size of 1.
	#SUPER IMPORTANT -- do NOT set these to load zero data.	DO NOT.
	#Because DMAing zero data actually means load 0x10000 data, and you will crash your game hard
	address_to_write = freespace_lower.get(7)
	rom.write_to_snes_address(address_to_write,[image_location,1,1],"322")
	DMA_lower_table_indices["null"] = (0,lower_table_fill)
	address_to_write = freespace_upper.get(7)
	rom.write_to_snes_address(address_to_write,[image_location,1,1],"322")
	DMA_upper_table_indices["null"] = (upper_table_number,upper_table_fill)

	return DMA_upper_table_indices, DMA_lower_table_indices, success_code

def link_tables_to_animations(DMA_upper_table_indices, DMA_lower_table_indices, samus,rom):
	#Here is the deal at this point -- at $92D94E there is a big table with exactly one pointer for every animation
	#ORG $92D94E				#DW AFP_T00, AFP_T01, AFP_T02, AFP_T03, ...
	#and then immediately following that is a big long list of 4 byte tuples, essentially
	#that correspond to (upper_table, upper_index, lower_table, lower_index)
	#so we need to populate this now, and might also expand the big long list
	#but if we do, we need to work OVER some code that might have something to do with loading from save points/fanfare related
	#and this code is at $92ED24-$EDF3
	#but after that, we have all the free space that we could want, right up to the end of the bank, if we so desired.
	#also we have this space that we freed up by homogenizing the tilemaps
	freespace = FreeSpace([(0x92DB48,0x92ED24),(0x92B800,0x92C500)])#,(0x92EDF4,0x930000)])

	#as a failsafe against vanilla glitches, let's start by setting all the pointers to a null list
	NULL_SIZE = 0x40
	address_to_write = freespace.get(NULL_SIZE*4)	 #going to fill the null list with the largest number of poses possible in an animation
	null_entries = [DMA_upper_table_indices["null"][0],
					DMA_upper_table_indices["null"][1],
					DMA_lower_table_indices["null"][0],
					DMA_lower_table_indices["null"][1]]
	rom.write_to_snes_address(address_to_write,NULL_SIZE*null_entries, "1"*(4*NULL_SIZE))
	#now assign all the pointers to the null list
	rom.write_to_snes_address(0x92D94E,[address_to_write % 0x10000 for _ in range(0xFD)],"2"*0xFD)

	animation_lookup = {}	 #will contain a list of the poses each animation has
	for animation, pose in get_numbered_poses_old_and_new(samus,rom):
		if animation in animation_lookup:
			animation_lookup[animation].append(pose)
		else:
			animation_lookup[animation] = [pose]

	for animation,pose_list in animation_lookup.items():	 #the "used" animations
		max_pose = max(pose_list)+1	 #+1 because zero index is a thing
		base_address = freespace.get(max_pose*4)	 #allocate memory
		rom.write_to_snes_address(0x92D94E+2*animation, base_address % 0x10000, 2)	#set the pointer to this new stuff
		for pose in range(max_pose):
			if pose in pose_list:
				image_names = samus.layout.get_all_image_names(animation,pose)
				image_entries = null_entries.copy()	 #default to null entries, unless there is image data here
				for image_name in image_names:
					if image_name in DMA_upper_table_indices:
						image_entries[0] = DMA_upper_table_indices[image_name][0]
						image_entries[1] = DMA_upper_table_indices[image_name][1]
					elif image_name in DMA_lower_table_indices:
						image_entries[2] = DMA_lower_table_indices[image_name][0]
						image_entries[3] = DMA_lower_table_indices[image_name][1]
				rom.write_to_snes_address(base_address+4*pose, image_entries,"1111")		#assign
			else:
				rom.write_to_snes_address(base_address+4*pose, null_entries, "1111")	#assign null tables

	return True

def assign_new_tilemaps(samus,rom):
	#my note to myself from early on in this process:
	#	The game stalls badly if there is a tilemap missing.	Don't use $0000 for missing tilemaps like in vanilla.
	#
	#Ok, so the offsets to the upper tilemaps are stored at $929263 in a table indexed by 2*animation number
	# Use that offset*2 + $92808D to get the list of pointers to the pose tilemaps (in bank $92)
	# These are the pointers that we need to change, so that they point at our new tilemaps
	#lower offsets are the same except start at $92945D

	#this was the old table full of TM pointers.	We navigate around the delicate areas and rearrange the remaining tilemap pointers
	lookup_table_freespace = FreeSpace([(0x928091,0x928390),(0x9283C1,0x9283E4),(0x9283e7,0x928a04),(0x928a0d,0x9290c4)])
	#leaving TM_006 alone because its auxiliary uses in-game are not clear, but the rest can go
	tilemap_freespace = FreeSpace([(0x929663,0x92B000)])	 #this used to contain all the tilemaps, and again it will!
	#reserving the space after $92B000 for death tilemaps

	#need a null map to prevent terrible lag parties from happening when vanilla glitches rear their head
	null_map_location = tilemap_freespace.get(2)
	rom.write_to_snes_address(null_map_location, 0, 2)	 #write zero to state that there are zero tiles mapped here

	#need a dumping ground for null maps if lower is not forced
	null_list_address = lookup_table_freespace.get(2*96)	#96 is the most poses of any animation

	animation_lookup = {}	 #will contain a list of the poses each animation has
	for animation, pose in get_numbered_poses_old_and_new(samus,rom):
		if animation in animation_lookup:
			animation_lookup[animation].append(pose)
		else:
			animation_lookup[animation] = [pose]

	master_tilemap_location_dict = {}

	for animation,pose_list in animation_lookup.items():
		max_pose = max(pose_list)+1	 #+1 because zero index is a thing

		#comb through first and see if we need a unique lower tilemap set
		need_lower_tilemaps = False
		for pose in range(max_pose):
			if pose in pose_list:
				for image_name in samus.layout.get_all_image_names(animation,pose):
					if samus.layout.get_property("force", image_name) == "lower":
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

				image_names = samus.layout.get_all_image_names(animation,pose)
				for image_name in image_names:
					force = samus.layout.get_property("force", image_name)
					dimensions = samus.layout.get_property("dimensions", image_name)
					extra_area = samus.layout.get_property("extra area", image_name)
					palette = samus.layout.get_property("palette", image_name)
					tilemap = get_tilemap_from_dimensions(dimensions, extra_area, palette, 0x08 if force=="lower" else 0x00)
					if image_name[:14] == "crystal_bubble":
						#have to make the huge bubble out of just a quarter bubble
						tilemap = get_quadrated_tilemap(tilemap)
					elif animation == 0xB2 and pose in itertools.chain(range(0,9),range(25,41),range(57,64)):	#0-8,25-40,57-63
						#need to 180 rotate these grapple poses so that they appears as they did in classic for upside-down poses
						tilemap = rotate_tilemap(tilemap)
					elif animation == 0xB3 and pose in itertools.chain(range(0,8),range(24,40),range(56,64)):	#0-7,24-39,56-63
						#need to 180 rotate these grapple poses so that they appears as they did in classic for upside-down poses
						tilemap = rotate_tilemap(tilemap)

					if tuple(tilemap) in master_tilemap_location_dict:
						tilemap_location = master_tilemap_location_dict[tuple(tilemap)]
					else:
						tilemap_location = tilemap_freespace.get(len(tilemap)+2)
						rom.write_to_snes_address(tilemap_location, len(tilemap)//5, 2)	#write how many tiles are mapped
						rom.bulk_write_to_snes_address(tilemap_location+2, tilemap, len(tilemap))	#and then the maps
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

def connect_death_sequence(DMA_dict,death_DMA_loc,samus,rom):
	#the death tilemaps are referenced by these offsets
	#$92:EDCF A9 1C 08		LDA #$081C									;this is an offset into the lower tilemap table for right facing death tilemaps
	#$92:EDDA A9 25 08		LDA #$0825									;this is an offset into the lower tilemap table for left facing death tilemaps
	#to dereference them, go to $92808D+2*offset
	#there you will find a list of the tilemaps for the death pose (9 in total for each side)
	#in this code we change those offsets

	freespace = FreeSpace([(0x92B001,0x92B800)])	 #starts where the other tilemaps end.
	#Needs to start on an odd number in order to index correctly from 0x92808D

	for direction,base_address in [("left",0x92EDDB),("right",0x92EDD0)]:
		death_list_location = freespace.get(18)
		if death_list_location % 2 == 0:	 #have to start on an odd number
			death_list_location += 1
			freespace.get(1)
		rom.write_to_snes_address(base_address,(death_list_location-0x92808D)//2 ,2)
		for i in range(9):
			tilemap = get_death_tilemap(direction, i)
			tilemap_location = freespace.get(len(tilemap)+2)
			rom.write_to_snes_address(tilemap_location, len(tilemap)//5, 2)	#write how many tiles are mapped
			rom.bulk_write_to_snes_address(tilemap_location+2, tilemap, len(tilemap))	#and then the maps

			#tie it into the list now
			rom.write_to_snes_address(death_list_location+2*i, tilemap_location % 0x10000, 2)

	#during the death sequence, Samus prefetches data while she is pausing for dramatic effect
	#$9B:B44A C9 04 00		CMP #$0004
	#so we just prefetch more.	Don't prefetch the very last one because that one is special, as it overwrites bonk pose
	success_code = rom._apply_single_fix_to_snes_address(0x9BB44A,[0xC9,0x0004],[0xC9,0x000F],"12")

	#new code to load different data based upon left or right facing
	'''
	AD 1E 0A	LDA $0A1E				;load the direction that Samus is facing
	89 08 00	BIT #$0008			 ;right facing?
	D0 04		 BNE right_face
	B9 ?? ??	LDA $????,y			;get the DMA relative pointers
	60				RTS
	:right_face
	B9 ?? ??	LDA $????,y		;get the DMA relative pointers
	60				RTS
	'''

	DMA_LEFT_POINTER_LOC = 0x9BFDA0
	DMA_RIGHT_POINTER_LOC = DMA_LEFT_POINTER_LOC + 32
	DEST_POINTER_LOC = DMA_RIGHT_POINTER_LOC + 32
	NEW_CODE_LOC = DEST_POINTER_LOC + 32
	NEW_CODE = [0xAD,0x1E,0x0A,0x89,0x08,0x00,0xD0,0x04,0xB9,
				DMA_LEFT_POINTER_LOC & 0xFF,(DMA_LEFT_POINTER_LOC//0x100) & 0xFF,
				0x60,0xB9,
				DMA_RIGHT_POINTER_LOC & 0xFF,(DMA_RIGHT_POINTER_LOC//0x100) & 0xFF,
				0x60]

	left_facing_tiles = death_DMA_loc
	right_facing_tiles = death_DMA_loc + 0x4000

	#place the new code
	success_code = success_code and rom._apply_single_fix_to_snes_address(NEW_CODE_LOC, [0xFF]*16, NEW_CODE,"1"*16)

	#use the correct bank
	#$9B:B6EE A9 9B			 LDA #$9B								 ;old code: use bank 9B
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x9BB6EE,[0xA9,0x9B],[0xA9,left_facing_tiles//0x10000],"11")	#get correct bank

	#place the new pointers in the table I just made
	success_code = success_code and rom._apply_single_fix_to_snes_address(DMA_LEFT_POINTER_LOC,
													 [0xFFFF]*16,
													 [(left_facing_tiles % 0x10000)+0x400*i for i in range(1,16)]+[left_facing_tiles % 0x10000],
													 "2"*16)
	success_code = success_code and rom._apply_single_fix_to_snes_address(DMA_RIGHT_POINTER_LOC,
													 [0xFFFF]*16,
													 [(right_facing_tiles % 0x10000)+0x400*i for i in range(1,16)]+[right_facing_tiles % 0x10000],
													 "2"*16)
	success_code = success_code and rom._apply_single_fix_to_snes_address(DEST_POINTER_LOC,
													 [0xFFFF]*16,
													 [0x6000+0x200*i for i in range(1,16)]+[0x6000],
													 "2"*16)

	#hook the new pointers
	#old code: $9B:B6F5 B9 C9 B7		LDA $B7C9,y		;destination of DMA data transfer during the death sequence
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x9BB6F5,[0xB9,0xB7C9],[0xB9,DEST_POINTER_LOC % 0x10000],"12")

	#hook the new subroutine
	#old code: $9B:B6E5 B9 BF B7		LDA $B7BF,y		;get the DMA relative pointers
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x9BB6E5,[0xB9,0xB7BF],[0x20,NEW_CODE_LOC % 0x10000],"12")

	#the final fetch is special because it overwrites the Samus bonk pose, so it is indexed at the last moment
	#old code: $9B:B5AE A0 08 00		LDY #$0008
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x9BB5Ae,[0xA0,0x0008],[0xA0,0x001E],"12")

	return success_code

def get_death_tilemap(direction, pose):
	#hardcoded this for now, since this is hard to get working at all
	tilemap = []

	#start with the exploding pieces
	#some tiles overlap. this is intended, and isn't a big problem for death poses
	if pose == 1:	#[-9,15,-25,23]
		x_min = -9 if direction == "left" else -15
		y_min = -25
		tile_manifest = [(x_min	 ,y_min	 ,0xC2,0x00),
						 (x_min	 ,y_min+16,0xC2,0x20),
						 (x_min	 ,y_min+32,0xC2,0x40),
						 (x_min+8 ,y_min	 ,0xC2,0x01),
						 (x_min+8 ,y_min+16,0xC2,0x21),
						 (x_min+8 ,y_min+32,0xC2,0x41),
						]
	elif pose == 2:	#[-12,20,-25,23]
		x_min = -12 if direction == "left" else -20
		y_min = -25
		tile_manifest = [(x_min	 ,y_min	 ,0xC2,0x03),
						 (x_min	 ,y_min+16,0xC2,0x23),
						 (x_min	 ,y_min+32,0xC2,0x43),
						 (x_min+16,y_min	 ,0xC2,0x05),
						 (x_min+16,y_min+16,0xC2,0x25),
						 (x_min+16,y_min+32,0xC2,0x45),
						]
	elif pose == 3:	#[-18,22,-35,29]
		x_min = -18 if direction == "left" else -22
		y_min = -35
		tile_manifest = [(x_min	 ,y_min	 ,0xC2,0xB7),
						 (x_min	 ,y_min+16,0xC2,0xD7),
						 (x_min+16,y_min	 ,0xC2,0xB9),
						 (x_min+16,y_min+16,0xC2,0xD9),
						 (x_min+24,y_min	 ,0xC2,0xBA),
						 (x_min+24,y_min+16,0xC2,0xDA),	 #top

						 (x_min	 ,y_min+32,0xC2,0xBC),
						 (x_min	 ,y_min+48,0xC2,0xDC),
						 (x_min+16,y_min+32,0xC2,0xBE),
						 (x_min+16,y_min+48,0xC2,0xDE),	 #left bottom

						 (x_min+32,y_min+32,0x00,0xF7),
						 (x_min+32,y_min+40,0x00,0xF8),
						 (x_min+32,y_min+48,0x00,0xF9),
						 (x_min+32,y_min+56,0x00,0xFA),	 #right bottom pieces
						]
	elif pose == 4:	 #[-26,30,-42,38]
		x_min = -26 if direction == "left" else -30
		y_min = -42
		tile_manifest = [(x_min	 ,y_min	 ,0xC2,0x60),
						 (x_min	 ,y_min+16,0xC2,0x80),
						 (x_min	 ,y_min+32,0xC2,0xA0),
						 (x_min	 ,y_min+48,0xC2,0xC0),
						 (x_min	 ,y_min+64,0xC2,0xE0),
						 (x_min+16,y_min	 ,0xC2,0x62),
						 (x_min+16,y_min+16,0xC2,0x82),
						 (x_min+16,y_min+32,0xC2,0xA2),
						 (x_min+16,y_min+48,0xC2,0xC2),
						 (x_min+16,y_min+64,0xC2,0xE2),
						 (x_min+32,y_min	 ,0xC2,0x64),
						 (x_min+32,y_min+16,0xC2,0x84),
						 (x_min+32,y_min+32,0xC2,0xA4),
						 (x_min+32,y_min+48,0xC2,0xC4),
						 (x_min+32,y_min+64,0xC2,0xE4),
						 (x_min+40,y_min	 ,0xC2,0x65),
						 (x_min+40,y_min+16,0xC2,0x85),
						 (x_min+40,y_min+32,0xC2,0xA5),
						 (x_min+40,y_min+48,0xC2,0xC5),
						 (x_min+40,y_min+64,0xC2,0xE5),
						]
	elif pose == 5:	 #[-36,36,-45,43]
		x_min = -36 if direction == "left" else -36
		y_min = -45
		tile_manifest = [(x_min	 ,y_min	 ,0xC2,0x07),
						 (x_min	 ,y_min+16,0xC2,0x27),
						 (x_min	 ,y_min+32,0xC2,0x47),
						 (x_min	 ,y_min+48,0xC2,0x67),
						 (x_min	 ,y_min+64,0xC2,0x87),
						 (x_min	 ,y_min+72,0xC2,0x97),
						 (x_min+16,y_min	 ,0xC2,0x09),
						 (x_min+16,y_min+16,0xC2,0x29),
						 (x_min+16,y_min+32,0xC2,0x49),
						 (x_min+16,y_min+48,0xC2,0x69),
						 (x_min+16,y_min+64,0xC2,0x89),
						 (x_min+16,y_min+72,0xC2,0x99),
						 (x_min+32,y_min	 ,0xC2,0x0B),
						 (x_min+32,y_min+16,0xC2,0x2B),
						 (x_min+32,y_min+32,0xC2,0x4B),
						 (x_min+32,y_min+48,0xC2,0x6B),
						 (x_min+32,y_min+64,0xC2,0x8B),
						 (x_min+32,y_min+72,0xC2,0x9B),
						 (x_min+48,y_min	 ,0xC2,0x0D),
						 (x_min+48,y_min+16,0xC2,0x2D),
						 (x_min+48,y_min+32,0xC2,0x4D),
						 (x_min+48,y_min+48,0xC2,0x6D),
						 (x_min+48,y_min+64,0xC2,0x8D),
						 (x_min+48,y_min+72,0xC2,0x9D),
						 (x_min+56,y_min	 ,0xC2,0x0E),
						 (x_min+56,y_min+16,0xC2,0x2E),
						 (x_min+56,y_min+32,0xC2,0x4E),
						 (x_min+56,y_min+48,0xC2,0x6E),
						 (x_min+56,y_min+64,0xC2,0x8E),
						 (x_min+56,y_min+72,0xC2,0x9E),
						]

	pieces_palette = 0x29	#normally 0x28, but the last bit here goes to the next VRAM page to grab tiles
	if pose in range(1,6):
		for x,y,size,index in tile_manifest:
			tilemap.extend([x%0x100, size+(1 if x<0 else 0), y%0x100, index, pieces_palette])

	#now add the body
	if direction == "left":
		x_min = -12
	elif direction == "right":
		x_min = -20
	else:
		raise AssertionError(f"Unknown direction {direction} in get_death_tilemap()")
	y_min = -32
	body_palette = 0x2E if pose > 0 else 0x28

	for i in range(2):
		for j in range(4):
			x = x_min + 16*i
			y = y_min + 16*j
			if x < 0:
				tilemap.extend([0x100+x,0xC3])
			else:
				tilemap.extend([x,0xC2])
			if y < 0:
				tilemap.append(0x100+y)
			else:
				tilemap.append(y)
			index_base = pose - (1 if pose >= 7 else 0)
			tilemap.append(4*(index_base%4) + 0x80*(index_base//4) + 2*i + 0x20*j)	#index
			tilemap.append(body_palette)
	return tilemap

def get_tilemap_from_dimensions(dimensions, extra_area, palette, start_index=0x00):
	if palette is None:
		palette = 0x28	 #default to normal Samus palette
	elif isinstance(palette,str) and palette[:2] == "0x":
		palette = int(palette[2:],16)
	else:
		raise AssertionError(f"Did not recognize palette hex code {palette} in get_tilemap_from_dimensions()")

	big_tiles = []
	small_tiles = []
	for bounding_box in itertools.chain([dimensions],extra_area if extra_area else []):
		xmin,ymin,xmax,ymax = bounding_box
		x_chad = ((xmax-xmin) % 16) != 0	 #True if there is a small tile hanging over in the x direction, False else
		y_chad = ((ymax-ymin) % 16) != 0	 #True if there is a small tile hanging over in the y direction, False else
		for y in range(ymin,ymax-15,16):
			for x in range(xmin,xmax-15,16):
				big_tiles.append((x,y))
			if x_chad:
				small_tiles.append((xmax-8,y	))
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
			current_index -= 0x0F	 #subtract 0x10 and add 0x01

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
				size ^= 0x01		 #flip the x sign bit
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
		if size & 0xC2 == 0:	 #small tile
			flip_anchor = 0xF8	#math
		else:
			flip_anchor = 0xF0	#more math.	Learn algebra, kids; you'll need it at 4pm on a Thursday in April.
		x = flip_anchor - x
		y = flip_anchor - y
		size ^= 0x01
		palette ^= 0xC0
		if x < 0:
			x += 0x100		 #hex stuff, happens when x is negative but close to zero
			size ^= 0x01	 #more hex stuff.	Learn hexadecimal, kids; you'll need it at 4:15pm on a Thursday in April.
		if y < 0:
			y += 0x100
		rotated_tilemap.extend([x,size,y,tile,palette])
	return rotated_tilemap

def no_more_stupid(samus,rom):
	#in theory, I could just break the code that loads the stupid tile, but I won't rest at night until this tile is gone
	rom.bulk_write_to_snes_address(0x9AD620, [0 for _ in range(0x20)], 0x20)
	#somehow I have the feeling that it's going to come back for me,
	# chasing me down while giving an endless monologue on the health benefits of kombucha
	return True

def disable_upper_bypass(samus,rom):
	#so if you DMA zero bytes, you actually DMA an entire bank.	And trying to DMA an entire bank into the middle of VRAM
	# is super bad news.	But this also means that there's not a simple way to avoid DMA -- you have to write a bypass
	# routine.	This bypass routine served its purpose in the original game but now we've made improvements to the engine
	# and this routine is actually getting in our way.
	OLD_SUBROUTINES = [0x868D, 0x8686, 0x8686, 0x86C6, 0x8688, 0x8686, 0x8686, 0x8688,
						 0x8688, 0x8688, 0x86EE, 0x8686, 0x8686, 0x874C, 0x8686, 0x870C,
						 0x8686, 0x8688, 0x8688, 0x8688, 0x8768, 0x8686, 0x8686, 0x8686,
						 0x8686, 0x877C, 0x8686, 0x8790]
	NEW_SUBROUTINES = [0x8686 for _ in range(28)]	 #these are just null routines
	success_code = rom._apply_single_fix_to_snes_address(0x90864E, OLD_SUBROUTINES, NEW_SUBROUTINES, "2"*28)
	return success_code

def write_spin_attack_config(spiffy_dict,rom):
	# Use the new screw attack animations if enabled (set $9B93FE to $0000 to disable, $0001 to enable.	All other numbers also enable.)
	flag = 0x0001

	#this'll check VARIA tournament flag
	isVaria = rom.read(0x175CA, 1) == 0x60 and rom.read(0x19E1, 1) == 0xEA and rom.read(0xF27, 1) == 0x20
	print(rom.read(0x175CA, 1), 0x60)
	print(rom.read(0x19E1,	1), 0xEA)
	print(rom.read(0xF27,	 1), 0x20)
	if isVaria:
		print("Is VARIA")
		start = 0x1C0200
		end = 0x1C0210
		for byte in range(start, end):
			print(rom.read(byte, 1), 0xFF)
			if flag > 0x0000 and rom.read(byte, 1) != 0xFF:
				print("Is Race VARIA; disabling Spin Attack")
				flag = 0x0000
	if flag > 0x0000 and "split-screw-attack_var" in spiffy_dict:
		if spiffy_dict["split-screw-attack_var"].get() == "no":
			flag = 0x0000
	rom.write_to_snes_address(0x9B93FE, flag, 2)
	return True

def create_new_control_code(samus,rom):
	#new control code: place at $908688-$9086AE (0x27 bytes)
	SUBROUTINE_LOCATION = 0x908688
	'''
	AD A2 09		;LDA $09A2			 ;get item equipped info
	89 00 02		;BIT #$0200			;check for space jump equipped
	D0 10			 ;BNE screw_attack	;if space jump, branch to regular screw attack stuff
	AF FE 93 9B ;LDA config_spinattack	 ;see if spin attack is enabled
	F0 0A			 ;BEQ screw_attack	;if disabled, do regular screw attack animation (if branch taken, uses one more clock cycle)
	;:spin_attack
	AF 96 0A 7E ;LDA.l $7E0A96	 ;get the pose number (LDA.l here to add one more clock cycle to preserve timing)
	18					;CLC						 ;prepare to do math
	69 1B 00		;ADC #$001B			;skip past the old screw attack to the new stuff
	80 09			 ;BRA get_out		 ;then prepare to end subroutine
	;:screw_attack
	AD 96 0A		;LDA $0A96			 ;get the pose number
	18					;CLC						 ;prepare to do math
	69 01 00		;ADC #$0001			;just add one to go to the old screw attack (could INC, but this preserves timing between two versions)
	80 00			 ;BRA get_out		 ;then prepare to end subroutine (could skip, but timing)
	;:get_out
	8D 96 0A		;STA $0A96			 ;store the new pose in the correct spot
	A8					;TAY						 ;transfer to Y because reasons
	38					;SEC						 ;flag the carry bit because reasons
	60					;RTS						 ;now GET OUT
	'''

	#TODO: retype this
	NEW_SUBROUTINE = [
						0xAD, 0xA2, 0x09,
						0x89, 0x00, 0x02,
						0xD0, 0x10,
						0xAF, 0xFE, 0x93, 0x9B,
						0xF0, 0x0A,
						0xAF, 0x96, 0x0A, 0x7E,
						0x18,
						0x69, 0x1B, 0x00,
						0x80, 0x09,
						0xAD, 0x96, 0x0A,
						0x18,
						0x69, 0x01, 0x00,
						0x80, 0x00,
						0x8D, 0x96, 0x0A,
						0xA8,
						0x38,
						0x60]

	rom.bulk_write_to_snes_address(SUBROUTINE_LOCATION, NEW_SUBROUTINE, 0x27)

	#need to link up this subroutine to control code $F5
	success_code = rom._apply_single_fix_to_snes_address(0x90832E, 0x8344, SUBROUTINE_LOCATION % 0x10000, 2)

	#we're going to tie in the $F5 code to run right after the normal code in $FB.
	#"Waste not want not", as people imitating my mom used to say
	#In particular, here:
	'''
	OLD CODE
	$90:8482 69 15 00		ADC #$0015
	$90:8485 8D 96 0A		STA $0A96
	$90:8488 A8					TAY
	$90:8489 38					SEC
	$90:848A 60					RTS
	'''
	#the F5 control code adds 1 if space jump is equipeed, else adds 27.	Technically we want to add 0 or 26, so we do this:
	'''
	NEW CODE
	$90:8482 69 14 00		ADC #$0014
	$90:8485 8D 96 0A		STA $0A96
	$90:8488 4C ?? ??		JMP SUBROUTINE_LOCATION
	'''
	#because we're jumping straight-up instead of JSR, we end up returning correctly, with the correct final result

	success_code = success_code and rom._apply_single_fix_to_snes_address(0x908482,
		[0x69, 0x15, 0x00, 0x8D, 0x96, 0x0A, 0xA8, 0x6038],	 #made the last two bytes a word for convenience in the next line
		[0x69, 0x14, 0x00, 0x8D, 0x96, 0x0A, 0x4C, SUBROUTINE_LOCATION % 0x10000],
		 "11111112")

	return success_code

def implement_spin_attack(samus,rom):
	#here we adjust the timing sequence for screw attack, adding in the new control code
	# so that we have a new battery of poses which are used to implement spin attack

	#we're going to need some space in bank $91.	Bank $91 is super tight.

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
	NEW_SCREW_ATTACK = [0x04, 0xF5,		#F5 forces the decision about which sequence to draw
						0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, #old screw attack
						0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
						0xFE, 0x18,
						0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, #new spin attack
						0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
						0xFE, 0x18,
						0x08, 0xFF]		#this gives the wall jump prompt in case Samus is close to a wall
	rom.bulk_write_to_snes_address(0x91812D,NEW_SCREW_ATTACK,56)	 #should have ten bytes left to spare

	#the subroutine at 0x9180BE-0x918109 is unreachable.	We're going to relocate the walljump sequence there.
	NEW_WALLJUMP_SEQUENCE = [0x05, 0x05,		#lead up into a jump
							 0xFB,					#this chooses the type of jump -- we have augmented this subroutine
							 0x03, 0x02, 0x03, 0x02, 0x03, 0x02, 0x03, 0x02,	 #spin jump
							 0xFE, 0x08,
							 0x02, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02, 0x01,	 #space jump
							 0xFE, 0x08,
							 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,	#old screw attack
							 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
							 0xFE, 0x18,
							 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,	#new spin attack
							 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
							 0xFE, 0x18]
	rom.bulk_write_to_snes_address(0x9180BE,NEW_WALLJUMP_SEQUENCE,75)	#only one byte to spare

	#now need to point to these new sequences
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x91B010+2*0x81,
																	[0xB39E,0xB39E,0xB491,0xB491],
																	[0x812D,0x812D,0x80BE,0x80BE],
																	"2222")

	#but because of this code here, Samus will not glow green during spin attack, so we fix this:
	#old code	 $91:DA04 C9 1B 00		CMP #$001B		;compare to 27 (near old location of the wall jump prompt)
	#new code	 $91:DA04 C9 36 00		CMP #$0036		;compare to 54 (near new location of the wall jump prompt)
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x91DA04,[0xC9,0x1B,0x00],[0xC9,0x36,0x00],"111")
	#also need to fix the walljump check similarly
	#old code	 $90:9D63 C9 1B 00		CMP #$001B		;compare to 27 (near old location of the wall jump prompt)
	#new code	 $90:9D63 C9 36 00		CMP #$0036		;compare to 54 (near new location of the wall jump prompt)
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x909D63,[0xC9,0x1B,0x00],[0xC9,0x36,0x00],"111")

	#we also need to relocate the walljump prompt correctly
	#old code	 $90:9DD4 A9 1A 00		LDA #$001A		;go to 26 (old location of the wall jump prompt)
	#old code	 $90:9DD4 A9 35 00		LDA #$0035		;go to 53 (new location of the wall jump prompt)
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x909DD4,[0xA9,0x1A,0x00],[0xA9,0x35,0x00],"111")

	#this breaks when Samus turns mid-air
	#here is the issue
	#$91:F634 A9 01 00		LDA #$0001
	#$91:F637 8D 9A 0A		STA $0A9A	[$7E:0A9A]
	#I need this to conditionally load this value based upon water mechanics, screw attack, and space jump
	#So I need to loop in some new code
	#And bank $91 is super tight still...I am going to have to JSL.	How about over to the death tiles,
	# which I'm going to relocate anyway?
	NEW_SUBROUTINE_LOCATION = 0x9B8000

	'''
	By and large this new subroutine borrows heavily from control code $FB, which has to do similar checks
	AD A2 09		LDA $09A2				 ; get equipped items
	89 20 00		BIT #$0020				; check for gravity suit
	D0 20			 BNE equip_check	 ; if gravity suit, underwater status is not important
	22 58 EC 90 JSL $90EC58			 ; $12 / $14 = Samus' bottom / top boundary position
	AD 5E 19		LDA $195E				 ; get [FX Y position]
	30 0E			 BMI acid_check		; If [FX Y position] < 0:, need to check for acid
	C5 14			 CMP $14					 ; Check FX Y position against Samus's position
	10 13			 BPL equip_check	 ; above water, so underwater status is not important
	AD 7E 19		LDA $197E				 ; get physics flag
	89 04 00		BIT #$0004				; If liquid physics are disabled, underwater status is not important
	D0 0B			 BNE equip_check
	80 32			 BRA underwater		; ok, you're probably underwater at this point
	:;acid_check
	AD 62 19		LDA $1962
	30 04			 BMI equip_check	 ; If [lava/acid Y position] < 0, then there is no acid, so underwater status is not important
	C5 14			 CMP $14					 ;
	30 29			 BMI underwater		; If [lava/acid Y position] < Samus' top boundary position, then you are underwater

	;:equip_check
	AD A2 09				;LDA $09A2				;get equipped items
	89 08 00				;BIT #$0008			 ;check for screw attack equipped
	F0 1A					 ;BEQ just_one		 ;if screw attack not equipped, just do normal advance
	89 00 02				;BIT #$0200			 ;check for space jump
	F0 07					 ;BEQ spin_attack	;if space jump not equipped, branch out
	;:screw_attack
	A9 02 00				;LDA #0002				;default to (new) second pose
	8D 9A 0A				;STA $0A9A
	6B							;RTL							;GET OUT
	;:spin_attack
	AF FE 93 9B		 ;LDA config_spinattack	 ;see if spin attack is enabled
	F0 F3					 ;BEQ screw_attack	;if disabled, do regular screw attack animation (if branch taken, uses one more clock cycle)
	A9 1C 00				;LDA #001C				;skip over to our new spin attack section
	8F 9A 0A 7E		 ;STA.l $7E0A9A		;(STA.l here to add one more clock cycle to preserve timing)
	6B							;RTL							;GET OUT
	;:just_one
	A9 01 00				;LDA #0001				;default to first pose, as in classic
	8D 9A 0A				;STA $0A9A
	6B							;RTL							;GET OUT
	;:underwater
	;have to figure out if Samus jumped into the water, or started out that way, can find this out by checking for $81 or $82 animation
	;check for spin attack
	AD 1C 0A				;LDA $0A1C				;get animation #
	89 80 00				;BIT #$0080			 ;check for animations $81,$82
	F0 F1					 ;BEQ just_one		 ;if not, then just do normal stuff
	80 CD					 ;BRA equip_check	;but if so, we have to go through all the normal checks
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
				0x80, 0x32,
				0xAD, 0x62, 0x19,
				0x30, 0x04,
				0xC5, 0x14,
				0x30, 0x29,
				0xAD, 0xA2, 0x09,
				0x89, 0x08, 0x00,
				0xF0, 0x1A,
				0x89, 0x00, 0x02,
				0xF0, 0x07,
				0xA9, 0x02, 0x00,
				0x8D, 0x9A, 0x0A,
				0x6B,
				0xAF, 0xFE, 0x93, 0x9B,
				0xF0, 0xF3,
				0xA9, 0x1C, 0x00,
				0x8F, 0x9A, 0x0A, 0x7E,
				0x6B,
				0xA9, 0x01, 0x00,
				0x8D, 0x9A, 0x0A,
				0x6B,
				0xAD, 0x1C, 0x0A,
				0x89, 0x80, 0x00,
				0xF0, 0xF1,
				0x80, 0xCD]


	#put the new code in the ROM
	rom.bulk_write_to_snes_address(NEW_SUBROUTINE_LOCATION,NEW_CODE,91)

	#loop in the new code
	#previously: $91:F634 A9 01 00		 LDA #$0001
	#						$91:F637 8D 9A 0A		 STA $0A9A	[$7E:0A9A]
	#now:				$91:F634 22 ?? ?? ??	JSL NEW_SUBROUTINE_LOCATION
	#						$91:F638 EA EA				NOP NOP
	success_code = success_code and rom._apply_single_fix_to_snes_address(0x91F634,
														[0xA9, 0x8D0001, 0x9A, 0x0A],
														[0x22, NEW_SUBROUTINE_LOCATION, 0xEA, 0xEA],"1311")

	return success_code

def insert_file_select_graphics(samus,rom):
	#classically, the file select DMA data is located at $B6:C000.	However, many hacks relocate this to make more room for pause menu graphics.
	file_select_data_location = rom.read_from_snes_address(0x818E34, 3)

	#hard coded the image locations for now
	file_select_graphics_block = Image.new("P",(128,24),0)
	left_head = samus.images["file_select_head"]
	file_select_graphics_block.paste(left_head,(0,0))
	middle_head = samus.images["file_select_head1"]
	file_select_graphics_block.paste(middle_head,(24,0))
	center_head = samus.images["file_select_head2"]
	file_select_graphics_block.paste(center_head,(48,0))
	visor0 = samus.images["file_select_visor"]
	file_select_graphics_block.paste(visor0,(72,0))
	visor1 = samus.images["file_select_visor1"]
	file_select_graphics_block.paste(visor1,(88,0))
	visor2 = samus.images["file_select_visor2"]
	file_select_graphics_block.paste(visor2,(104,0))
	visor3 = samus.images["file_select_visor3"]
	file_select_graphics_block.paste(visor3,(72,8))
	visor4 = samus.images["file_select_visor4"]
	file_select_graphics_block.paste(visor4,(88,8))
	cursor_array = samus.images["file_select_cursor_array"]
	file_select_graphics_block.paste(cursor_array.crop((0,24,8,32)),(112,16))
	file_select_graphics_block.paste(cursor_array.crop((0,16,8,24)),(112,8))
	file_select_graphics_block.paste(cursor_array.crop((0,8,8,16)),(120,0))
	stray_missile_image = cursor_array.crop((0,0,8,8))
	file_select_graphics_block.paste(cursor_array.crop((8,8,16,16)),(120,8))
	file_select_graphics_block.paste(cursor_array.crop((8,16,16,24)),(120,16))
	stray_missilehead_image = cursor_array.crop((8,24,16,32))
	file_select_piping = samus.images["file_select_piping"]
	file_select_graphics_block.paste(file_select_piping.crop((0,0,24,8)),(72,16))	#top
	file_select_graphics_block.paste(file_select_piping.crop((16,8,24,24)),(104,8))	#side
	file_select_graphics_block.paste(file_select_piping.crop((0,16,8,24)),(96,16))	#corner

	file_select_DMA = common.convert_to_4bpp(file_select_graphics_block, (0,0), (0,0,128,16),None)
	file_select_DMA.extend(common.convert_to_4bpp(file_select_graphics_block, (0,0), (0,16,128,32),None)[:0x200])

	rom.bulk_write_to_snes_address(file_select_data_location + 0x1A00,file_select_DMA,0x600)

	stray_missile_DMA = common.convert_to_4bpp(stray_missile_image, (0,0), (0,0,8,8), None)
	rom.bulk_write_to_snes_address(file_select_data_location + 0x1900,stray_missile_DMA,0x20)
	stray_missilehead_DMA = common.convert_to_4bpp(stray_missilehead_image, (0,0), (0,0,8,8), None)
	rom.bulk_write_to_snes_address(file_select_data_location + 0x1980,stray_missilehead_DMA,0x20)

	return True

def assign_palettes(samus,rom):
	do_write = {
		"doors": True,
		"loader": True,
		"heat": True,
		"sepia": True,
		"sepia-hurt": True,
		"standard": True,
		"death": True,
		"crystalflash": True,
		"charge": True,
		"speed-boost": True,
		"speed-squat": True,
		"shinespark": True,
		"screwattack": True,
		"xray": True,
		"hyperbeam": True,
		"ship": True,
		"ship-intro": True,
		"ship-outro": True,
		"fileselect": True
	}

	#read saved palette writers file if it exists and set these
	palette_writers_path = os.path.join(".","resources","user","snes","metroid3","samus","manifests","palette_writers.json")
	if os.path.exists(palette_writers_path):
		with open(palette_writers_path) as json_file:
			data = {}
			try:
				data = json.load(json_file)
			except JSONDecodeError as e:
				raise ValueError("Palette Writers manifest malformed: " + "metroid3/samus")
			for k,v in data.items():
				do_write[k] = v

	# print("Pallettes:")

	key = "doors"
	if key in do_write and do_write[key]:
		# print(" Doors")
		# doors
		_,door_palette = samus.get_timed_palette("power","door")[0]
		door_555 = common.convert_to_555(door_palette)
		rom.write_to_snes_address(0x82E52C,door_555[3],2) #visor inside doors

	key = "loader"
	if key in do_write and do_write[key]:
		# print(" Loader")
		# loader
		for suit, loader_base_addr in [("power", 0x8DDB62+2),("varia",0x8DDCC8+2),("gravity",0x8DDE2E+2)]:
			loader_palettes = [pal for _,pal in samus.get_timed_palette(suit,"loader")]
			loader_555 = [common.convert_to_555(pal) for pal in loader_palettes]
			rom.write_to_snes_address(loader_base_addr+0x009,loader_555[0x00],"2"*0x0F)
			rom.write_to_snes_address(loader_base_addr+0x02D,loader_555[0x01],"2"*0x0F)
			rom.write_to_snes_address(loader_base_addr+0x058,loader_555[0x48],"2"*0x0F)
			rom.write_to_snes_address(loader_base_addr+0x07C,loader_555[0x49],"2"*0x0F)
			rom.write_to_snes_address(loader_base_addr+0x0A7,loader_555[0x4E],"2"*0x0F)
			rom.write_to_snes_address(loader_base_addr+0x0CB,loader_555[0x4F],"2"*0x0F)
			rom.write_to_snes_address(loader_base_addr+0x0F6,loader_555[0x54],"2"*0x0F)
			rom.write_to_snes_address(loader_base_addr+0x11A,loader_555[0x55],"2"*0x0F)
			rom.write_to_snes_address(loader_base_addr+0x142,loader_555[0x58],"2"*0x0F)

	key = "heat"
	if key in do_write and do_write[key]:
		# print(" Heat")
		# heat
		for suit, heat_base_addr in [("power",0x8DE45E),("varia",0x8DE68A),("gravity",0x8DE8B6)]:
			#these are stored as just fifteen colors, not sixteen.	The timer is in the spot normally taken by color 0
			heat_palettes = [pal for _,pal in samus.get_timed_palette(suit,"heat")]
			heat_555 = [common.convert_to_555(pal) for pal in heat_palettes]
			for i in range(16):
				rom.write_to_snes_address(heat_base_addr+0x0A+0x22*i,heat_555[i][-0x0F:],"2"*0x0F)

	key = "sepia"
	if key in do_write and do_write[key]:
		# print(" Sepia")
		# sepia
		_,sepia_palette = samus.get_timed_palette("power","sepia")[0]
		sepia_555 = common.convert_to_555(sepia_palette)
		rom.write_to_snes_address(0x8CE569+2,sepia_555,"2"*0x0F)
		rom.write_to_snes_address(0x9BA3A0+2,sepia_555,"2"*0x0F)								 #same as sepia regular

	key = "sepia-hurt"
	if key in do_write and do_write[key]:
		# print(" Sepia Hurt")
		# sepia hurt
		_,sepia_hurt_palette = samus.get_timed_palette("power","sepia hurt")[0]
		sepia_hurt_555 = common.convert_to_555(sepia_hurt_palette)
		rom.write_to_snes_address(0x9BA380+2,sepia_hurt_555,"2"*0x0F)
		# rom.write_to_snes_address(0x9BA3A0+2,sepia_555,"2"*0x0F)								 #same as sepia regular

	key = "standard"
	if key in do_write and do_write[key]:
		# print(" Standard")
		# standard
		for suit, base_addr in [("power",0x9B9400),("varia",0x9B9520),("gravity",0x9B9800)]:
			_,standard_palette = samus.get_timed_palette(suit,"standard")[0]
			standard_555 = common.convert_to_555(standard_palette)
			rom.write_to_snes_address(base_addr+2,standard_555,"2"*0x0F)

	key = "death"
	if key in do_write and do_write[key]:
		# print(" Death")
		# death
		death_flesh_palettes = [pal for _,pal in samus.get_timed_palette("power","death")]
		death_flesh_555 = [common.convert_to_555(pal) for pal in death_flesh_palettes]
		for i in range(9):
			rom.write_to_snes_address(0x9BA120+2+0x20*i,death_flesh_555[i],"2"*0x0F)

	key = "crystalflash"
	if key in do_write and do_write[key]:
		# print(" Crystal Flash")
		# crystal flash
		crystal_flash_palettes = [pal for _,pal in samus.get_timed_palette("power","flash")]
		crystal_flash_555 = [common.convert_to_555(pal) for pal in crystal_flash_palettes]
		for i in range(6):
			rom.write_to_snes_address(0x9B96C0+2+0x20*i,crystal_flash_555[i],"2"*0x0F)

	key = "charge"
	if key in do_write and do_write[key]:
		# print(" Charge")
		# charge
		for suit, charge_base_addr in [("power",0x9B9820),("varia",0x9B9920),("gravity",0x9B9A20)]:
			charge_palettes = [pal for _,pal in samus.get_timed_palette(suit,"charge")]
			charge_555 = [common.convert_to_555(pal) for pal in charge_palettes]
			for i in range(8):
				rom.write_to_snes_address(charge_base_addr+2+0x20*i,charge_555[i],"2"*0x0F)

	key = "speed-boost"
	if key in do_write and do_write[key]:
		# print(" Speed Boost")
		# speed boost
		for suit, speed_boost_base_addr in [("power",0x9B9B20),("varia",0x9B9D20),("gravity",0x9B9F20)]:
			speed_boost_palettes = [pal for _,pal in samus.get_timed_palette(suit,"speed boost")]
			speed_boost_555 = [common.convert_to_555(pal) for pal in speed_boost_palettes]
			for i in range(4):
				rom.write_to_snes_address(speed_boost_base_addr+2+0x20*i,speed_boost_555[i],"2"*0x0F)

	key = "speed-squat"
	if key in do_write and do_write[key]:
		# print(" Speed Squat")
		# speed squat
		for suit, speed_squat_base_addr in [("power",0x9B9BA0),("varia",0x9B9DA0),("gravity",0x9B9FA0)]:
			speed_squat_palettes = [pal for _,pal in samus.get_timed_palette(suit,"speed squat")]
			speed_squat_555 = [common.convert_to_555(pal) for pal in speed_squat_palettes]
			for i in range(4):
				rom.write_to_snes_address(speed_squat_base_addr+2+0x20*i,speed_squat_555[i],"2"*0x0F)

	key = "shinespark"
	if key in do_write and do_write[key]:
		# print(" Shinespark")
		# shinespark
		for suit, shinespark_base_addr in [("power",0x9B9C20),("varia",0x9B9E20),("gravity",0x9BA020)]:
			shinespark_palettes = [pal for _,pal in samus.get_timed_palette(suit,"shinespark")]
			shinespark_555 = [common.convert_to_555(pal) for pal in shinespark_palettes]
			for i in range(4):
				rom.write_to_snes_address(shinespark_base_addr+2+0x20*i,shinespark_555[i],"2"*0x0F)

	key = "screwattack"
	if key in do_write and do_write[key]:
		# print(" Screw Attack")
		# screw attack
		for suit, screw_attack_base_addr in [("power",0x9B9CA0),("varia",0x9B9EA0),("gravity",0x9BA0A0)]:
			screw_attack_palettes = [pal for _,pal in samus.get_timed_palette(suit,"screw attack")]
			screw_attack_555 = [common.convert_to_555(pal) for pal in screw_attack_palettes]
			for i in range(4):
				rom.write_to_snes_address(screw_attack_base_addr+2+0x20*i,screw_attack_555[i],"2"*0x0F)

	key = "xray"
	if key in do_write and do_write[key]:
		# print(" XRay")
		# xray
		xray_colors = [pal[3] for _,pal in samus.get_timed_palette("power","xray")]
		xray_555 = common.convert_to_555(xray_colors)
		rom.write_to_snes_address(0x9BA3C0,xray_555,"222")	 #xray lead up colors
		rom.write_to_snes_address(0x9BA3C6,xray_555,"222")	 #sustained xray colors

	key = "hyperbeam"
	if key in do_write and do_write[key]:
		# print(" Hyper Beam")
		# hyper beam
		hyper_beam_palettes = [pal for _,pal in samus.get_timed_palette("power","hyper")][::-1]
		hyper_beam_555 = [common.convert_to_555(pal) for pal in hyper_beam_palettes]
		for i in range(10):
			rom.write_to_snes_address(0x9BA240+2+0x20*i,hyper_beam_555[i],"2"*0x0F)

	key = "ship"
	if key in do_write and do_write[key]:
		# print(" Ship")
		# ship
		ship_palettes = [pal for _,pal in samus.get_timed_palette("ship","standard")]
		ship_555 = [common.convert_to_555(pal) for pal in ship_palettes]
		rom.write_to_snes_address(0xA2A59E+2, ship_555[0][:14],"2"*0x0E)	 #only the first 14 colors should be written (last is reserved for underglow)
		for i in range(0x0E):	 #underglow
			rom.write_to_snes_address(0x8DCA4E+6+6*i,ship_555[i][-1],2)	#just the last color

	key = "ship-intro"
	if key in do_write and do_write[key]:
		# print(" Ship Intro")
		# ship intro
		_,intro_ship_palette = samus.get_timed_palette("ship","intro")[0]
		intro_ship_555 = common.convert_to_555(intro_ship_palette)
		rom.write_to_snes_address(0x8CE689+2, intro_ship_555, "2"*0x0F)

	key = "ship-outro"
	if key in do_write and do_write[key]:
		# print(" Ship Outro")
		# ship outro
		outro_ship_palettes = [pal for _,pal in samus.get_timed_palette("ship","outro")]
		outro_ship_555 = [common.convert_to_555(pal) for pal in outro_ship_palettes]
		for i in range(0x10):
			rom.write_to_snes_address(0x8DD6BA+2+6+0x24*i, outro_ship_555[i], "2"*0x0F)

	key = "fileselect"
	if key in do_write and do_write[key]:
		# print(" File Select")
		# file select
		_,file_select_palette = samus.get_timed_palette( "power","file select")[0]
		file_select_555 = common.convert_to_555(file_select_palette)
		rom.write_to_snes_address(0x8EE5E0+2, file_select_555, "2"*0x0F)

	return True

def get_numbered_poses_old_and_new(samus,rom):
	for animation_string, pose in samus.layout.reverse_lookup:
		if animation_string[:2] == "0x":
			animation_int = int(animation_string[2:],16)
			yield animation_int, pose
