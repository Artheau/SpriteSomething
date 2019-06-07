# SpriteSomething
A GUI-enabled suite for management and replacement of retro gaming sprites.  Most known for its ability to inject custom player graphics into Super Metroid and A Link to the Past.

## Where to get it
Download the latest version from <https://github.com/Artheau/SpriteSomething/releases>.

## How to run it
### Windows users:
open `SpriteSomething.exe`

### Mac/Linux users:
You must have Python 3.6 or better installed, along with the packages `pillow` and `numpy`.

run `python SpriteSomething.py`

### Building from source (optional)
If you want to build an executable from source, you can use `build.py` and `SpriteSomething.spec` which should (in theory) be sufficient to build using `PyInstaller`.
The resulting executable will still require the `resources` subdirectory.
If UPX is present in a subdirectory named `upx`, then the builder will attempt to use it to compress the executable, but this feature has not worked in test builds, so it is recommended at this time to not use UPX compression.

## Super Metroid FAQ
### How can I replace Samus in Super Metroid with a new character?
- File/Open.  Choose any valid Samus sprite sheet, e.g. `megaman.png`.
The new character should appear in the view area, and you can also click the Overview tab to see the imported sheet.
- Export/Inject into Game File.

### How can I keep Samus, but get the new animations, like screw attack without space jump, and the restored crystal flash?
- File/Open.  Choose `samus.png`.
- Export/Inject into Game File.

### How can I get the new screw attack without space jump, but keep everything else exactly the way it was, even down to the broken walljump elbowpads and missing scanlines?
- File/Open.  Choose any Super Metroid ROM.  The program will import the graphics from the ROM directly.
- Export/Inject into Game File.

### Can I make my own sprite to replace Samus?
Yes!  This is one of the main focuses of the SpriteSomething project.

Along with the release files you can see that we have included a zip file containing a number of layers and images which are intended to assist you in the process.
Documentation is still a little light, and so a key part of the project will be adding tutorials and documenting the available features.

If you are interested in making custom sprites for Super Metroid, consider joining us in the `#sprite-dev` forum on the combo randomizer Discord: <https://discord.gg/PMKcDPQ>.
We like to talk about such things -- this is what we do for fun!

### How can I change the color of Samus's ship?
Take the `.png` file for your desired character, and look at the block of colors at the very top.
At the bottom right corner, you will notice three colors, which for Samus are yellow, green, and magenta, but may be different if you are using a custom sprite sheet.
These colors control the colors for the ship body, the ship window, and the glow effect on the underside of the ship, respectively.
You can change these colors to whatever you like, and then inject the new sprite sheet into the game!  The program will automatically apply shading to construct the full palette.

### Is this program compatible with randomizers, the combo randomizer, or with [Name of Hack]?
This program is designed to be fully compatible with standard randomizers, the SMaLttPR combo randomizer, and the original Super Metroid.

It will probably also work with any other Super Metroid variant that does not heavily edit banks `$92` and `$9B`.  If used to inject a sprite into a LoRom, SpriteSomething will place tile data into banks `$F5` through `$FF`.  If injecting into an ExLoRom, SpriteSomething will use `$35`-`3F` (6 MB), or `$73`-`$7D` (8 MB).

### Can I extract the custom Samus graphics from [Name of Hack]?
Usually yes.  You could, for instance, extract Auximines's Justin Bailey sprite from his famous hack.
However, if you're primarily interested in playing as the Bailey sprite, I encourage you to use the (included) modified Bailey sheet that cleans up missing tiles and corrects some palette errors.



## A Link to the Past FAQ
### How can I replace Link in A Link to the Past with a new character?
- File/Open.  Choose any valid Link sprite sheet, e.g. `alice.zspr`.
You can also import PNG files in this manner if they are formatted to have a palette block in the lower right corner.
- Export/Inject into Game File.

### The friendly thief in Lost Woods is a bit more of a pastel color than before.  Why is this?
The injection tool also includes with it a patch that fixes some issues that occur when custom sprites have modified palettes.
As part of this fix, the thief was moved to the closest available palette.
We could have also changed him to be the same color of yellow that he is in the end credits... but where's the fun in that?

### Can I make my own sprite to replace Link?
Yes!  This is one of the main focuses of the SpriteSomething project.
You could, for instance, File/Open any Link to the Past ROM, and then File/Save a PNG file, which you could then modify and re-inject.
That said, this might not be the easiest way to start!

The Link to the Past spriting community is quite active, and there is a wealth of other resources that might be helpful to you.
A good place to start is the `#sprite-dev` channel on the Link to the Past Randomizer Discord: <https://discordapp.com/invite/alttprandomizer>.
In the channel header you will find a variety of tools and tutorials designed to assist you in this regard.

## General FAQ
### Can I use this tool to make my own hack?
Yes, but please adhere to the following guidelines:
- Please do not use this tool to make a commercial product, or use it in a for-profit endeavor.
- If you want to use or modify an existing sprite for your own hack, please contact the artist first to ask permission.
- Be considerate of those who are sensitive to flashing effects, and do not structure your art or palettes to exploit that sensitivity.
- Please credit the SpriteSomething developers (our names are in the "About" menu).

Also, please share your work!  We are very interested in the art that others produce.
