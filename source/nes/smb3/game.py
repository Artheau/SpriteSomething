from source.meta.gui.gamelib import GameParent

class Game(GameParent):
    def __init__(self, my_subpath):
        super().__init__(my_subpath)
        self.name = "Super Mario Bros. 3"
        self.console_name = "nes"
        self.internal_name = "smb3"
