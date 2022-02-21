@echo off

set ship=%1
if not defined ship (
  set ship=samus
)
echo _
echo Back up baserom and prepare destination for injection

copy metroid3.sfc metroid3-backup.sfc
copy metroid3.sfc metroid3-%ship%_ship.sfc
