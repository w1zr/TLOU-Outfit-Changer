@echo off
rem Builds release\TLOUOutfitChanger-v<version>.zip (Fluffy Mod Manager or manual
rem install) from build\xinput1_4.dll, dist\TLOUOutfitChanger.ini and the files
rem in package\fluffy. Run build.bat first.
setlocal
set VERSION=1.0.0
cd /d "%~dp0"
if not exist build\xinput1_4.dll (
  echo build\xinput1_4.dll not found. Run build.bat first.
  exit /b 1
)
copy /y build\xinput1_4.dll package\fluffy\ >nul || exit /b 1
copy /y dist\TLOUOutfitChanger.ini package\fluffy\ >nul || exit /b 1
if not exist release mkdir release
set ZIP=release\TLOUOutfitChanger-v%VERSION%.zip
if exist "%ZIP%" del "%ZIP%"
powershell -NoProfile -Command "Compress-Archive -Path package\fluffy\modinfo.ini,package\fluffy\screenshot.png,package\fluffy\xinput1_4.dll,package\fluffy\TLOUOutfitChanger.ini,package\fluffy\TLOUOutfitChanger.log,package\fluffy\TLOUOutfitChanger-README.txt -DestinationPath '%ZIP%'" || exit /b 1
echo Built %ZIP%
