@echo off
echo Build Test
py -m PyInstaller --console --noconfirm --log-level=WARN build-test.spec
