#Originaly writtn by Artheau
#in Aprl 2019
#wile his brain and lettrs wer slpping awy

#includes routines that load the rom and apply bugfixes
#inherits from SNESRomHandler

    
if __name__ == "__main__":
    raise AssertionError(f"Called main() on utility library {__file__}")

import enum
from .RomHandler.rom import RomHandler      #assumes rom.py is in a subfolder called RomHandler


#enumeration for the suit types
class SuitType(enum.Enum):
    POWER = enum.auto()
    VARIA = enum.auto()
    GRAVITY = enum.auto()

class PaletteType(enum.Enum):
    STANDARD = enum.auto()           #palette used in absence of other effects
    LOADER = enum.auto()             #used when loading from a save
    HEAT = enum.auto()               #used in "hot" areas, or when the background is flashing red with alarm
    CHARGE = enum.auto()             #holding down the fire button
    SPEED_BOOST = enum.auto()        #running fast
    SPEED_SQUAT = enum.auto()        #after running fast and then pressing down
    SHINE_SPARK = enum.auto()        #flying through the air crazy-like
    SCREW_ATTACK = enum.auto()       #using screw attack
    HYPER_BEAM = enum.auto()         #the rainbow suit colors
    DEATH_SUIT = enum.auto()         #colors used to render the suit pieces as they break apart
    DEATH_FLESH = enum.auto()        #colors used to render suitless Samus during the death sequence
    CRYSTAL_FLASH = enum.auto()      #crystal flash rotating bubble colors
    SEPIA = enum.auto()              #during the intro sequence, most of the time
    SEPIA_HURT = enum.auto()         #during the intro sequence while getting hurt by mother brain
    SEPIA_ALTERNATE = enum.auto()    #during the intro sequence after getting hurt by mother brain (why is this a thing?)
    DOOR = enum.auto()               #palette used while Samus is transitioning through doors (basically just visor color)
    XRAY = enum.auto()               #palette used while Samus is in dark rooms, or when xray is active
    FILE_SELECT = enum.auto()        #used to render the Samus heads, the cursor, and the frame around SAMUS DATA
    SHIP = enum.auto()               #used to render Samus's ship in the game (includes underlight glowing)
    INTRO_SHIP = enum.auto()         #ship while flying to planet Zebes
    OUTRO_SHIP = enum.auto()         #ship while escaping from Zebes at the end


