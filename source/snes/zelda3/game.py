from source.meta.gui.gamelib import GameParent

class Game(GameParent):
    def __init__(self, my_subpath=""):
        super().__init__(my_subpath)
        # FIXME: Do we want to translate the game's display name?
        self.name = "The Legend of Zelda: A Link to the Past"
        self.console_name = "snes"
        self.internal_name = "zelda3"
        self.load_plugins()
