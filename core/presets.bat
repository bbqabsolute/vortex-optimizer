@echo off
:: ============================================================
::  presets.bat  -  Fortnite Optimizer
::  Applies preset configuration to config\settings.cfg
::  Argument: PRESET_NAME (TOURNAMENT/PERFORMANCE/BALANCED/STREAMING)
:: ============================================================
setlocal EnableDelayedExpansion

set "PRESET=%~1"
if "%PRESET%"=="" set "PRESET=PERFORMANCE"

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-6%"
set "CFG=%ROOT%config\settings.cfg"

echo [PRE] Applying preset: %PRESET%

if /i "%PRESET%"=="TOURNAMENT" (
    (
        echo # Fortnite Optimizer - PRESET: TOURNAMENT
        echo # Maximum FPS + Minimum ping for ranked/tournaments
        echo PRESET=TOURNAMENT
        echo FPS_BOOST=1
        echo VISUAL_EFFECTS=1
        echo DISABLE_DVRGAME=1
        echo POWER_PLAN=1
        echo HAGS_DISABLE=1
        echo HIGH_PRIORITY=1
        echo NETWORK_BOOST=1
        echo NAGLE_OFF=1
        echo DNS_OPTIMIZE=1
        echo DNS_PRIMARY=1.1.1.1
        echo DNS_SECONDARY=1.0.0.1
        echo CPU_UNPARK=1
        echo MSI_MODE=1
        echo MOUSE_OPTIMIZE=1
        echo FORTNITE_INI=1
        echo PAGEFILE_OPTIMIZE=0
        echo RESOLUTION_CHANGE=1
        echo RESOLUTION_WIDTH=1920
        echo RESOLUTION_HEIGHT=1080
        echo RESOLUTION_REFRESH=0
        echo PING_MONITOR=1
        echo RAM_CLEANUP=1
        echo KILL_USELESS=1
        echo LAUNCH_EPIC=1
        echo EPIC_PATH=C:\Program Files ^(x86^)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe
    ) > "%CFG%"
    echo [PRE] + TOURNAMENT preset applied
    echo [PRE]   - All optimizations: ON
    echo [PRE]   - HAGS: OFF ^(best for GTX/RTX 20xx^)
    echo [PRE]   - DNS: Cloudflare 1.1.1.1
    echo [PRE]   - Resolution: 1920x1080
    goto :done
)

if /i "%PRESET%"=="PERFORMANCE" (
    (
        echo # Fortnite Optimizer - PRESET: PERFORMANCE
        echo # High FPS + stability
        echo PRESET=PERFORMANCE
        echo FPS_BOOST=1
        echo VISUAL_EFFECTS=1
        echo DISABLE_DVRGAME=1
        echo POWER_PLAN=1
        echo HAGS_DISABLE=0
        echo HIGH_PRIORITY=1
        echo NETWORK_BOOST=1
        echo NAGLE_OFF=1
        echo DNS_OPTIMIZE=1
        echo DNS_PRIMARY=1.1.1.1
        echo DNS_SECONDARY=8.8.8.8
        echo CPU_UNPARK=1
        echo MSI_MODE=1
        echo MOUSE_OPTIMIZE=1
        echo FORTNITE_INI=1
        echo PAGEFILE_OPTIMIZE=0
        echo RESOLUTION_CHANGE=0
        echo RESOLUTION_WIDTH=1920
        echo RESOLUTION_HEIGHT=1080
        echo RESOLUTION_REFRESH=0
        echo PING_MONITOR=1
        echo RAM_CLEANUP=1
        echo KILL_USELESS=1
        echo LAUNCH_EPIC=1
        echo EPIC_PATH=C:\Program Files ^(x86^)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe
    ) > "%CFG%"
    echo [PRE] + PERFORMANCE preset applied
    echo [PRE]   - HAGS: ON ^(good for RTX 30xx+^)
    echo [PRE]   - Resolution: no change
    goto :done
)

if /i "%PRESET%"=="BALANCED" (
    (
        echo # Fortnite Optimizer - PRESET: BALANCED
        echo # Balance of FPS and quality
        echo PRESET=BALANCED
        echo FPS_BOOST=1
        echo VISUAL_EFFECTS=0
        echo DISABLE_DVRGAME=1
        echo POWER_PLAN=1
        echo HAGS_DISABLE=0
        echo HIGH_PRIORITY=1
        echo NETWORK_BOOST=1
        echo NAGLE_OFF=1
        echo DNS_OPTIMIZE=1
        echo DNS_PRIMARY=8.8.8.8
        echo DNS_SECONDARY=8.8.4.4
        echo CPU_UNPARK=1
        echo MSI_MODE=0
        echo MOUSE_OPTIMIZE=1
        echo FORTNITE_INI=0
        echo PAGEFILE_OPTIMIZE=0
        echo RESOLUTION_CHANGE=0
        echo RESOLUTION_WIDTH=1920
        echo RESOLUTION_HEIGHT=1080
        echo RESOLUTION_REFRESH=0
        echo PING_MONITOR=1
        echo RAM_CLEANUP=1
        echo KILL_USELESS=0
        echo LAUNCH_EPIC=1
        echo EPIC_PATH=C:\Program Files ^(x86^)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe
    ) > "%CFG%"
    echo [PRE] + BALANCED preset applied
    echo [PRE]   - MSI Mode: OFF ^(safer^)
    echo [PRE]   - INI tweaks: OFF ^(standard quality^)
    echo [PRE]   - Processes: not killed
    goto :done
)

if /i "%PRESET%"=="STREAMING" (
    (
        echo # Fortnite Optimizer - PRESET: STREAMING
        echo # For streamers: FPS + good image quality
        echo PRESET=STREAMING
        echo FPS_BOOST=1
        echo VISUAL_EFFECTS=0
        echo DISABLE_DVRGAME=0
        echo POWER_PLAN=1
        echo HAGS_DISABLE=0
        echo HIGH_PRIORITY=1
        echo NETWORK_BOOST=1
        echo NAGLE_OFF=1
        echo DNS_OPTIMIZE=1
        echo DNS_PRIMARY=1.1.1.1
        echo DNS_SECONDARY=8.8.8.8
        echo CPU_UNPARK=1
        echo MSI_MODE=0
        echo MOUSE_OPTIMIZE=1
        echo FORTNITE_INI=0
        echo PAGEFILE_OPTIMIZE=0
        echo RESOLUTION_CHANGE=0
        echo RESOLUTION_WIDTH=1920
        echo RESOLUTION_HEIGHT=1080
        echo RESOLUTION_REFRESH=0
        echo PING_MONITOR=0
        echo RAM_CLEANUP=1
        echo KILL_USELESS=0
        echo LAUNCH_EPIC=1
        echo EPIC_PATH=C:\Program Files ^(x86^)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe
    ) > "%CFG%"
    echo [PRE] + STREAMING preset applied
    echo [PRE]   - Game DVR: ON ^(for capture^)
    echo [PRE]   - INI tweaks: OFF ^(normal quality^)
    echo [PRE]   - Processes: not killed ^(keeps OBS^)
    goto :done
)

echo [PRE] ! Unknown preset: %PRESET%
echo [PRE] Available: TOURNAMENT / PERFORMANCE / BALANCED / STREAMING

:done
echo [PRE] =======================================
echo [PRE] Preset %PRESET% saved to settings.cfg
echo [PRE] =======================================
endlocal
