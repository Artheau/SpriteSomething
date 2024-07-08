#Originaly writtn by Artheau
#in Aprl 2019
#wile his brain and lettrs wer slpping awy

#includes routines that load the rom and apply bugfixes
#inherits from the generic romhandler

if __name__ == "__main__":
    raise AssertionError(f"Called main() on utility library {__file__}")

import enum
from source.snes import romhandler as snes

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
    SHINESPARK = enum.auto()         #flying through the air crazy-like
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

class RomHandler(snes.RomHandlerParent):
    def __init__(self, filename):
        super().__init__(filename)      #do the usual stuff

        self._apply_bugfixes()
        self._apply_improvements()

    def get_pose_data(self,animation,pose,port_frame=0,upper=True,lower=True):
        tilemaps = self._get_pose_tilemaps(animation,pose,upper=upper,lower=lower)
        DMA_writes = self._get_dma_data(animation, pose)
        duration = self._get_pose_duration(animation, pose)

        if port_frame > 0:
            gun_tilemap, gun_tile, gun_DMA = self.get_gun_data(animation, pose)
            if gun_tilemap:
                tilemaps.append(gun_tilemap)       #join the tilemap at the end, as it will sit over the other tiles
                DMA_writes[gun_tile] = gun_DMA       #join the DMA info at the end, as it overwrites the normal DMA

        return tilemaps, DMA_writes, duration

    def get_default_vram_data(self, equipped_weapon = "standard"):
        #go in and get the data that is by default loaded into the VRAM.
        #Except for stupid tile, this shouldn't be rendered as part of a Samus pose
        # unless something is glitched out (by this I mean a game glitch, not a bug in my code)
        # in which case the data here will depend upon what kind of weapon Samus has equipped

        #main population is from data starting at D5200-D71FF LOROM (populates from 0x00 on)
        #Note: grapple beam (e.g. $D0200 LOROM) can overwrite parts of row 2, and Mode 7 rooms (e.g. $183A00 LOROM)
        # can load "sprites" into the last three rows.  Rain can also go in row 0xD0
        DMA_writes = {0x00: self.bulk_read_from_snes_address(0x9AD200,0x2000)}

        #row 0x30 is populated with 8 tiles depending upon equipped weapon (0x30-0x37)
        equipped_weapon_switcher = {
            "regular": 0x9AF200,
            "standard": 0x9AF200,
            "charge": 0x9AF200,

            "ice": 0x9AF400,
            "wave": 0x9AF600,
            "plasma": 0x9AF800,
            "spazer": 0x9AFA00
        }
        snes_address = equipped_weapon_switcher.get(equipped_weapon)
        DMA_writes[0x30] = self.bulk_read_from_snes_address(snes_address,0x100)

        return DMA_writes

    def get_pose_control_data(self,animation,pose):
        #similar to get_pose_duration, except that this returns a list containing the pose control code
        # and its accompanying arguments in a list
        duration_list_location = self._get_duration_list_location(animation)
        control_code = self.read_from_snes_address(duration_list_location+pose,1)

        control_code_switcher = {
            0xF8: "11", #these codes have one byte-sized argument
            0xFD: "11",
            0xFE: "11",

            0xF9: "121111", #has one word and 4 byte arguments
            0xFA: "111", #two byte arguments
            0xFC: "1211" #one word and 2 byte arguments
        }
        read_type = control_code_switcher.get(control_code)

        if read_type:
            return self.read_from_snes_address(duration_list_location+pose, read_type)
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
            gun_tile = None
            gun_DMA = None
        elif priority != 0x01:
            # FIXME: English
            raise AssertionError(f"get_gun_port() called for data that has non-one priority {priority}")
        else:
            direction = direction & 0x7F   #need to clear out that high bit for the rest of this

            #now what is left is a list of xy pairs.  we can just grab what we need.
            x_position, y_position = self.read_from_snes_address(cannon_position_pointer + 2*(pose+1), "11")


            level_of_opening = min(2, frame//4)

            tile, palette, gun_tile, gun_DMA = self.get_minimal_gun_data(direction, level_of_opening)

            #construct the full tilemap
            x_high_bit = 1 if x_position >= 0x80 else 0
            tilemap = [x_position, x_high_bit, y_position, tile, palette]

        return tilemap, gun_tile, gun_DMA

    def get_minimal_gun_data(self, direction, level):
        # FIXME: English
        if level not in range(3):
            raise AssertionError(f"get_minimal_gun_data() called with invalid level value {level}")
        if direction not in range(10):
            raise AssertionError(f"get_minimal_gun_data() called with invalid direction value {direction}")
        tile, palette = self.read_from_snes_address(0x90C791+2*direction, "11")

        #need DMA info
        DMA_list = 0x900000 + self.read_from_snes_address(0x90C7A5 + 2*direction, 2)
        DMA_pointer = 0x9A0000 + self.read_from_snes_address(DMA_list + 2*(level+1), 2)

        #this is where the tile is loaded into in VRAM
        gun_tile = (self.read_from_snes_address(0x90C786,2)-0x6000)//0x10

        #this is the actual graphics data for the tile
        gun_DMA = self.read_from_snes_address(DMA_pointer, "1"*0x20)

        return tile, palette, gun_tile, gun_DMA

    def get_death_data(self, pose, facing='left', suit=SuitType.POWER):
        #get tilemap
        if facing[0] in ['l','L']:
            tilemaps = self._get_pose_tilemaps_from_addr(0x92EDDB, 0, pose)
        elif facing[0] in ['r','R']:
            tilemaps = self._get_pose_tilemaps_from_addr(0x92EDD0, 0, pose)
        else:
            # FIXME: English
            raise AssertionError(f"received call to get_death_data() with invalid facing {facing}")

        #get DMA data
        DMA_writes = {}
        write_size = self.read_from_snes_address(0x9BB6DF,2)
        bank = self.read_from_snes_address(0x9BB6EF, 1)
        if self.read_from_snes_address(0x9BB6E5,"12") == [0xB9, 0xB7BF]:   #classic
            classic = True
            DMA_loc_list = 0x9BB7BF
        elif self.read_from_snes_address(0x9BB6E5,1) == 0x20:    #modified ROM, have to go into the JSR and pull out the pointers
            classic = False
            search_loc = 0x9B0000 + self.read_from_snes_address(0x9BB6E6,2)
            search_size = min(0x100, 0x9C0000 - search_loc)
            search_array = self.bulk_read_from_snes_address(search_loc, search_size)
            DMA_cue = search_array.index(0xB9)
            if facing == 'right':   #go to the second ref
                DMA_cue = DMA_cue+1 + search_array[DMA_cue+1:].index(0xB9)
            DMA_loc_list = 0x9B0000 + search_array[DMA_cue+1] + search_array[DMA_cue+2]*0x100
        else:
            # FIXME: English
            raise AssertionError("cannot find the DMA location of the death sequence tiles")

        dest_tile_sequence_loc = 0x9B0000 + self.read_from_snes_address(0x9BB6F6, 2)
        for i in range(5 if classic else 0x10):   #classically, there are 5 double rows, but the modifications expand this to 16
            dest_tile = (self.read_from_snes_address(dest_tile_sequence_loc+2*i,2) - 0x6000)//0x10
            source_data = (bank * 0x10000) + self.read_from_snes_address(DMA_loc_list+2*i,2)
            DMA_writes[dest_tile] = self.read_from_snes_address(source_data, "1"*write_size)

        #how long to hold this pose, and an index to which palette to use
        duration, palette_index = self.read_from_snes_address(0x9BB823 + 2*pose, "11") # FIXME: palette_index unused variable

        return tilemaps[::-1], DMA_writes, duration

    def get_file_select_dma_data(self):
        #classically, the file select DMA data is located at $B6:C000.  However, many hacks relocate this to make more room for pause menu graphics.
        file_select_data_location = self.read_from_snes_address(0x818E34, 3)
        return {0x00: self.read_from_snes_address(file_select_data_location, "1"*0x2000)}

    def get_file_select_tilemaps(self, item):
        #For now, I have just coded these up by hand because it does not seem worth it to extract this information dynamically
        #8/31/2019: Maybe I should have extracted them dynamically because I coded it wrong by hand the first time *facepalm*
        palette = 0x22                              #this is more for convenience -- they are not actually on this palette
        if item in [0,1,2]:   #the Samus heads
            return [[0x08*i,
                     0x00,
                     0x08*j,
                     0xD0+i+0x10*j+3*item,
                     palette]
                      for i in range(3) for j in range(3)]
        if item in [3,4,5,6,7]:   #the Samus visors
            item_col = (item-3)//3
            item_row = (item-3)%3
            return [[4+0x08*i,
                     0x00,
                     10,
                     0xD9+i+2*item_row+0x10*item_col,
                     palette]
                      for i in range(2)]
        if item in [8]: #cursor
            return [[0x00,0x00,0x18,0xFE,palette],
                    [0x00,0x00,0x10,0xEE,palette],
                    [0x00,0x00,0x08,0xDF,palette],
                    [0x00,0x00,0x00,0xC8,palette],
                    [0x08,0x00,0x18,0xCC,palette],
                    [0x08,0x00,0x10,0xFF,palette],
                    [0x08,0x00,0x08,0xEF,palette]]
        if item in [9]: #pipe framework
            return [[0x00,0x00,0x00,0xF9,palette],
                    [0x08,0x00,0x00,0xFA,palette],
                    [0x10,0x00,0x00,0xFB,palette],
                    [0x10,0x00,0x08,0xED,palette],
                    [0x00,0x00,0x10,0xFC,palette],
                    [0x10,0x00,0x10,0xFD,palette]]
        # FIXME: English
        raise AssertionError(f"get_file_select_tilemaps() called for unknown item number {item}")

    def get_palette(self, base_type, suit_type):
        #interface to provide a string-based function to external callers
        base_type = base_type.upper().replace(" ", "_") if isinstance(base_type,str) else "STANDARD"
        suit_type = suit_type.upper().replace(" ", "_") if isinstance(suit_type,str) else "POWER"

        return self.get_palette_from_enum(getattr(PaletteType,base_type), getattr(SuitType,suit_type))

    def get_palette_from_enum(self, base_type, suit_type):
        #returns a list.  Each element of the list is a tuple, where the first entry is the amount of time that the palette
        # should display for (here $00 is a special case for static palettes).  The second entry is the 555 palette data.

        PALETTE_READ_SIZE = "2"*0x10 # FIXME: unused variable

        if base_type == PaletteType.STANDARD:
            suit_type_switcher = {
                SuitType.POWER: 0x9B9400,
                SuitType.VARIA: 0x9B9520,
                SuitType.GRAVITY: 0x9B9800
            }
            # FIXME: English
            base_address = suit_type_switcher.get(suit_type)
            if base_address is None:
                raise AssertionError(f"function get_palette_from_enum() called for standard palette with unknown suit type: {suit_type}")
            return [self._get_static_palette(base_address)]

        if base_type == PaletteType.LOADER:
            suit_type_switcher = {
                SuitType.POWER: 0x8DDB62,
                SuitType.VARIA: 0x8DDCC8,
                SuitType.GRAVITY: 0x8DDE2E
            }
            # FIXME: English
            base_address = suit_type_switcher.get(suit_type)
            if base_address is None:
                raise AssertionError(f"function get_palette_from_enum() called for loader palette with unknown suit type: {suit_type}")

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
            base_address += 4  #skip over the final control codes
            full_palette_set.append(self._get_timed_palette(base_address))

            full_palette_set.append((0,full_palette_set[0][1]))   #don't keep flashing forever (for the animator)

            return full_palette_set

        if base_type == PaletteType.HEAT:
            suit_type_switcher = {
                SuitType.POWER: 0x8DE45E,
                SuitType.VARIA: 0x8DE68A,
                SuitType.GRAVITY: 0x8DE8B6
            }
            # FIXME: English
            base_address = suit_type_switcher.get(suit_type)
            if base_address is None:
                raise AssertionError(f"function get_palette_from_enum() called for heat palette with unknown suit type: {suit_type}")

            full_palette_set = []
            base_address += 8                #skip over the control codes
            return self._get_sequence_of_timed_palettes(base_address, 16, add_transparency=True)  #heat is not coded with transparency

        if base_type == PaletteType.CHARGE:
            suit_type_switcher = {
                SuitType.POWER: 0x9B9820,
                SuitType.VARIA: 0x9B9920,
                SuitType.GRAVITY: 0x9B9A20
            }
            # FIXME: English
            base_address = suit_type_switcher.get(suit_type)
            if base_address is None:
                raise AssertionError(f"function get_palette_from_enum() called for charge palette with unknown suit type: {suit_type}")

            #The charged shot palette advances every frame (determined by manual frame advance)
            return [(1,self._get_raw_palette(base_address + i*0x20)) for i in range(8)]

        if base_type == PaletteType.SPEED_BOOST:
            suit_type_switcher = {
                SuitType.POWER: 0x9B9B20,
                SuitType.VARIA: 0x9B9D20,
                SuitType.GRAVITY: 0x9B9F20
            }
            # FIXME: English
            base_address = suit_type_switcher.get(suit_type)
            if base_address is None:
                raise AssertionError(f"function get_palette_from_enum() called for speed boost palette with unknown suit type: {suit_type}")

            #4 frames each during the warm up, then stay at last palette forever (determined by manual frame advance)
            return [(4,self._get_raw_palette(base_address + i*0x20)) for i in range(3)] + \
                         [(0,self._get_raw_palette(base_address + 0x60))]

        if base_type == PaletteType.SPEED_SQUAT:
            suit_type_switcher = {
                SuitType.POWER: 0x9B9BA0,
                SuitType.VARIA: 0x9B9DA0,
                SuitType.GRAVITY: 0x9B9FA0
            }
            # FIXME: English
            base_address = suit_type_switcher.get(suit_type)
            if base_address is None:
                raise AssertionError(f"function get_palette_from_enum() called for speed squat palette with unknown suit type: {suit_type}")

            #timing and order determined by manual frame advance.  One frame each, oscillates between 0 and 3
            return [(1,self._get_raw_palette(base_address + i*0x20)) for i in [0,1,2,3,2,1]]

        if base_type == PaletteType.SHINESPARK:
            suit_type_switcher = {
                SuitType.POWER: 0x9B9C20,
                SuitType.VARIA: 0x9B9E20,
                SuitType.GRAVITY: 0x9BA020
            }
            # FIXME: English
            base_address = suit_type_switcher.get(suit_type)
            if base_address is None:
                raise AssertionError(f"function get_palette_from_enum() called for shine spark palette with unknown suit type: {suit_type}")

            #timing and order determined by manual frame advance.  1 frame each, goes 0 to 3 then resets
            return [(1,self._get_raw_palette(base_address + i*0x20)) for i in range(4)]

        if base_type == PaletteType.SCREW_ATTACK:
            suit_type_switcher = {
                SuitType.POWER: 0x9B9CA0,
                SuitType.VARIA: 0x9B9EA0,
                SuitType.GRAVITY: 0x9BA0A0
            }
            # FIXME: English
            base_address = suit_type_switcher.get(suit_type)
            if base_address is None:
                raise AssertionError(f"function get_palette_from_enum() called for screw attack palette with unknown suit type: {suit_type}")

            #timing and order determined by manual frame advance.  One frame each, oscillates between 0 and 3
            return [(1,self._get_raw_palette(base_address + i*0x20)) for i in [0,1,2,3,2,1]]

        if base_type == PaletteType.HYPER_BEAM:
            base_address = 0x9BA240

            #timing and order estimated by Youtube frame advance.  Each frame goes down 1, overall from 9 to 0 then resets
            return [(2,self._get_raw_palette(base_address + i*0x20)) for i in range(9,-1,-1)]

        if base_type == PaletteType.DEATH_SUIT:
            #the colors for the exploding suit pieces can be set to different palettes.

            #To retrieve these palettes, first need to grab the pointers to the palettes
            suit_type_switcher = {
                SuitType.POWER: 0x9BB7D3,
                SuitType.VARIA: 0x9BB7E7,
                SuitType.GRAVITY: 0x9BB7FB
            }
            # FIXME: English
            base_address = suit_type_switcher.get(suit_type)
            if base_address is None:
                raise AssertionError(f"function get_palette_from_enum() called for death suit palette with unknown suit type: {suit_type}")

            #There are ten pointers in total, grab them all
            palette_list = [0x9B0000 + offset for offset in self.read_from_snes_address(palette_list_pointer, "2"*10)]

            #ironically, the code doesn't even use all of these palettes, because that is determined by the next parameters
            full_palette_set = []
            for i in range(9):
                duration,palette_index = self.read_from_snes_address(0x9BB823 + 2*i,"11")
                full_palette_set.append(duration,palette_list[palette_index])

            return full_palette_set

        if base_type == PaletteType.DEATH_FLESH:
            palette_list_pointer = 0x9BB80F

            #There are ten pointers in total, grab them all
            palette_list = [0x9B0000 + offset for offset in self.read_from_snes_address(palette_list_pointer, "2"*10)]

            #ironically, the code doesn't even use all of these palettes, because that is determined by the next parameters
            full_palette_set = []
            for i in range(9):
                duration,palette_index = self.read_from_snes_address(0x9BB823 + 2*i,"11")
                full_palette_set.append((duration,self._get_raw_palette(palette_list[palette_index])))

            return full_palette_set

        if base_type == PaletteType.CRYSTAL_FLASH:
            #timing determined by manual frame advance
            return [(2,self._get_raw_palette(0x9B96C0 + i*0x20)) for i in range(6)]

        if base_type == PaletteType.SEPIA:
            return [self._get_static_palette(0x8CE569)]

        if base_type == PaletteType.SEPIA_HURT:
            return [self._get_static_palette(0x9BA380)]

        if base_type == PaletteType.SEPIA_ALTERNATE:
            return [self._get_static_palette(0x9BA3A0)]

        if base_type == PaletteType.DOOR:
            visor_color = self.read_from_snes_address(0x82E52C, 2)
            base_colors = [0 for _ in range(16)]   #use 0 as the base color...technically this fades upwards into the suit color
            base_colors[4] = visor_color
            return [(0, base_colors)]

        if base_type == PaletteType.XRAY:
            _,base_palette = self.get_palette_from_enum(PaletteType.STANDARD, suit_type)[0]    #recurse to get the regular suit palette
            visor_colors = self.get_nightvisor_colors()
            #I did manual frame advances to learn that the duration is 6 frames for each visor color
            return [(6, base_palette[:4]+[color]+base_palette[5:]) for color in visor_colors]

        if base_type == PaletteType.FILE_SELECT:
            return [self._get_static_palette(0x8EE5E0)]

        if base_type == PaletteType.SHIP:
            base_palette_address = 0xA2A59E    #yes, way over here
            ship_underglow_address = 0x8DCA4E  #yes, way over there

            base_palette = self.read_from_snes_address(base_palette_address,"2"*15)  #intentionally skipping last color

            ship_underglow_address += 4    #skip over the control codes
            full_palette_set = []
            for i in range(14):
                #now what you're going to get is a list of duration, color, control code (2 bytes each, 14 in total)
                duration, glow_color = self.read_from_snes_address(ship_underglow_address + 6*i, "22")
                #the glow color appends at the final index (index 15)
                full_palette_set.append((duration,base_palette+[glow_color]))

            return full_palette_set

        if base_type == PaletteType.INTRO_SHIP:
            #Technically the thrusters alternate white and black every frame, but this is a bit much on the eyes
            return [self._get_static_palette(0x8CE689)]

        if base_type == PaletteType.OUTRO_SHIP:
            base_address = 0x8DD6BA
            base_address += 4       #skip the control codes
            return self._get_sequence_of_timed_palettes(base_address, 16)

        # FIXME: English
        raise AssertionError(f"function get_palette_from_enum() called with unknown palette type: {base_type}")

    def get_nightvisor_colors(self):
        return self.read_from_snes_address(0x9BA3C6, "222")

    def _get_static_palette(self, snes_address):
        return (0, self._get_raw_palette(snes_address))

    def _get_timed_palette(self, snes_address, add_transparency=False):
        duration = self.read_from_snes_address(snes_address, 2)
        palette = self._get_raw_palette(snes_address + (0 if add_transparency else 2))  #some palettes don't have transparent pixels already in there
        return (duration,palette)

    def _get_sequence_of_timed_palettes(self, snes_address, num_palettes, add_transparency=False):
        #adding 0x24 skips over the duration dbyte, previous palette, and the control code each time
        skip_amount = 0x22 if add_transparency else 0x24
        return [self._get_timed_palette(snes_address + skip_amount*i, add_transparency=add_transparency) for i in range(num_palettes)]

    def _get_raw_palette(self,snes_address):
        return self.read_from_snes_address(snes_address, "2"*0x10)

    def _get_pose_tilemaps(self,animation,pose, upper=True, lower=True):
        lower_tilemaps = self._get_pose_tilemaps_from_addr(0x92945D, animation, pose)
        upper_tilemaps = self._get_pose_tilemaps_from_addr(0x929263, animation, pose)

        #special case here for elevator poses, they have this extra stupid tile
        #the position is hardcoded into the game at a block starting at $90:868D.
        #I did not make the code go in there and dig out the offsets because this tile is stupid.
        if animation == 0x00:
            if pose == 0:  #elevator pose (power suit only)
                stupid_tile_tilemap = [[0xF9,0x01,0xF5,0x21,0x38]]   #stupid offsets
            else:          #launcher pose (power suit only)
                stupid_tile_tilemap = [[0xF9,0x01,0xF0,0x21,0x38]]   #stupider offsets
        else:
            stupid_tile_tilemap = []

        #the tiles are rendered in this specific order: backwards lower, backwards upper
        return (lower_tilemaps[::-1] if lower else []) + stupid_tile_tilemap + (upper_tilemaps[::-1] if upper else [])

    def _get_pose_tilemaps_from_addr(self, base_addr, animation, pose):
        #get the pointer to the list of pose pointers (in disassembly: get P??_UT or P??_LT)
        animation_all_poses_index = self.read_from_snes_address(base_addr + 2*animation, 2)
        #now get the specific pointer to the tilemap set (in disassembly: get TM_???)
        pose_tilemaps_pointer = 0x920000 + self.read_from_snes_address(0x92808D + 2*animation_all_poses_index + 2*pose, 2)
        #now use that pointer to find out how many tilemaps there actually are
        if pose_tilemaps_pointer == 0x920000:    #as will be the case when the pointer is zero, specifying no tiles here
            num_tilemaps = 0
        else:
            num_tilemaps = self.read_from_snes_address(pose_tilemaps_pointer, 2)
        #and now get the tilemaps!  They start right after the word specifying their number
        return [self.read_from_snes_address(pose_tilemaps_pointer + 2 + 5*i, "11111") for i in range(num_tilemaps)]

    def _get_dma_data(self,animation,pose):
        #get the pointer to the big list of table indices (in disassembly: get AFP_T??)
        animation_frame_progression_table = 0x920000 + self.read_from_snes_address(0x92D94E + 2*animation, 2)
        #get two sets of table/entry indices for use in the DMA table
        top_DMA_table, top_DMA_entry, bottom_DMA_table, bottom_DMA_entry = self.read_from_snes_address(animation_frame_progression_table + 4*pose,"1111")
        #get the data for each part
        DMA_writes = {}
        for (base_addr, table, entry, vram_offset) in \
                                        [(0x92D938, bottom_DMA_table, bottom_DMA_entry, 0x08), #lower body VRAM
                                         (0x92D91E, top_DMA_table,    top_DMA_entry,    0x00)]: #upper body VRAM
            #reference the first index to figure out where the relevant DMA table is
            this_DMA_table = 0x920000 + self.read_from_snes_address(base_addr + 2*table,2)
            #From this table, get the appropriate entry in the list which contains the DMA pointer and the row sizes
            DMA_pointer, row1_size, row2_size = self.read_from_snes_address(this_DMA_table + 7 * entry, "322")
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
        return self.read_from_snes_address(duration_list_location+pose,1)

    def _get_duration_list_location(self, animation):
        return 0x910000 + self.read_from_snes_address(0x91B010 + 2* animation,2)

    def _apply_improvements(self):
        #these are not mandatory for the animation viewer to work, but they are general quality of life improvements
        # that I recommend to make.

        '''
        ;E508
        AFP_T31:;Midair morphball facing right without springball
        AFP_T32:;Midair morphball facing left without springball
        '''
        #this bug preventing left and right morphball from being different, but now we fix this
        #have to fix tilemaps too

        self._apply_single_fix_to_snes_address(0x92D9B2,0xE508,0xE530,2)
        self._apply_single_fix_to_snes_address(0x9292C7,0x0710,0x071A,2) #upper tilemap
        self._apply_single_fix_to_snes_address(0x9294C1,0x0710,0x071A,2) #lower tilemap

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
        self._apply_single_fix_to_snes_address(0x90C9DB,[0x00,0x02],[0x00,0x00],"11")

        #it is my intention to be as hands-off as possible with the positioning of the cannon port onto the sprite,
        # but the directly downwards aiming ones are super broken.
        #start by redirects to new XY lists
        #self._apply_single_fix_to_snes_address(0x90C80D,0xCAC5,0xCAC5,2)
        self._apply_single_fix_to_snes_address(0x90C80F,0xCACB,0xCB31,2)
        self._apply_single_fix_to_snes_address(0x90C839,0xCB31,0xCAC5,2)
        self._apply_single_fix_to_snes_address(0x90C83B,0xCB37,0xCB31,2)
        #new XY lists
        self._apply_single_fix_to_snes_address(0x90CAC5,[0x04,0x01,0x00,0x0D,0x00,0x0D,0x05,0x01],
                                                        [0x83,0x01,0x84,0x01,0x0B,0x01,0x00,0x0D], "11111111")
        self._apply_single_fix_to_snes_address(0x90CB31,[0x04,0x01,0x00,0x09,0x00,0x09,0x05,0x01],
                                                        [0x86,0x01,0x85,0x01,0xED,0x01,0xF7,0x0D], "11111111")

        #the application of the right-facing jump begin/jump land missile port placements is inconsistent
        # across the animations and in many animations is omitted.  These lines make this consistent by always omitting it
        self._apply_single_fix_to_snes_address(0x90CAD1, [0x03,0x01], [0x00,0x00], "11")
        self._apply_single_fix_to_snes_address(0x90CBF9, [0x03,0x01], [0x00,0x00], "11")
        self._apply_single_fix_to_snes_address(0x90CC05, [0x03,0x01], [0x00,0x00], "11")

        '''
        ;CBA5
        XY_P49:     ;49:;Moonwalk, facing left
        DB $02, $01
        DB $F1, $FD, $F1, $FC, $F1, $FC, $F1, $FD, $F1, $FC, $F1, $FC

        ;CBB3
        XY_P4A:     ;4A:;Moonwalk, facing right
        DB $07, $01
        DB $07, $FD, $07, $FC, $07, $FC, $07, $FD, $07, $FC, $07, $FC
        '''
        #in this case the cannon was actually placed onto the gun port backwards...
        self._apply_single_fix_to_snes_address(0x90CBA5,[0x02,0x01,0xF1,0xFD,0xF1,0xFC,0xF1,0xFC,0xF1,0xFD,0xF1,0xFC,0xF1,0xFC],
                                                        [0x07,0x01,0xED,0xFD,0xED,0xFC,0xED,0xFC,0xED,0xFD,0xED,0xFC,0xED,0xFC], "1"*14)
        self._apply_single_fix_to_snes_address(0x90CBB3,[0x07,0x01,0x07,0xFD,0x07,0xFC,0x07,0xFC,0x07,0xFD,0x07,0xFC,0x07,0xFC],
                                                        [0x02,0x01,0x0B,0xFD,0x0B,0xFC,0x0B,0xFC,0x0B,0xFD,0x0B,0xFC,0x0B,0xFC], "1"*14)

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
