# SpriteSomething

## App Resources

The files in this folder and its subfolders generally are required by the program in the form of icons or default source information.

The `meta` folder has things that pertain to the program as a whole. It contains `icons` used by the main user interface (including `app.ico`, an icon to identify the program, made by Artheau), translation files in the `lang` folder (defaulting to English), and several manifests including:
* `app_names.json` contains strings that build the randomized program title upon starting
* `bindings.json` contains default keybindings
* `game_header_info.json` contains infirmation that helps with auto-detecting certain game files
* `pip_requirements.txt` contains pip packages that are required dependencies
* `zspr.json` has some notes about the differing versions of the ZSPR file format

The `metroid3` folder has a stock set of backgrounds in the `backgrounds` folder, translation files (defaulting to English), `manifest.json` has some basic metadata about the Player Character Sprite as represented by Samus.

The `samus` folder has `icons` for Samus, translation files (defaulting to English), her animation definitions, the layout of the sprite sheet and a full-version of the sprite sheet as described by the aforementioned layout. You may use `samus.png` as a reference. There are some additional sheets for other various aspects of her animations.

The `zelda3` folder has a stock set of backgrounds in the `backgrounds` folder, translation files (defaulting to English),`manifest.json` has some basic metadata about the Player Character Sprite as represented by Link.

The `link` folder has `icons` for Link, translation files (defaulting to English), his animation definitions, the layout of the sprite sheet and a compiled version of the sprite sheet as described by the aforementioned layout. You may use `link.zspr` as a reference. Layer files for popular image editing software can be found in the `#sprites` channel of the [ALttP Randomizer Discord](http://discord.gg/alttprandomizer).
