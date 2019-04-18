@echo off
echo Build Release
py -m PyInstaller --windowed --noconfirm --log-level=WARN build-release.spec
