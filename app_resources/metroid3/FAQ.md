# SpriteSomething

## Super Metroid FAQ

### How can I replace Samus in Super Metroid with a new character?

- File/Open.  Choose any valid Samus sprite sheet, e.g. `megaman.png`.
The new character should appear in the view area, and you can also click the Overview tab to see the imported sheet.
- Export/Inject into Game File.

### How can I keep Samus, but get the new animations, like screw attack without space jump, and the restored crystal flash?

- File/Open.  Choose `samus.png`.
- Export/Inject into Game File.

### How can I get the new screw attack without space jump, but keep everything else exactly the way it was, even down to the broken walljump elbowpads and missing scanlines?

- File/Open.  Choose a base Super Metroid ROM (crc32: `D63ED5F8`).  The program will import the graphics from the ROM directly.
- Export/Inject into Game File.

### Can I make my own sprite to replace Samus?

Yes!  This is one of the main focuses of the SpriteSomething project.

You can locate a list of Samus sprites available at our [online SpriteSomething collection](http://artheau.github.io/SpriteSomething).
Documentation is still a little light, and so a key part of the project will be adding tutorials and documenting the available features.

If you are interested in making custom sprites for Super Metroid, consider joining us in the `#sprite-dev` channel on the [Super Metroid/A Link to the Past Combination Randomizer Discord](https://discord.gg/PMKcDPQ).
We like to talk about such things -- this is what we do for fun!

### How can I change the color of Samus's ship?

Take the `.png` file for your desired character, and look at the block of colors at the very top.
At the bottom right corner, you will notice three colors, which for Samus are yellow, green, and magenta, but may be different if you are using a custom sprite sheet.
These colors control the colors for the ship body, the ship window, and the glow effect on the underside of the ship, respectively.
You can change these colors to whatever you like, and then inject the new sprite sheet into the game!  The program will automatically apply shading to construct the full palette.

### Is this program compatible with randomizers, the combo randomizer, or with [Name of Hack]?

This program is designed to be fully compatible with standard randomizers, the SMALttPR Combo Randomizer, and the original Super Metroid.

It will probably also work with any other Super Metroid variant that does not heavily edit banks `$92` and `$9B`.  If used to inject a sprite into a LoRom, SpriteSomething will place tile data into banks `$F5` through `$FF`.  If injecting into an ExLoRom, SpriteSomething will use `$35`-`3F` (6 MB), or `$73`-`$7D` (8 MB).

### Can I extract the custom Samus graphics from [Name of Hack]?

Usually yes.  You could, for instance, extract Auximines's Justin Bailey sprite from his famous hack.
However, if you're primarily interested in playing as the Bailey sprite, I encourage you to use the modified Bailey sheet that cleans up missing tiles and corrects some palette errors. This modified sheet is available on our [online SpriteSomething collection](http://artheau.github.io/SpriteSomething).
