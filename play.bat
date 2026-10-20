@echo off
cd /d "%~dp0"
title J-Stars Victory VS+ PC

REM Check executable location
if exist "out\jstars_pc.exe" (
    set "EXE=out\jstars_pc.exe"
) else if exist "out\gpu\jstars_pc.exe" (
    set "EXE=out\gpu\jstars_pc.exe"
) else (
    echo Error: jstars_pc.exe not found! Please compile first.
    pause
    exit /b 1
)

echo ======================================================================
echo           J-Stars Victory VS+ Native PC Port (x86-64 Wrapper)
echo ======================================================================
echo Keyboard Controls:
echo   [Movement]         WASD or Arrow Keys
echo   [Cross / Confirm]  Z or J or Space
echo   [Circle / Cancel]  X or K or Left Shift
echo   [Square]           C or U or H
echo   [Triangle]         V or I or Y
echo   [L1 (Guard)]       Q or 1
echo   [R1 (Special)]     E or 3
echo   [Options / Start]  Enter or Escape
echo   [Touchpad]         Backspace or Tab
echo ======================================================================
echo.

"%EXE%" "out\boot-linked.bin" --app0 "extracted_game\app0" --import-names "out\import_names.txt"

if %errorlevel% neq 0 (
    echo.
    echo Game process ended with code %errorlevel%.
    pause
)
