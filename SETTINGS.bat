@echo off
:: ============================================================
::  FORTNITE OPTIMIZER v2.0 - SETTINGS
:: ============================================================
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

mode con: cols=65 lines=40
color 0B
title Fortnite Optimizer v2.0 - Settings

cls
echo.
echo  +=======================================================+
echo  ^|       FORTNITE OPTIMIZER v2.0 - SETTINGS            ^|
echo  +=======================================================+
echo  [G] Launch Modern Python GUI (Recommended)
echo  [1] Classic settings menu (VBS)
echo  [2] Quick preset selector (TOURNAMENT/PERFORMANCE/...)
echo  [3] Change display resolution
echo  [4] Fortnite server ping test
echo  [0] Exit
echo.
set /p "START_CHOICE=  Your choice: "

if "%START_CHOICE%"=="0" goto :end
if /i "%START_CHOICE%"=="G" (
    start "" pythonw "%ROOT%\gui.py"
    goto :end
)
if "%START_CHOICE%"=="2" (
    wscript.exe "%ROOT%\vbs\preset_picker.vbs"
    goto :show_current
)
if "%START_CHOICE%"=="3" (
    wscript.exe "%ROOT%\vbs\resolution_picker.vbs"
    goto :show_current
)
if "%START_CHOICE%"=="4" (
    call "%ROOT%\core\ping_monitor.bat"
    goto :extra_menu
)

echo.
echo  Loading settings menu...
echo.

set "VBS_MENU=%ROOT%\vbs\show_menu.vbs"

if exist "%VBS_MENU%" (
    wscript.exe "%VBS_MENU%"

:show_current
    echo.
    echo  [OK] Settings saved!
    echo.
    echo  +-----------------------------------------------------+
    echo  ^|  Current settings ^(config\settings.cfg^):         ^|
    echo  +-----------------------------------------------------+
    echo.

    set "CFG=%ROOT%\config\settings.cfg"
    if exist "%CFG%" (
        for /f "usebackq tokens=1,* delims==" %%A in ("%CFG%") do (
            set "key=%%A"
            set "val=%%B"
            if not "!key:~0,1!"=="#" (
                if not "!val!"=="" (
                    if "!val!"=="1" (
                        echo     [ON]  !key!
                    ) else if "!val!"=="0" (
                        echo     [OFF] !key!
                    ) else (
                        echo     [>>]  !key! = !val!
                    )
                )
            )
        )
    )

    echo.
    echo  -----------------------------------------------------
    echo  Settings apply on next LAUNCH_OPTIMIZER.bat run
    echo  -----------------------------------------------------
    echo.

:extra_menu
    echo  What to do now?
    echo.
    echo  [1] Run optimization now ^(LAUNCH_OPTIMIZER.bat^)
    echo  [2] Restore all changes to Windows defaults
    echo  [3] Open config\settings.cfg in Notepad
    echo  [4] Exit
    echo.
    set /p "CHOICE=  Your choice ^(1-4^): "

    if "%CHOICE%"=="1" (
        echo.
        echo  Starting optimization...
        call "%ROOT%\LAUNCH_OPTIMIZER.bat"
        goto :end
    )
    if "%CHOICE%"=="2" (
        echo.
        echo  Restoring defaults...
        call "%ROOT%\core\restore_defaults.bat"
        goto :end
    )
    if "%CHOICE%"=="3" (
        start notepad.exe "%ROOT%\config\settings.cfg"
        echo  File opened in Notepad.
        echo.
        goto :extra_menu
    )
    if "%CHOICE%"=="4" goto :end
    goto :extra_menu

) else (
    echo  [ERROR] vbs\show_menu.vbs not found!
    echo  Opening config in Notepad...
    if not exist "%ROOT%\config" mkdir "%ROOT%\config"
    start notepad.exe "%ROOT%\config\settings.cfg"
)

:end
echo.
echo  Press any key to exit...
pause >nul
endlocal
