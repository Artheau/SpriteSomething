@echo off
py -m PyInstaller --noconfirm --log-level=WARN ^
  main.spec
