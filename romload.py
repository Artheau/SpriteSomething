#Written by Artheau
#over several days in Feb. 2019
#while looking out the window and dreaming of being outside in the sunshine

#includes routines that load the rom and apply bugfixes

import shutil
import mmap
import os

def load_rom_contents(rom_filename,apply_fixes=True):
    new_rom_filename = "_modified".join(os.path.splitext(rom_filename))

    try:
        shutil.copyfile(rom_filename, new_rom_filename)
    except OSError:
        new_rom_filename = "_modified_second".join(os.path.splitext(rom_filename))
        shutil.copyfile(rom_filename, new_rom_filename)

    with open(new_rom_filename, "r+b") as f:
        rom = mmap.mmap(f.fileno(), 0)

    if apply_fixes:
        apply_bugfixes(rom)

    return rom

def apply_bugfixes(rom):
    fix_tilemaps(rom)
    fix_animation_sequences(rom)

def fix_tilemaps(rom):
    fix_tile_palettes(rom)
    fix_bouncing_shoulder_tiles(rom)
    fix_left_rolling_ball(rom)

def fix_animation_sequences(rom):
    fix_falling_facing_diagonal(rom)

def fix_falling_facing_diagonal(rom):
    '''
    FD_6D:  ;Falling facing right, aiming upright
    FD_6E:  ;Falling facing left, aiming upleft
    FD_6F:  ;Falling facing right, aiming downright
    FD_70:  ;Falling facing left, aiming downleft
    DB $02, $F0, $10, $FE, $01 
    '''
    #the second byte here was probably supposed to be $10, just like the animations above it.
    #$F0 is a terminator, and this is the only time that $F0 would ever be invoked (also, there is a pose in this spot!)
    rom[0x08B362] = 0x10                        #$91B362 LoROM


def fix_tile_palettes(rom):
    '''
    TM_193:
    DW $0001  
    DB $F8, $01, $F8, $00, $30 
    '''
    #last byte should be $28, like everything else
    rom[0x093EC5] = 0x28                         #$92BEC5 LoROM

    '''
    TM_181:
    DW $0001  
    DB $F8, $01, $F8, $00, $10 
    '''
    #last byte should be $28, like everything else
    rom[0x093C80] = 0x28                         #$92BC80 LoROM

    '''
    TM_0DA:
    DW $0004  
    DB $FD, $01, $0F, $0A, $78 
    '''
    #last byte should be $68, like everything else
    rom[0x092EE7] = 0x68                         #$92AEE7 LoROM

    '''
    TM_06F:
    DW $0001  
    DB $F8, $01, $F8, $00, $30 
    '''
    #last byte should be $38, just like the other elevator poses
    rom[0x92132] = 0x38                          #$92A132 LoROM

def fix_bouncing_shoulder_tiles(rom):
    #in the running and moonwalking animations, when the cannon is facing diagonally, the shoulderpad bounces 2 pixels
    #instead of moving with the torso, it sort of flops around.  Fixed by y-offsetting by 1 in the "middle" frame.
    
    '''
    TM_050:
    DW $0006  
    DB $FB, $01, $F9, $02, $28 
    DB $FB, $01, $F1, $03, $28 
    DB $F3, $01, $F1, $04, $28
    '''

    rom[0x091D02] = 0xFA            #$929D02 LoROM
    rom[0x091D07] = 0xF2            #$929D07 LoROM
    rom[0x091D0C] = 0xF2            #$929D0C LoROM

    '''
    TM_04F:
    DW $0005  
    DB $0C, $00, $E9, $02, $68 
    DB $FD, $01, $F6, $03, $28
    DB $FD, $01, $EE, $04, $28
    '''
    #the shoulderpad in this frame is also made out of only 2 tiles instead of 3,
    #but there is no room to fix that without re-engineering this part of the rom to add a byte
    rom[0x091CEC] = 0xF7            #$929CEC LoROM
    rom[0x091CF1] = 0xEF            #$929CF1 LoROM

    ''' 
    TM_045:
    DW $0006  
    DB $FD, $01, $F9, $02, $28 
    DB $05, $00, $F1, $03, $28 
    DB $FD, $01, $F1, $04, $28 
    '''
    rom[0x091BCF] = 0xFA            #$929BCF LoROM
    rom[0x091BD4] = 0xF2            #$929BD4 LoROM
    rom[0x091BD9] = 0xF2            #$929BD9 LoROM

    '''
    TM_046:
    DW $0006  
    DB $F1, $01, $FC, $02, $68 
    DB $ED, $01, $00, $03, $68 
    DB $FC, $01, $F9, $04, $28 
    DB $F4, $01, $F1, $05, $28 
    DB $FC, $01, $F1, $06, $28 
    '''
    #here the gun and shoulder are in a different order, but they do not overlap so it does not matter
    rom[0x091BF9] = 0xFA            #$929BF9 LoROM
    rom[0x091BFE] = 0xF2            #$929BFE LoROM
    rom[0x091C03] = 0xF2            #$929C03 LoROM


def fix_left_rolling_ball(rom):
    '''
    The following should not be linked -- left is in there accidentally with right.  Need to set this pointer correctly
    ;E508
    AFP_T1D:;Facing right as morphball, no springball
    AFP_T31:;Midair morphball facing right without springball
    AFP_T32:;Midair morphball facing left without springball
    '''
    rom[0x959B2:0x959B4] = bytes([0x30,0xE5])      #$92D9B2-$92D9B3 LoROM

def main():
    raise AssertionError("Compiled utility library directly")
    
if __name__ == "__main__":
    main()