#Originally written by Artheau
#in April 2019
#while in a Stalfos costume sitting on a throne, filming for a live-action motion picture

#includes routines that load the rom and apply bugfixes
#inherits from SNESRomHandler


if __name__ == "__main__":
    raise AssertionError(f"Called main() on utility library {__file__}")

import enum
from lib.RomHandler.rom import RomHandler


#enumeration for the mail types
class MailType(enum.Enum):
    GREEN = enum.auto()
    BLUE = enum.auto()
    RED = enum.auto()
    BUNNY = enum.auto()


class Zelda3RomHandler(RomHandler):
    def __init__(self, filename):
        super().__init__(filename)      #do the usual stuff

        self._apply_bugfixes()
        self._apply_improvements()


    def get_pose_data(self,animation,pose):
        raise NotImplementedError()


    def get_default_vram_data(self):
        raise NotImplementedError()


    def get_pose_control_data(self,animation,pose):
        raise NotImplementedError()


    def get_palette(self, mail_type, glove_type):
        #returns a list.  Each element of the list is a tuple, where the first entry is the amount of time that the palette
        # should display for (here $00 is a special case for static palettes).  The second entry is the 555 palette data.
        raise NotImplementedError()


    def _get_pose_tilemaps(self,animation,pose):
        raise NotImplementedError()


    def _get_dma_data(self,animation,pose):
        raise NotImplementedError()


    def _get_pose_duration(self,animation, pose):
        raise NotImplementedError()


    def _apply_improvements(self):
        pass

    def _apply_bugfixes(self):
        #these are significant typos that reference bad palettes or similar, and would raise assertion errors in any clean code
        pass
