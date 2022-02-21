@echo off

set ship=%1
if not defined ship (
  set ship=samus
)
call do_backup.bat %ship%

echo _
echo Inject PNG into game file
@echo on
py -3.8 ./tools/inject_ship.py --rom=metroid3-%ship%_ship.sfc --png=./tools/ship/%ship%/%ship%.png
