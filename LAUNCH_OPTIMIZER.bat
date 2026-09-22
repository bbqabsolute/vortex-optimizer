@echo off
:: ============================================================
::  FORTNITE OPTIMIZER v2.0 - MAIN LAUNCHER
::  Applies all optimizations then launches Fortnite
:: ============================================================
setlocal EnableDelayedExpansion

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
set "CFG=%ROOT%\config\settings.cfg"

mode con: cols=65 lines=55
color 0A
title Fortnite Optimizer v2.0

cls
echo.
echo  +=======================================================+
echo  ^|         FORTNITE OPTIMIZER  v2.0                    ^|
echo  ^|   Maximum FPS + Minimum Ping                        ^|
echo  +=======================================================+
echo.

set "PRESET=CUSTOM"
set "FPS_BOOST=1"
set "VISUAL_EFFECTS=1"
set "DISABLE_DVRGAME=1"
set "POWER_PLAN=1"
set "HAGS_DISABLE=0"
set "HIGH_PRIORITY=1"
set "NETWORK_BOOST=1"
set "NAGLE_OFF=1"
set "DNS_OPTIMIZE=1"
set "DNS_PRIMARY=8.8.8.8"
set "DNS_SECONDARY=8.8.4.4"
set "CPU_UNPARK=1"
set "MSI_MODE=1"
set "MOUSE_OPTIMIZE=1"
set "FORTNITE_INI=1"
set "PAGEFILE_OPTIMIZE=0"
set "RESOLUTION_CHANGE=0"
set "RESOLUTION_WIDTH=1920"
set "RESOLUTION_HEIGHT=1080"
set "RESOLUTION_REFRESH=0"
set "PING_MONITOR=1"
set "RAM_CLEANUP=1"
set "KILL_USELESS=1"
set "LAUNCH_EPIC=1"
set "EPIC_PATH=C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"

if exist "%CFG%" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%CFG%") do (
        set "ln=%%A"
        if not "!ln:~0,1!"=="#" if not "%%B"=="" set "%%A=%%B"
    )
    echo  [OK] Config loaded  ^|  Preset: !PRESET!
) else (
    echo  [WARN] Config not found, using default settings
)

echo.
echo  +-------------------------------------------------------+
echo  ^|  OPTIMIZATION PLAN:                                  ^|
echo  ^|                                                       ^|

if "%FPS_BOOST%"=="1"         echo  ^|  [ON]  [1] FPS Boost + Game DVR + Power Plan         ^|
if "%CPU_UNPARK%"=="1"        echo  ^|  [ON]  [2] CPU Unpark - all cores active             ^|
if "%MSI_MODE%"=="1"          echo  ^|  [ON]  [3] MSI Mode GPU/NIC - lower latency          ^|
if "%MOUSE_OPTIMIZE%"=="1"    echo  ^|  [ON]  [4] Mouse 1:1 - accurate aim                 ^|
if "%NETWORK_BOOST%"=="1"     echo  ^|  [ON]  [5] Network + Nagle + DNS + QoS              ^|
if "%FORTNITE_INI%"=="1"      echo  ^|  [ON]  [6] Fortnite INI tweaks                      ^|
if "%PAGEFILE_OPTIMIZE%"=="1" echo  ^|  [ON]  [7] Pagefile optimization                    ^|
if "%RESOLUTION_CHANGE%"=="1" echo  ^|  [ON]  [8] Resolution: !RESOLUTION_WIDTH!x!RESOLUTION_HEIGHT!                  ^|
if "%PING_MONITOR%"=="1"      echo  ^|  [ON]  [9] Ping test - Fortnite servers             ^|
if "%RAM_CLEANUP%"=="1"       echo  ^|  [ON]  [10] RAM + TEMP cleanup                      ^|

echo  +-------------------------------------------------------+
echo.
echo  Press any key to start optimization...
echo  (Close this window to cancel)
pause >nul

cls
echo.
echo  +=======================================================+
echo  ^|               OPTIMIZATION RUNNING                  ^|
echo  +=======================================================+
echo.

set "STEP=0"
set "TOTAL=10"

set /a STEP+=1
if "%FPS_BOOST%"=="1" (
    echo  [!STEP!/!TOTAL!] FPS optimizations...
    echo  -------------------------------------------------------
    call "%ROOT%\core\fps_boost.bat"
    call "%ROOT%\core\apply_tweaks.bat" %HAGS_DISABLE%
    echo.
) else (
    echo  [!STEP!/!TOTAL!] FPS optimizations: SKIPPED
)

