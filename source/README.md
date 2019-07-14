# SpriteSomething

## Source

The files in this folder and its subfolders are required by the program to run.

The `metroid3` folder contains scripts describing how to interface with Super Metroid. `game.py` describes metadata of the game. `rom.py` has memory addresses for finding particular bits of data within the game. The `samus` folder contains scripts describing how to interface with the Player Character sprite data. `rom_export.py` applies several bits of code to massage the game into being able to accept the new format of the Samus sprite sheet. `sprite.py` drives a lot of the Samus-specific stuff for the user interface.

The `zelda3` folder contains scripts describing how to interface with A Link to the Past. `game.py` describes metadata of the game. `rom.py` applies several bits of code to fix several inconsistencies and limitations of the Player Sprite animation engine. `sprite.py` drives a lot of the Link-specific stuff for the user interface.

`gamelib.py` describes a basic understanding of interfacing with games.

`spritelib.py` describes a basic understanding of interfacing with sprites.
