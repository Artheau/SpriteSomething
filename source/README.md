# SpriteSomething

## Source

The files in this folder and its subfolders are required by the program to run.

The `metroid3` folder contains scripts describing how to interface with Super Metroid. `game.py` describes metadata of the game. `rom.py` has memory addresses for finding particular bits of data within the game.

The `samus` folder contains scripts describing how to interface with the Player Character sprite data.

* `plugins.py` describes various plugins available for Samus-like sprites.
* `rdc_export.py` describes how to export as the Retro Data Container (RDC) format.
* `rom_export.py` applies several bits of code to massage the game into being able to accept the new format of the Samus sprite sheet.
* `sprite.py` drives a lot of the Samus-specific stuff for the user interface.

The `zelda3` folder contains scripts describing how to interface with A Link to the Past. `game.py` describes metadata of the game. `rom.py` applies several bits of code to fix several inconsistencies and limitations of the Player Sprite animation engine.

`SpriteSomething.spec` tells `pyinstaller` what we want it to do when building binaries using the Continuous Integration interface as described in the appropriate configuration file.

The `snes` folder contains things associated with SNES games.

* `romhandler.py` handles processing of SNES and SNES-like game files.

The `snes/zelda3/link` folder contains scripts describing how to interface with the Player Character sprite data.

* `equipment.py` helps with splitting Link's equipment from a master sheet for use in various animations.
* `plugins.py` describes various plugins available for Link-like sprites.
* `sprite.py` drives a lot of the Link-specific stuff for the user interface.

The `meta` folder contains scripts that interface with all supported games and sprites:

* `animationlib.py` handles processing and pasting images together in a sequence to animate each defined animation.
* `cli.py` handles processing the commandline interface.
* `common.py` has many functions that are used in many places within the application.
* `constants.py` has a few definitions of various configuration bits that are usde in many places within the application.
* `gamelib.py` describes a basic understanding of interfacing with games.
* `gui_common.py` describes many common elements used in the GUI that strives to keep these things away from the game and sprite libraries.
* `gui.py` drives a lot of the GUI-specific elements.
* `layoutlib.py` handles processing of sprite sheet layout manifests.
* `pluginslib.py` handles processing of plugins definitions.
* `spritelib.py` describes a basic understanding of interfacing with sprites.
* `ssTranslate.py` handles processing of translation files for the interface.
* `widgetlib.py`, like `gui_common.py`, describes common elements used in the GUI.
