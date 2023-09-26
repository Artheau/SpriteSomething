# SpriteSomething

This release of SpriteSomething includes many basic features of the main design of the program.

## Updates Since Last Version

### Core

* Prelim work on some new unit tests.
* Fixed `.rdc` export.
* Fixed Metroid3/Samus loading from game files
* Forced Zelda3/Link Bunny Palette for Bunny animations

## Known Issues

* Pillow versions including 7.0 and above are not yet supported (color processing errors)
* Python versions including 3.9 and above are not yet supported (Pillow 6.2.2 does not build on Py3.9+)
* MacOSX builds not provided at this time because `pyinstaller` complains about security-signing the executable and I'm not paying money to resolve that, kthx. Running from source should still work on MacOSX.

## Features

### Supported Games

* The Legend of Zelda: A Link to the Past
  * Several romhacks thereof
* ALttP Randomizer
  * Item Randomizer
  * Enemy Randomizer
  * Entrance Randomizer
* Super Metroid
  * Several romhacks thereof
* Super Metroid Randomizer
  * Item Randomizer
* Super Metroid/A Link to the Past Combo Randomizer

### General Features included in this version

* Open sprite from flattened PNG, compiled ZSPR
* Extract sprite from supported game file
* Read/Write ZSPR sprite metadata
* Export sprite as flattened PNG, compiled ZSPR, compiled RDC
* Inject sprite into supported game file; single or a directory (experimental)
* Export current animation frame as PNG
* Export current animation as GIF
* Export current animation as horizontal collage

### Animation Features included in this version

* Bundled backgrounds
* Directional controls
* Palette selection controls
* Zoom controls
* Playback controls
* Download Official ALttPR Sprites
* Download Link sprites as included by the SpriteSomething team
* Download Samus sprites as included by the SpriteSomething team

### Lesser-documented features in this version

* Command-line interface

## Executable Builds

* Executables for Linux (built on Ubuntu Focal), ~~MacOSX (built on 10.15 xcode 11.2.1)~~ (*MacOSX builds are being difficult and are thusly discontinued until further notice*) and Windows (built on Windows Server 2019) all built on python 3.8 are available.

### Build from source

If you would prefer to run/build from source, you can download the source code for this release below.  See `docs/BUILDING.md` for instructions.