class SamusRomHandler(RomHandler):
    def __init__(self, filename):
        super().__init__(filename)      #do the usual stuff

        self._apply_bugfixes()
        self._apply_improvements()


    def get_pose_data(self,animation,pose):
        tilemaps = self._get_pose_tilemaps(animation,pose)
        DMA_writes = self._get_dma_data(animation, pose)
        duration = self._get_pose_duration(animation, pose)
        return tilemaps, DMA_writes, duration


    def get_default_vram_data(self, equipped_weapon = "standard"):
        #go in and get the data that is by default loaded into the VRAM.
        #Except for stupid tile, this shouldn't be rendered as part of a Samus pose
        # unless something is glitched out (by this I mean a game glitch, not a bug in my code)
        # in which case the data here will depend upon what kind of weapon Samus has equipped

        #main population is from data starting at D5200-D71FF LOROM (populates from 0x00 on)
        #Note: grapple beam (D0200 LOROM) can overwrite parts of row 2, and Mode 7 rooms (183A00 LOROM)
        # can load "sprites" into the last three rows.  Rain can also go in row 0xD0
        DMA_writes = {0x00: self.read_from_snes_address(0x9AD200,'1'*0x2000)}

        #row 0x30 is populated with 8 tiles depending upon equipped weapon (0x30-0x37) 
        if equipped_weapon in ["regular","standard","charge"]:
            DMA_writes[0x30] = self.read_from_snes_address(0x9AF200,'1'*0x100)
        elif equipped_weapon in ["ice"]:
            DMA_writes[0x30] = self.read_from_snes_address(0x9AF400,'1'*0x100)
        elif equipped_weapon in ["wave"]:
            DMA_writes[0x30] = self.read_from_snes_address(0x9AF600,'1'*0x100)
        elif equipped_weapon in ["plasma"]:
            DMA_writes[0x30] =  self.read_from_snes_address(0x9AF800,'1'*0x100)
        elif equipped_weapon in ["spazer"]:
            DMA_writes[0x30] = self.read_from_snes_address(0x9AFA00,'1'*0x100)

        return DMA_writes


    def get_pose_control_data(self,animation,pose):
        #similar to get_pose_duration, except that this returns a list containing the pose control code
        # and its accompanying arguments in a list
        duration_list_location = self._get_duration_list_location(animation)
        control_code = self.read_from_snes_address(duration_list_location,1)
        if control_code in [0xF8,0xFD,0xFE]:
            return self.read_from_snes_address(duration_list_location, "11")  #these codes have one byte-sized argument
        elif control_code == 0xF9:
            return self.read_from_snes_address(duration_list_location, "121111")  #has one word and 4 byte arguments
        elif control_code == 0xFA:
            return self.read_from_snes_address(duration_list_location, "111")   #two byte arguments
        elif control_code == 0xFC:
            return self.read_from_snes_address(duration_list_location, "1211")    #one word and 2 byte arguments
        else:
            return [control_code]


    def get_gun_data(self, animation, pose, frame=0x08):
        #frame is used to tell the code how far the gun port is into the opening process
        # it opens using three different poses that open over 4 frames each, so full open is 0x08 or more

        #get the pointer to the XY data (XY_P?? in disassembly)
        cannon_position_pointer = 0x900000 + self.read_from_snes_address(0x90C7DF + 2*animation,2)
        
        #first byte tells us the direction the cannon is facing, and if it has high bit set, it only counts for first pose
        #second byte tells us the rendering priority (0 = do not render, 1 = render in front of Samus, 2 = render behind Samus)
        direction, priority = self.read_from_snes_address(cannon_position_pointer,"11")

        #if first byte has high bit set and we are not in the zero pose, grab another set of values for use in the following frames 
        if direction >= 0x80:
            cannon_position_pointer += 2
            if pose > 0:
                direction, priority = self.read_from_snes_address(cannon_position_pointer,"11")

        #TODO: Priority 2 is not implemented in this code -- this should render behind Samus

        if priority in [0x00,0x02]:    #bail out now if the gun should not be drawn
            tilemap = None
            DMA_write = None
        elif priority != 0x01:
            raise AssertionError(f"get_gun_port() called for data that has non-one priority {priority}")
        else:
            direction = direction & 0x7F   #need to clear out that high bit for the rest of this

            #now what is left is a list of xy pairs.  we can just grab what we need.
            x_position, y_position = self.read_from_snes_address(cannon_position_pointer + 2*(pose+1), "11")
            
            tile, palette = self.read_from_snes_address(0x90C791+2*direction, "11")

            #construct the full tilemap
            x_high_bit = 1 if x_position >= 0x80 else 0
            tilemap = [x_position, x_high_bit, y_position, tile, palette]

            #need DMA info
            DMA_list = 0x900000 + self.read_from_snes_address(0x90C7A5 + 2*direction, 2)
            level_of_opening = min(2, frame//4)
            DMA_pointer = 0x900000 + self.read_from_snes_address(DMA_list + 2*(1 + level_of_opening), 2)

            #this is where the tile is loaded into in VRAM
            DMA_destination = (self.read_from_snes_address(0x90C786,2)-0x6000)//0x10

            DMA_writes = {DMA_destination: self.read_from_snes_address(DMA_pointer, "1"*0x20)}

        return tilemap, DMA_writes


    def get_death_data(self, pose, facing='left', suit=SuitType.POWER):
        #get tilemap
        if facing[0] in ['l','L']:
            tilemaps = self._get_pose_tilemaps_from_addr(0x92EDDB, 0, pose)
        elif facing[0] in ['r','R']:
            tilemaps = self._get_pose_tilemaps_from_addr(0x92EDD0, 0, pose)
        else:
            raise AssertionError(f"received call to get_death_data() with invalid facing {facing}")

        #get DMA data
        DMA_writes = {}
        write_size = self.read_from_snes_address(0x9BB6DF,2)
        for i in range(5):
            dest_tile = (self.read_from_snes_address(0x9BB7C9+2*i,2) - 0x6000)//0x10
            source_data = 0x9B0000 + self.read_from_snes_address(0x9BB7BF+2*i,2)
            DMA_writes[dest_tile] = self.read_from_snes_address(source_data, "1"*write_size)

        #how long to hold this pose, and an index to which palette to use
        duration, palette_index = self.read_from_snes_address(0x9BB823 + 2*pose, "11")

        #commented this out because now going to do palettes in a self-contained manner
        # if suit == SuitType.POWER:
        #     suit_number == 0
        # if suit == SuitType.VARIA:
        #     suit_number == 1
        # if suit == SuitType.GRAVITY:
        #     suit_number == 2
        # suit_palette_addr = 0x9B0000 + self.read_from_snes_address(0x9BB7D3+2*palette_index+10*suit_number, 2)
        # suitless_palette_addr = 0x9B0000 + self.read_from_snes_address(0x9BB7D3+2*palette_index+30, 2)

        return tilemaps, DMA_writes, duration



    def get_file_select_dma_data(self):
        return {0x00: self.read_from_snes_address(0xB6C000, "1"*0x2000)}


    def get_palette(self, base_type, suit_type):
        #returns a list.  Each element of the list is a tuple, where the first entry is the amount of time that the palette
        # should display for (here $00 is a special case for static palettes).  The second entry is the 555 palette data.

        PALETTE_READ_SIZE = "2"*0x10

        if base_type == PaletteType.STANDARD:
            if suit_type == SuitType.POWER:
                base_address = 0x9B9400    
            elif suit_type == SuitType.VARIA:
                base_address = 0x9B9520
            elif suit_type == SuitType.GRAVITY:
                base_address = 0x9B9800
            else:
                raise AssertionError(f"function get_palette() called for standard palette with unknown suit type: {suit_type}")
            return [self._get_static_palette(base_address)]

        elif base_type == PaletteType.LOADER:
            if suit_type == SuitType.POWER:
                base_address = 0x8DDB62
            elif suit_type == SuitType.VARIA:
                base_address = 0x8DDCC8
            elif suit_type == SuitType.GRAVITY:
                base_address = 0x8DDE2E
            else:
                raise AssertionError(f"function get_palette() called for loader palette with unknown suit type: {suit_type}")

            #this is a set of rotating palettes implemented in microcode (loader is the most complex case of these, thankfully)
            full_palette_set = []
            for _ in range(4):    #there are four "cycles" before a special fifth cycle
                counter = self.read_from_snes_address(base_address + 6, 1)
                current_palette_set = []
                base_address += 7               #skip over the control codes for this cycle
                #each cycle has two palettes each
                for _ in range(2):
                    current_palette_set.append(self._get_timed_palette(base_address))
                    base_address += 0x24         #skip over the duration dbyte, the palette, and the control code
                full_palette_set.extend(counter*current_palette_set)   #append the whole cycle and all its repetitions
            #fifth cycle is special (not really a cycle... just a single frame addition to the end)
            full_palette_set.append(self._get_timed_palette(base_address))

            return full_palette_set

        elif base_type == PaletteType.HEAT:
            if suit_type == SuitType.POWER:
                base_address = 0x8DE45E
            elif suit_type == SuitType.VARIA:
                base_address = 0x8DE68A
            elif suit_type == SuitType.GRAVITY:
                base_address = 0x8DE8B6
            else:
                raise AssertionError(f"function get_palette() called for heat palette with unknown suit type: {suit_type}")

            full_palette_set = []
            base_address += 8                #skip over the control codes
            return self._get_sequence_of_timed_palettes(base_addr, 16)

        elif base_type == PaletteType.CHARGE:
            if suit_type == SuitType.POWER:
                base_address = 0x9B9820
            elif suit_type == SuitType.VARIA:
                base_address = 0x9B9920
            elif suit_type == SuitType.GRAVITY:
                base_address = 0x9B9A20
            else:
                raise AssertionError(f"function get_palette() called for charge palette with unknown suit type: {suit_type}")

            #The charged shot palette advances every frame (determined by manual frame advance)
            return [(1,self._get_static_palette(base_address + i*0x20)) for i in range(8)]

        elif base_type == PaletteType.SPEED_BOOST:
            if suit_type == SuitType.POWER:
                base_address = 0x9B9B20
            elif suit_type == SuitType.VARIA:
                base_address = 0x9B9D20
            elif suit_type == SuitType.GRAVITY:
                base_address = 0x9B9F20
            else:
                raise AssertionError(f"function get_palette() called for speed boost palette with unknown suit type: {suit_type}")

            #4 frames each during the warm up, then stay at last palette forever (determined by manual frame advance)
            return [(4,self._get_raw_palette(base_address + i*0x20)) for i in range(3)] + \
                         [(0,self._get_raw_palette(base_address + 0x60))]

        elif base_type == PaletteType.SPEED_SQUAT:
            if suit_type == SuitType.POWER:
                base_address = 0x9B9BA0
            elif suit_type == SuitType.VARIA:
                base_address = 0x9B9DA0
            elif suit_type == SuitType.GRAVITY:
                base_address = 0x9B9FA0
            else:
                raise AssertionError(f"function get_palette() called for speed squat palette with unknown suit type: {suit_type}")

            #timing and order determined by manual frame advance.  One frame each, oscillates between 0 and 3
            return [(1,self._get_raw_palette(base_address + i*0x20)) for i in [0,1,2,3,2,1]]

        elif base_type == PaletteType.SHINE_SPARK:
            if suit_type == SuitType.POWER:
                base_address = 0x9B9C20
            elif suit_type == SuitType.VARIA:
                base_address = 0x9B9E20
            elif suit_type == SuitType.GRAVITY:
                base_address = 0x9BA020
            else:
                raise AssertionError(f"function get_palette() called for shine spark palette with unknown suit type: {suit_type}")

            #timing and order determined by manual frame advance.  1 frame each, goes 0 to 3 then resets
            return [(1,self._get_raw_palette(base_address + i*0x20)) for i in range(4)]

        elif base_type == PaletteType.SCREW_ATTACK:
            if suit_type == SuitType.POWER:
                base_address = 0x9B9CA0
            elif suit_type == SuitType.VARIA:
                base_address = 0x9B9EA0
            elif suit_type == SuitType.GRAVITY:
                base_address = 0x9BA0A0
            else:
                raise AssertionError(f"function get_palette() called for screw attack palette with unknown suit type: {suit_type}")

            #timing and order determined by manual frame advance.  One frame each, oscillates between 0 and 3
            return [(1,self._get_raw_palette(base_address + i*0x20)) for i in [0,1,2,3,2,1]]

        elif base_type == PaletteType.HYPER_BEAM:
            base_address = 0x9BA240
            
            #timing and order determined by manual frame advance.  Each frame goes down 1, overall from 9 to 0 then resets
            return [(1,self._get_raw_palette(base_address + i*0x20)) for i in range(9,-1,-1)]

        elif base_type == PaletteType.DEATH_SUIT:
            #the colors for the exploding suit pieces can be set to different palettes.

            #To retrieve these palettes, first need to grab the pointers to the palettes
            if suit_type == SuitType.POWER:
                palette_list_pointer = 0x9BB7D3
            elif suit_type == SuitType.VARIA:
                palette_list_pointer = 0x9BB7E7
            elif suit_type == SuitType.GRAVITY:
                palette_list_pointer = 0x9BB7FB
            else:
                raise AssertionError(f"function get_palette() called for screw attack palette with unknown suit type: {suit_type}")

            #There are ten pointers in total, grab them all
            palette_list = [0x9B0000 + offset for offset in self.read_from_snes_address(palette_list_pointer, "2"*10)]

            #ironically, the code doesn't even use all of these palettes, because that is determined by the next parameters
            full_palette_set = []
            for i in range(9):
                durations,palette_index = self.read_from_snes_address(0x9BB823 + 2*i,"11")
                full_palette_set.append(duration,palette_list[palette_index])

            return full_palette_set

        elif base_type == PaletteType.DEATH_FLESH:
            palette_list_pointer = 0x9BB80F
            
            #There are ten pointers in total, grab them all
            palette_list = [0x9B0000 + offset for offset in self.read_from_snes_address(palette_list_pointer, "2"*10)]

            #ironically, the code doesn't even use all of these palettes, because that is determined by the next parameters
            full_palette_set = []
            for i in range(9):
                durations,palette_index = self.read_from_snes_address(0x9BB823 + 2*i,"11")
                full_palette_set.append(duration,palette_list[palette_index])

            return full_palette_set

        elif base_type == PaletteType.CRYSTAL_FLASH:
            #timing determined by manual frame advance
            return [(2,self._get_raw_palette(0x9B96C0 + i*0x20)) for i in range(6)]

        elif base_type == PaletteType.SEPIA:
            return self._get_static_palette(0x8CE569)

        elif base_type == PaletteType.SEPIA_HURT:
            return self._get_static_palette(0x9BA380)

        elif base_type == PaletteType.SEPIA_ALTERNATE:
            return self._get_static_palette(0x9BA3A0)

        elif base_type == PaletteType.DOOR:
            visor_color = self.read_from_snes_address(0x82E52B, 2)
            base_colors = [0 for _ in range(16)]   #use 0 as the base color...technically this fades upwards into the suit color
            base_colors[4] = visor_color
            return [(0, base_colors)]

        elif base_type == PaletteType.XRAY:
            _,base_palette = self.get_palette(PaletteType.STANDARD, suit_type)[0]    #recurse to get the regular suit palette
            visor_colors = self.read_from_snes_address(0x9BA3C6, "222")
            #I did manual frame advances to learn that the duration is 6 frames for each visor color
            return [(6, base_palette[:4]+[color]+base_palette[5:]) for color in visor_colors]

        elif base_type == PaletteType.FILE_SELECT:
            return self._get_static_palette(0x8EE5E0)

        elif base_type == PaletteType.SHIP:
            base_palette_address = 0xA2A59E    #yes, way over here
            ship_underglow_address = 0x8DCA4E  #yes, way over there

            base_palette = self.read_from_snes_address(base_palette_address,"2"*15)  #intentionally skipping last color

            ship_underglow_address += 2    #skip over the control codes
            full_palette_set = []
            for i in range(14):
                #now what you're going to get is a list of duration, color, control code (2 bytes each, 14 in total)
                duration, glow_color = self.read_from_snes_address(ship_underglow_address + 6*i, "22")
                #the glow color appends at the final index (index 15)
                full_palette_set.append((duration,base_palette+[glow_color]))

            return full_palette_set
            
        elif base_type == PaletteType.INTRO_SHIP:
            #Technically the thrusters alternate white and black every frame, but this is a bit much on the eyes
            return self._get_static_palette(0x8CE68B)

        elif base_type == PaletteType.OUTRO_SHIP:
            base_address = 0x8DD6BA
            base_address += 2       #skip the control codes
            return self._get_sequence_of_timed_palettes(base_address, 16)

        else:
            raise AssertionError(f"function get_palette() called with unknown palette type: {base_type}")


    def _get_static_palette(self, snes_addr):
        return (0, self._get_raw_palette(snes_addr))

    def _get_timed_palette(self, snes_addr):
        duration = self.read_from_snes_address(snes_addr, 2)
        palette = self._get_raw_palette(snes_addr + 2)
        return (duration,palette)

    def _get_sequence_of_timed_palettes(self, snes_addr, num_palettes):
        #adding 0x24 skips over the duration dbyte, previous palette, and the control code each time
        return [self._get_timed_palette(base_address + 0x24*i) for i in range(num_palettes)]
        

    def _get_raw_palette(self,snes_addr):
        return self.read_from_snes_address(snes_addr, "2"*0x10)


    def _get_pose_tilemaps(self,animation,pose):
        lower_tilemaps = self._get_pose_tilemaps_from_addr(0x92945D, animation, pose)
        upper_tilemaps = self._get_pose_tilemaps_from_addr(0x929263, animation, pose)

        #special case here for elevator poses, they have this extra stupid tile
        #the position is hardcoded into the game at a block starting at $90:868D.
        #I did not make the code go in there and dig out the offsets because this tile is stupid.
        if animation in [0x00, 0x9B]:  #elevator poses (power suit/upgraded suit)
            stupid_tile_tilemap = [[0xF9,0x01,0xF5,0x21,0x38]]   #stupid offsets
        else:
            stupid_tile_tilemap = []
        
        #the tiles are rendered in this specific order: backwards lower, backwards upper
        return lower_tilemaps[::-1] + stupid_tile_tilemap + upper_tilemaps[::-1]   


    def _get_pose_tilemaps_from_addr(self, base_addr, animation, pose):
        #get the pointer to the list of pose pointers (in disassembly: get P??_UT or P??_LT)
        animation_all_poses_index = self.read_from_snes_address(base_addr + 2*animation, 2)
        #now get the specific pointer to the tilemap set (in disassembly: get TM_???)
        pose_tilemaps_pointer = 0x920000 + self.read_from_snes_address(0x92808D + 2*animation_all_poses_index, 2)
        #now use that pointer to find out how many tilemaps there actually are
        if pose_tilemaps_pointer == 0x920000:    #as will be the case when the pointer is zero, specifying no tiles here
            num_tilemaps = 0
        else:
            num_tilemaps = self.read_from_snes_address(pose_tilemaps_pointer, 2)
        #and now get the tilemaps!  They start right after the word specifying their number
        return [self.read_from_snes_address(pose_tilemaps_pointer + 2 + 5*i, "11111") for i in range(num_tilemaps)]


    def _get_dma_data(self,animation,pose):
        #get the pointer to the big list of table indices (in disassembly: get AFP_T??)
        animation_frame_progression_table = 0x920000 + self.read_from_snes_address(0x92D94E, 2)
        #get two sets of table/entry indices for use in the DMA table
        top_DMA_table, top_DMA_entry, bottom_DMA_table, bottom_DMA_entry = self.read_from_snes_address(animation_frame_progression_table,"1111")
        #get the data for each part
        DMA_writes = {}
        for (base_addr, table, entry, vram_offset) in \
                                        [(0x92D938, bottom_DMA_table, bottom_DMA_entry, 0x08), #lower body VRAM
                                         (0x92D91E, top_DMA_table,    top_DMA_entry,    0x00)]: #upper body VRAM
            #reference the first index to figure out where the relevant DMA table is
            this_DMA_table = 0x920000 + self.read_from_snes_address(base_addr,2)
            #From this table, get the appropriate entry in the list which contains the DMA pointer and the row sizes
            DMA_pointer, row1_size, row2_size = self.read_from_snes_address(this_DMA_table + 7 * pose, "322")
            #Read the DMA data
            row1 = self.read_from_snes_address(DMA_pointer, "1"*row1_size)
            row2 = self.read_from_snes_address(DMA_pointer+row1_size, "1"*row2_size)

            #add the DMA write information to the dictionary
            DMA_writes[vram_offset] = row1
            DMA_writes[0x10+vram_offset] = row2
            
        return DMA_writes


    def _get_pose_duration(self,animation, pose):
        #get the duration list pointer (FD_?? in disassembly)
        duration_list_location = self._get_duration_list_location(animation)
        return self.read_from_snes_address(duration_list_location,1)
    
        
    def _get_duration_list_location(self, animation):
        return 0x910000 + self.read_from_snes_address(0x91B010 + 2* animation,2)


    def _apply_single_fix_to_snes_address(self, snes_address, classic_values, fixed_values, encoding):
        #checks to see if, indeed, a value is still in the classic (bugged) value, and if so, fixes it
        #returns True if the fix was affected and False otherwise

        #first make sure the input makes sense -- either all integers or matching length lists
        if type(encoding) is not int and len(classic_values) != len(fixed_values):
            raise AssertionError(f"function _apply_single_fix_to_snes_address() called with different length lists:\n{classic_values}\n{fixed_values}")

        if self.read_from_snes_address(snes_address, encoding) == classic_values:
            self.write_to_snes_address(snes_address, fixed_values, encoding)
            return True
        else:
            return False


    def _apply_improvements(self):
        #these are not mandatory for the animation viewer to work, but they are general quality of life improvements
        # that I recommend to make.

        '''
        ;E508
        AFP_T31:;Midair morphball facing right without springball
        AFP_T32:;Midair morphball facing left without springball
        '''
        #this bug preventing left and right morphball from being different, but now we fix this

        self._apply_single_fix_to_snes_address(0x92D9B2,0xE508,0xE530,2)

        '''
        ;$B361
        FD_6D:  ;Falling facing right, aiming upright
        FD_6E:  ;Falling facing left, aiming upleft
        FD_6F:  ;Falling facing right, aiming downright
        FD_70:  ;Falling facing left, aiming downleft
        DB $02, $F0, $10, $FE, $01 
        '''
        #the second byte here was probably supposed to be $10, just like the animations above it.
        #$F0 is a terminator, and this is the only time that $F0 would ever be invoked (also, there is a pose in this spot!)

        original_values = [0x02,0xF0,0x10,0xFE,0x01]
        fixed_values    = [0x02,0x10,0x10,0xFE,0x01]
        self._apply_single_fix_to_snes_address(0x91B361,original_values,fixed_values,"11111")

        '''
        ;c9db
        XY_P00:     ;00:;Facing forward, ala Elevator pose (power suit)
        XY_P9B:     ;9B:;Facing forward, ala Elevator pose (Varia and/or Gravity Suit)
        DB $00, $02 
        '''
        #the second byte here is supposed to be 00, but because it is not, the missile port is rendered behind Samus's left
        # fist during elevator pose.
        self._apply_single_fix_to_snes_address(0x90c9db,[0x00,0x02],[0x00,0x00],"11")



    def _apply_bugfixes(self):
        #these are significant typos that reference bad palettes or similar, and would raise assertion errors in any clean code

        '''
        TM_193:
        DW $0001  
        DB $F8, $01, $F8, $00, $30 
        '''
        #last byte should be $28, like everything else
        original_values = [0xF8,0x01,0xF8,0x00,0x30]
        fixed_values    = [0xF8,0x01,0xF8,0x00,0x28]
        self._apply_single_fix_to_snes_address(0x92BEC1,original_values,fixed_values,"11111")


        '''
        TM_181:
        DW $0001  
        DB $F8, $01, $F8, $00, $10 
        '''
        #last byte should be $28, like everything else
        original_values = [0xF8,0x01,0xF8,0x00,0x10]
        fixed_values    = [0xF8,0x01,0xF8,0x00,0x28]
        self._apply_single_fix_to_snes_address(0x92BC7C,original_values,fixed_values,"11111")


        '''
        TM_0DA:
        DW $0004  
        DB $FD, $01, $0F, $0A, $78 
        '''
        #last byte should be $68, like everything else
        original_values = [0xFD,0x01,0x0F,0x0A,0x78]
        fixed_values    = [0xFD,0x01,0x0F,0x0A,0x68]
        self._apply_single_fix_to_snes_address(0x92AEE3,original_values,fixed_values,"11111")


        '''
        TM_06F:
        DW $0001  
        DB $F8, $01, $F8, $00, $30 
        '''
        #last byte should be $38, just like the other elevator poses
        original_values = [0xF8,0x01,0xF8,0x00,0x30]
        fixed_values    = [0xF8,0x01,0xF8,0x00,0x38]
        self._apply_single_fix_to_snes_address(0x92A12E,original_values,fixed_values,"11111")
