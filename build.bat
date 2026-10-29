@echo off
rem Builds xinput1_4.dll (the mod) and scan_test.exe with the MSVC x64 toolchain.
rem Requires Visual Studio 2022 Build Tools with the "Desktop development with C++" workload.
setlocal
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
for /f "usebackq delims=" %%i in (`call "%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSDIR=%%i"
if not defined VSDIR (
  echo MSVC x64 tools not found. Install Visual Studio 2022 Build Tools with the C++ workload.
  exit /b 1
)
call "%VSDIR%\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1

cd /d "%~dp0"
if not exist build mkdir build

set CFLAGS=/nologo /std:c++17 /O2 /MT /W4 /WX /EHsc /DUNICODE /D_UNICODE /DWIN32_LEAN_AND_MEAN /GS /guard:cf
set SRC=src\dllmain.cpp src\game.cpp src\scan.cpp src\config.cpp src\log.cpp src\proxy_xinput.cpp

cl %CFLAGS% /LD %SRC% /Fo"build\\" /Fe"build\xinput1_4.dll" /link /DEF:src\xinput.def /GUARD:CF user32.lib kernel32.lib || exit /b 1
cl %CFLAGS% tests\scan_test.cpp src\scan.cpp /Fo"build\\" /Fe"build\scan_test.exe" || exit /b 1

echo.
echo Built build\xinput1_4.dll and build\scan_test.exe
