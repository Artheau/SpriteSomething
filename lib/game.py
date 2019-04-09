#this file contains common files for the class that contains all game-specific functions

import os

class Game():
    def __init__(self):
        raise AssertionError("function __init__() called on abstract class Game()")

    def get_background_names(self):
        return self.background_images.keys()

    def get_background_image(self, background_name):
        if background_name in self.background_images:
            filename = self.background_images[background_name]
            return Image.load(os.join("resources",self._directory_name,filename))
        else:
            raise AssertionError(f"received call to get_background_image() with invalid background name {background_name}")

