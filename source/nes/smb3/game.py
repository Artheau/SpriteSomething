from source.meta.gui.gamelib import GameParent


class Game(GameParent):
    def __init__(self):
        super().__init__()
        self.name = "Super Mario Bros. 3"
        self.console_name = "nes"
        self.internal_name = "smb3"
