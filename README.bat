@echo off
:: ============================================================
::  README - Fortnite Optimizer v2.0 Instructions
:: ============================================================
setlocal
set "ROOT=%~dp0"

mode con: cols=65 lines=55
color 0E
title Fortnite Optimizer - Instructions

cls
echo.
echo  +=======================================================+
echo  ^|         FORTNITE OPTIMIZER v2.0                     ^|
echo  ^|              INSTRUCTIONS                           ^|
echo  +=======================================================+
echo.
echo  +-------------------------------------------------------+
echo  ^|  FILES:                                              ^|
echo  +-------------------------------------------------------+
echo  ^|  START_GUI.bat          - Modern Python GUI (Recommended)
echo  ^|  LAUNCH_OPTIMIZER.bat  - Console Launcher (optimize+game)
echo  ^|  SETTINGS.bat          - Console settings menu
echo  ^|  README.bat            - This instructions file
echo  ^|  core\                 - Core optimization scripts  ^|
echo  ^|  vbs\                  - VBS dialogs                ^|
echo  ^|  config\settings.cfg   - Your settings              ^|
echo  +-------------------------------------------------------+
echo.
echo  +-------------------------------------------------------+
echo  ^|  HOW TO USE:                                         ^|
echo  +-------------------------------------------------------+
echo  ^|                                                       ^|
echo  ^|  1. Run SETTINGS.bat (as Administrator)             ^|
echo  ^|     -> Configure optimizations for your PC         ^|
echo  ^|     -> Choose a preset or customize manually       ^|
echo  ^|     -> Set correct Epic Games path if needed       ^|
echo  ^|                                                       ^|
echo  ^|  2. Run LAUNCH_OPTIMIZER.bat before every game     ^|
echo  ^|     -> Applies all enabled optimizations           ^|
echo  ^|     -> Shows ping test (if enabled)                ^|
echo  ^|     -> Auto-launches Fortnite                      ^|
echo  ^|                                                       ^|
echo  +-------------------------------------------------------+
echo.
echo  +-------------------------------------------------------+
echo  ^|  WHAT IT OPTIMIZES:                                  ^|
echo  +-------------------------------------------------------+
echo  ^|                                                       ^|
echo  ^|  FPS:                                                ^|
echo  ^|  * Power plan: Ultimate Performance                 ^|
echo  ^|  * Game DVR, Xbox GameBar: DISABLED                 ^|
echo  ^|  * Windows visual effects: DISABLED                 ^|
echo  ^|  * CPU/GPU priority for games (GPU Priority 8)     ^|
echo  ^|  * System timer optimization                        ^|
echo  ^|  * NVIDIA / AMD specific tweaks                     ^|
echo  ^|  * Superfetch, indexing: DISABLED                   ^|
echo  ^|  * FPS cap in GameUserSettings.ini: REMOVED         ^|
echo  ^|                                                       ^|
echo  ^|  PING (NETWORK):                                     ^|
echo  ^|  * Nagle Algorithm: DISABLED (lower latency)        ^|
echo  ^|  * DNS: Cloudflare 1.1.1.1 / Google 8.8.8.8       ^|
echo  ^|  * TCP/IP stack optimization                        ^|
echo  ^|  * NetworkThrottling: DISABLED                      ^|
echo  ^|  * QoS priority for Fortnite process               ^|
echo  ^|  * Firewall rules for Fortnite                      ^|
echo  ^|  * IPv6 tunnels disabled (Teredo, 6to4)            ^|
echo  ^|                                                       ^|
echo  ^|  UNIQUE FEATURES:                                    ^|
echo  ^|  * CPU Core Unpark (100%% cores active)              ^|
echo  ^|  * MSI Mode GPU/NIC (lower interrupt latency)      ^|
echo  ^|  * Mouse 1:1 SmoothXY curves (no acceleration)    ^|
echo  ^|  * Fortnite Engine.ini deep tweaks                  ^|
echo  ^|  * Pagefile auto-optimizer (RAM-based sizing)       ^|
echo  ^|  * Ping monitor - shows best region before launch  ^|
echo  ^|  * Resolution changer (stretched res support)      ^|
echo  ^|  * 4 Presets: TOURNAMENT/PERFORMANCE/BALANCED/     ^|
echo  ^|               STREAMING                             ^|
echo  +-------------------------------------------------------+
echo.
echo  +-------------------------------------------------------+
echo  ^|  PRESETS:                                            ^|
echo  +-------------------------------------------------------+
echo  ^|  TOURNAMENT  - Max FPS, min ping, all ON            ^|
echo  ^|  PERFORMANCE - High FPS, HAGS ON (RTX 30xx+)       ^|
echo  ^|  BALANCED    - Core tweaks, no INI changes          ^|
echo  ^|  STREAMING   - Game DVR ON, keeps OBS running      ^|
echo  +-------------------------------------------------------+
echo.
echo  +-------------------------------------------------------+
echo  ^|  IMPORTANT:                                          ^|
echo  +-------------------------------------------------------+
echo  ^|  * Always run as Administrator!                     ^|
echo  ^|  * To rollback: SETTINGS.bat -> "Restore defaults" ^|
echo  ^|  * HAGS OFF: GTX 10xx / RTX 20xx                  ^|
echo  ^|  * HAGS ON:  RTX 30xx / RTX 40xx                  ^|
echo  ^|  * MSI Mode + Pagefile require REBOOT              ^|
echo  +-------------------------------------------------------+
echo.

set /p "OPEN=  Open SETTINGS.bat now? (y/n): "
if /i "%OPEN%"=="y" (
    call "%ROOT%SETTINGS.bat"
)

pause
endlocal
