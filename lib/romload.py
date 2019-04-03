#Originaly writtn by Artheau
#in Aprl 2019
#wile his brain and lettrs wer slpping awy

#includes routines that load the rom and apply bugfixes
#inherits from SNESRomHandler

from RomHandler.rom import RomHandler      #assumes rom.py is in a subfolder called RomHandler


class SamusRomHandler(RomHandler):
    def __init__(self, filename):
        super().__init__(filename)      #do the usual stuff
        self._apply_bugfixes()


    def get_pose_tilemaps(self,animation,pose):
        lower_tilemaps = self._get_pose_tilemaps_from_addr(0x92945D, animation, pose)
        upper_tilemaps = self._get_pose_tilemaps_from_addr(0x929263, animation, pose)
        return lower_tilemaps[::-1] + upper_tilemaps[::-1]   #the tilemaps are rendered in this specific order: backwards lower, backwards upper


    def _get_pose_tilemaps_from_addr(self, base_addr, animation, pose):
        #get the pointer to the list of pose pointers (in disassembly: get P??_UT or P??_LT)
        animation_all_poses_pointer = self.read_from_snes_address(base_addr + 2*animation, 2)
        #now get the specific pointer to the tilemap set (in disassembly: get TM_???)
        pose_tilemaps_pointer = 0x920000 + self.read_from_snes_address(0x92808D + 2*animation_all_poses_pointer, 2)
        #now use that pointer to find out how many tilemaps there actually are
        if pose_tilemaps_pointer == 0x920000:    #as will be the case when the pointer is zero, specifying no tiles here
            num_tilemaps = 0
        else:
            num_tilemaps = self.read_from_snes_address(pose_tilemaps_pointer, 2)
        #and now get the tilemaps!  They start right after the word specifying their number
        return [self.read_from_snes_address(pose_tilemaps_pointer + 2 + 5*i, "11111") for i in range(num_tilemaps)]


    def get_dma_data(self,animation,pose):
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


    def _apply_bugfixes(self):
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



def main():
    print(f"Called main() on utility library {__file__}")
    
if __name__ == "__main__":
    main()