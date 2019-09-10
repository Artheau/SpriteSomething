# SpriteSomething

A GUI-enabled suite for management and replacement of retro gaming sprites.  Most known for its ability to inject custom player graphics into Super Metroid and A Link to the Past.

## Where to get it

Download the latest version from our [GitHub repository](https://github.com/Artheau/SpriteSomething/releases).

## How to run it

There should be a bundled executable in the release that you downloaded.
If you would like to run it from source, you can do so by running `SpriteSomething.py`

### Building from source (optional)

If you want to build an executable from source, you can use `build.py` and `SpriteSomething.spec` which should (in theory) be sufficient to build using `PyInstaller`.

The resulting executable will still require the source code and will run in place of `SpriteSomething.py`.

If UPX is present in a subdirectory named `upx`, then the builder will attempt to use it to compress the executable. UPX is not currently used in the released builds.

## General FAQ

### What do the script files in the root directory do?
See that particular [README document](./README-files.md).

### Can I use this tool to make my own hack?

Yes, but please adhere to the following guidelines:

- Please do not use this tool to make a commercial product, or use it in a for-profit endeavor.
- If you want to use or modify an existing sprite for your own hack, please contact the artist first to ask permission.
- Be considerate of those who are sensitive to flashing effects, and do not structure your art or palettes to exploit that sensitivity.
- Please credit the SpriteSomething developers (our names are in the "About" menu).

Also, please share your work!  We are very interested in the art that others produce.

## [Super Metroid FAQ](./app_resources/metroid3/FAQ.md)

## [A Link to the Past FAQ](./app_resources/zelda3/FAQ.md)
