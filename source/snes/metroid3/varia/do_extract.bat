@echo off
copy metroid3.sfc metroid3-backup.sfc
if "%1"=="" (
  set hack=hack.sfc
)

echo *
echo Extract PNG from game file
@echo on
py -3.8 ./tools/extract_ship.py ./metroid3.sfc %hack%
