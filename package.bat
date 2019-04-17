@echo off
cd dist
rmdir /s /q package
cd ..
echo .sfc > no-sfcs.txt
echo .smc >> no-sfcs.txt
xcopy /q /s /i /y lib\*.* dist\package\lib
xcopy /q /s /i /y dist\main\PIL\*.* dist\package\PIL
xcopy /q /s /i /y /EXCLUDE:no-sfcs.txt resources\*.* dist\package\resources
xcopy /q /s /i /y dist\main\tcl\*.* dist\package\tcl
xcopy /q /s /i /y dist\main\tk\*.* dist\package\tk
xcopy /q /y dist\main\_tkinter.pyd dist\package\_tkinter.pyd*
xcopy /q /y dist\main\base_library.zip dist\package\base_library.zip*
xcopy /q /y dist\main\main.exe dist\package
xcopy /q /y dist\main\python37.dll dist\package
xcopy /q /y dist\main\tcl86t.dll dist\package
xcopy /q /y dist\main\tk86t.dll dist\package