set /a STEP+=1
if "%CPU_UNPARK%"=="1" (
    echo  [!STEP!/!TOTAL!] CPU Unpark - activating all cores...
    echo  -------------------------------------------------------
    call "%ROOT%\core\cpu_unpark.bat"
    echo.
) else (
    echo  [!STEP!/!TOTAL!] CPU Unpark: SKIPPED
)

set /a STEP+=1
if "%MSI_MODE%"=="1" (
    echo  [!STEP!/!TOTAL!] MSI Mode for GPU and NIC...
    echo  -------------------------------------------------------
    call "%ROOT%\core\msi_mode.bat"
    echo.
) else (
    echo  [!STEP!/!TOTAL!] MSI Mode: SKIPPED
)

set /a STEP+=1
if "%MOUSE_OPTIMIZE%"=="1" (
    echo  [!STEP!/!TOTAL!] Mouse optimization ^(1:1 no acceleration^)...
    echo  -------------------------------------------------------
    call "%ROOT%\core\mouse_optimize.bat"
    echo.
) else (
    echo  [!STEP!/!TOTAL!] Mouse optimization: SKIPPED
)

set /a STEP+=1
if "%NETWORK_BOOST%"=="1" (
    echo  [!STEP!/!TOTAL!] Network optimizations ^(reduce ping^)...
    echo  -------------------------------------------------------
    call "%ROOT%\core\network_boost.bat" "%DNS_PRIMARY%" "%DNS_SECONDARY%" %NAGLE_OFF% %DNS_OPTIMIZE%
    echo.
) else (
    echo  [!STEP!/!TOTAL!] Network optimizations: SKIPPED
)

set /a STEP+=1
if "%FORTNITE_INI%"=="1" (
    echo  [!STEP!/!TOTAL!] Fortnite INI tweaks...
    echo  -------------------------------------------------------
    call "%ROOT%\core\fortnite_ini.bat"
    echo.
) else (
    echo  [!STEP!/!TOTAL!] INI tweaks: SKIPPED
)

set /a STEP+=1
if "%PAGEFILE_OPTIMIZE%"=="1" (
    echo  [!STEP!/!TOTAL!] Pagefile optimization...
    echo  -------------------------------------------------------
    call "%ROOT%\core\pagefile_optimize.bat"
    echo.
) else (
    echo  [!STEP!/!TOTAL!] Pagefile: SKIPPED
)

set /a STEP+=1
if "%RESOLUTION_CHANGE%"=="1" (
    echo  [!STEP!/!TOTAL!] Changing resolution: %RESOLUTION_WIDTH%x%RESOLUTION_HEIGHT%...
    echo  -------------------------------------------------------
    call "%ROOT%\core\resolution.bat" %RESOLUTION_WIDTH% %RESOLUTION_HEIGHT% %RESOLUTION_REFRESH%
    echo.
) else (
    echo  [!STEP!/!TOTAL!] Resolution: SKIPPED ^(no change^)
)

set /a STEP+=1
if "%PING_MONITOR%"=="1" (
    echo  [!STEP!/!TOTAL!] Ping test - Fortnite servers...
    echo  -------------------------------------------------------
    call "%ROOT%\core\ping_monitor.bat"
    echo.
) else (
    echo  [!STEP!/!TOTAL!] Ping test: SKIPPED
)

set /a STEP+=1
if "%RAM_CLEANUP%"=="1" (
    echo  [!STEP!/!TOTAL!] RAM cleanup + temp files + processes...
    echo  -------------------------------------------------------
    call "%ROOT%\core\cleanup.bat" %KILL_USELESS%
    echo.
) else (
    echo  [!STEP!/!TOTAL!] Cleanup: SKIPPED
)

echo.
echo  +=======================================================+
echo  ^|  Launching Fortnite...                              ^|
echo  +=======================================================+
echo.

if "%LAUNCH_EPIC%"=="1" (
    call "%ROOT%\core\launch_fortnite.bat" "%EPIC_PATH%" %HIGH_PRIORITY%
) else (
    echo  Auto-launch disabled. Start Epic Games manually.
)

echo.
echo  +=======================================================+
echo  ^|    ALL OPTIMIZATIONS APPLIED SUCCESSFULLY!          ^|
echo  ^|                                                       ^|
echo  ^|  FPS Boost        - active                          ^|
echo  ^|  CPU Unpark       - all cores active                ^|
echo  ^|  MSI Mode         - GPU latency reduced             ^|
echo  ^|  Mouse            - 1:1 no acceleration             ^|
echo  ^|  Network/Ping     - optimized                       ^|
echo  ^|  INI Tweaks       - applied                         ^|
echo  ^|  RAM              - cleaned                         ^|
echo  ^|                                                       ^|
echo  ^|           GG WP! Good luck!                        ^|
echo  +=======================================================+
echo  Press any key to exit this window...
pause >nul
endlocal
