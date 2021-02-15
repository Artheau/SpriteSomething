#includes routines that load the rom and apply bugfixes
#inherits from the generic romhandler

from source.snes import romhandler as snes

class RomHandler(snes.RomHandlerParent):
	def __init__(self, filename):
		super().__init__(filename)			#do the usual stuff

		self._apply_bugfixes()
		self._apply_improvements()

	def _apply_improvements(self):
		#these are not mandatory for the animation viewer to work, but they are general quality of life improvements
		# that I recommend to make.

		success_code = self.shared_player_palette_fix()

		return success_code

	def _apply_bugfixes(self):
		#these are significant typos that reference bad palettes or similar, and would raise assertion errors in any clean code
		return True

	def shared_player_palette_fix(self):
		#this only corrects errors in the J rom.	This could in theory be modified to fix errors in the U rom if the addresses
		# were changed

		success_code = True

		'''
		;Bee (Credits)
		;This puts the bee on the palette it uses in the rest of the game (bits 1-3)
		org $0ECFBA		;$74FBA in ROM
		db $76
		'''
		success_code &= self._apply_single_fix_to_snes_address(0x0ECFB6,[0x4A,0x29,0x40,0x49,0x7E],[0x4A,0x29,0x40,0x49,0x76],"11111")

		'''
		;Chests (Credits)
		;Gives them a much more natural color (bits 1-3)
		org $0ED35A		;7535A in ROM
		db $37
		org $0ED362		;75362 in ROM
		db $37
		org $0ED36A		;7536A in ROM
		db $37
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x0ED356,[0xFF,0xF4,0xFF,0x08,0x3F],[0xFF,0xF4,0xFF,0x08,0x37],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x0ED35E,[0x00,0xf4,0xff,0x20,0x3f],[0x00,0xf4,0xff,0x20,0x37],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x0ED366,[0x00,0xf4,0xff,0x20,0x3f],[0x00,0xf4,0xff,0x20,0x37],"11111")

		'''
		;Sweeping Woman (In-Game)
		;Puts her on the same color of red that she is in the ending credits (bits 1-3)
		org $0DB383		;6B383 in ROM
		db $07
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x0DB37F,[0x18,0x1b,0x41,0x47,0x0f],[0x18,0x1b,0x41,0x47,0x07],"11111")

		'''
		;Ravens (Credits)
		;Puts them on the same color as they are in-game (bits 1-3)
		org $0ED653		;75653 in ROM
		db $09
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x0ED64F,[0x4a,0x29,0x40,0x49,0x0f],[0x4a,0x29,0x40,0x49,0x09],"11111")

		'''
		;Running Man (In-Game)
		;Puts the jacket on the same palette as the hat
		;bits 1-3 are XORed with the base palette (currently 0b011)
		org $05E9DA		;2E9DA in ROM
		db $00
		org $05E9EA		;2E9EA in ROM
		db $40
		org $05E9FA		;2E9FA in ROM
		db $00
		org $05EA0A		;2EA0A in ROM
		db $40
		org $05EA1A		;2EA1A in ROM
		db $00
		org $05EA2A		;2EA2A in ROM
		db $00
		org $05EA3A		;2EA3A in ROM
		db $40
		org $05EA4A		;2EA4A in ROM
		db $40
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x05E9D6,[0x00,0x00,0x00,0xee,0x08],[0x00,0x00,0x00,0xee,0x00],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x05E9E6,[0x00,0x01,0x00,0xee,0x48],[0x00,0x01,0x00,0xee,0x40],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x05E9F6,[0x00,0x00,0x00,0xca,0x08],[0x00,0x00,0x00,0xca,0x00],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x05EA06,[0x00,0x01,0x00,0xca,0x48],[0x00,0x01,0x00,0xca,0x40],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x05EA16,[0x00,0x00,0x00,0xcc,0x08],[0x00,0x00,0x00,0xcc,0x00],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x05EA26,[0x00,0x01,0x00,0xce,0x08],[0x00,0x01,0x00,0xce,0x00],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x05EA36,[0x00,0x00,0x00,0xcc,0x48],[0x00,0x00,0x00,0xcc,0x40],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x05EA46,[0x00,0x01,0x00,0xce,0x48],[0x00,0x01,0x00,0xce,0x40],"11111")

		'''
		;Running Man (Credits Only)
		;Puts the jacket and the arm on the same palette as the hat (bits 1-3)
		org $0ECE72		;74E72 in ROM
		db $47
		org $0ECE8A		;74E8A in ROM
		db $07
		org $0ECE92		;74E92 in ROM
		db $07
		org $0ECEA2		;74EA2 in ROM
		db $47
		org $0ECEAA		;74EAA in ROM
		db $07
		org $0ECEBA		;74EBA in ROM
		db $47
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x0ECE6E,[0x00,0x00,0x00,0xca,0x4f],[0x00,0x00,0x00,0xca,0x47],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x0ECE86,[0x00,0x00,0x00,0xca,0x0f],[0x00,0x00,0x00,0xca,0x07],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x0ECE8E,[0xff,0x00,0x00,0x77,0x0f],[0xff,0x00,0x00,0x77,0x07],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x0ECE9E,[0x00,0x00,0x00,0xca,0x4f],[0x00,0x00,0x00,0xca,0x47],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x0ECEA6,[0xff,0x00,0x00,0x66,0x0f],[0xff,0x00,0x00,0x66,0x07],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x0ECEB6,[0x00,0x00,0x00,0xca,0x4f],[0x00,0x00,0x00,0xca,0x47],"11111")

		'''
		;Hoarder (when under a stone)
		;Complete fix
		;This was a bug that made the hoarder ignore its palette setting only when it was under a rock
		org $06AAAC		;32AAC in ROM
		db $F0
		;But now we have to give it the correct palette info (bits 1-3)
		org $06AA46		;32A46 in ROM
		db $0B
		org $06AA48		;32A48 in ROM
		db $0B
		org $06AA4A		;32A4A in ROM
		db $0B
		org $06AA4C		;32A4C in ROM
		db $0B
		org $06AA4E		;32A4E in ROM
		db $4B
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x06AAA8,[0x90,0xa5,0x05,0x29,0xfe],[0x90,0xa5,0x05,0x29,0xf0],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x06AA46,[0x03,0x0c,0x03,0x0c,0x03,0x0c,0x03,0x0c,0x43,0x0c],[0x0B,0x0c,0x0B,0x0c,0x0B,0x0c,0x0B,0x0c,0x4B,0x0c],10*"1")

		'''
		;Thief (friendly thief in cave)
		;There is a subtle difference in color here (more pastel)
		;His palette is given by bits 1-3
		org $0DC322		;6C322 in ROM
		db $07			;set him to red
		;Alternate palette options:
		;db $09			;lavender
		;db $0B			;green
		;db $0D 		;yellow (same as he is in the credits)
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x0DC31E,[0x9d,0xb0,0x0e,0xa9,0x0f],[0x9d,0xb0,0x0e,0xa9,0x07],"11111")

		'''
		;Pedestal Pull
		;This edit DOES create a visual difference
		;so I also present some alternate options
		;
		;
		;Option A: Fix the red pendant, but now it ignores shadows
		;and as a result, looks bugged
		;org $05893D	;2893D in ROM
		;db $07
		;
		;
		;Option B: Make the red pendant a yellow pendant
		;org $05893D	;2893D in ROM
		;db $0D
		;
		;
		;Option C: Also change the other pendants so that they all
		;ignore shadows.	This looks better because they appear to
		;glow even brighter
		;BUT I had to compromise on the color of the blue pendant
		org $058933		;28933 in ROM
		db $05			;change palette of blue pendant
		org $058938		;28938 in ROM
		db $01			;change palette of green pendant
		org $05893D		;2893D in ROM
		db $07			;change palette of red pendant
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x05892F,[0x8d,0x7b,0x03,0xa9,0x09],[0x8d,0x7b,0x03,0xa9,0x05],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x058934,[0x20,0xd3,0x8c,0xa9,0x0b],[0x20,0xd3,0x8c,0xa9,0x01],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x058939,[0x20,0xd3,0x8c,0xa9,0x0f],[0x20,0xd3,0x8c,0xa9,0x07],"11111")

		'''
		;the pendants travel in a direction determined by their color
		;so option C also requires a fix to their directional movement
		org $058D21		;28D21 in ROM
		db $04
		org $058D22		;28D22 in ROM
		db $04
		org $058D23		;28D23 in ROM
		db $FC
		org $058D24		;28D24 in ROM
		db $00
		org $058D25		;28D25 in ROM
		db $FE
		org $058D26		;28D26 in ROM
		db $FE
		org $058D27		;28D27 in ROM
		db $FE
		org $058D28		;28D28 in ROM
		db $FC
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x058D21,[0xfc,0x04,0x00,0x00,0xfe,0xfe,0xfc,0xfc], [0x04,0x04,0xfc,0x00,0xfe,0xfe,0xfe,0xfc],"11111111")

		'''
		;Blind Maiden
		;Previously she switched palettes when she arrived at the light (although it was very subtle)
		;Here we just set it so that she starts at that color
		org $0DB410		;6B410 in ROM
		db $4B			;sets the palette of the prison sprite (bits 1-3)
		org $09A8EB		;4A8EB in ROM
		db $05			;sets the palette of the tagalong (bits 0-2)
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x0DB40C,[0x40,0x59,0x41,0x58,0x4f],[0x40,0x59,0x41,0x58,0x4b],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x09A8E7,[0x04,0x04,0x04,0x00,0x07],[0x04,0x04,0x04,0x00,0x05],"11111")

		'''
		;Crystal Maiden (credits)
		;One of the crystal maidens was on Link's palette, but only in the end sequence
		;palette given by bits 1-3
		org $0EC8C3		;748C3 in ROM
		db $37
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x0EC8BF,[0x06,0x3b,0x31,0x3d,0x3f],[0x06,0x3b,0x31,0x3d,0x37],"11111")

		'''
		;Cukeman (Everywhere)
		;This guy is such a bugfest. Did you know that his body remains an enemy and if you try talking to him,
		;you have to target the overlaid sprite that only has eyeballs and a mouth?
		;This is why you can still be damaged by him. In any case, I digress.	Let's talk edits.
		;
		;These edits specifically target the color of his lips
		;Bits 1-3 are XORed with his base ID palette (0b100)
		;and the base palette cannot be changed without breaking buzzblobs (i.e. green dancing pickles)
		org $1AFA93		;D7A93 in ROM
		db $0F
		org $1AFAAB		;D7AAB in ROM
		db $0F
		org $1AFAC3		;D7AC3 in ROM
		db $0F
		org $1AFADB		;D7ADB in ROM
		db $0F
		org $1AFAF3		;D7AF3 in ROM
		db $0F
		org $1AFB0B		;D7B0B in ROM
		db $0F
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x1AFA8F,[0x00,0x07,0x00,0xe0,0x07],[0x00,0x07,0x00,0xe0,0x0f],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x1AFAA7,[0x00,0x08,0x00,0xe0,0x07],[0x00,0x08,0x00,0xe0,0x0f],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x1AFABF,[0x00,0x08,0x00,0xe0,0x07],[0x00,0x08,0x00,0xe0,0x0f],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x1AFAD7,[0x00,0x07,0x00,0xe0,0x07],[0x00,0x07,0x00,0xe0,0x0f],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x1AFAEF,[0x00,0x06,0x00,0xe0,0x07],[0x00,0x06,0x00,0xe0,0x0f],"11111")
		success_code &= self._apply_single_fix_to_snes_address(0x1AFB07,[0x00,0x08,0x00,0xe0,0x07],[0x00,0x08,0x00,0xe0,0x0f],"11111")

		'''
		;BUT there is a very specific ramification of the above edits:
		;Because his lips were moved to the red palette, his lips
		;no longer respond to shadowing effects
		;(like how red rupees appear in lost woods)
		;this will only be apparent if enemizer places him in areas like lost woods
		;or in the end credits sequence during his short cameo,
		;so the line below replaces him in the end sequence
		;with a buzzblob
		org $0ED664		;75664 in ROM
		db $00			;number of cukeman in the scene (up to 4)
		'''

		success_code &= self._apply_single_fix_to_snes_address(0x0ED660,[0x9d,0x20,0x0e,0xe0,0x01],[0x9d,0x20,0x0e,0xe0,0x00],"11111")

		return success_code
