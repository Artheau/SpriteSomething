@echo off

set ship=%1
if not defined ship (
  set ship=samus
)
call do_backup.bat %ship%

echo _
echo Convert PNG using ImageMagick
@echo on
magick convert ./tools/ship/%ship%/%ship%.png +dither -colors 16 PNG32:./tools/ship/%ship%/%ship%_magick.png
@echo off

call do_inject.bat %ship%
