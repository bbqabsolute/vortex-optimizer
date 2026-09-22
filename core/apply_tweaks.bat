@echo off
:: ============================================================
::  apply_tweaks.bat  -  Fortnite Optimizer
::  Additional system registry tweaks for performance
::  Argument 1: HAGS_DISABLE (0/1)
:: ============================================================
setlocal EnableDelayedExpansion

set "HAGS=%~1"
if "%HAGS%"=="" set "HAGS=0"

echo [TWK] Applying system tweaks...

reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f >nul 2>&1
echo [TWK] + Windows Game Mode enabled

bcdedit /deletevalue useplatformclock >nul 2>&1
echo [TWK] + HPET optimized

if "%HAGS%"=="1" (
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 1 /f >nul 2>&1
    echo [TWK] + HAGS disabled ^(recommended for GTX 10xx / RTX 20xx^)
) else (
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f >nul 2>&1
    echo [TWK] - HAGS enabled ^(recommended for RTX 30xx+^)
)

reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "ClearPageFileAtShutdown" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "DisablePagingExecutive" /t REG_DWORD /d 1 /f >nul 2>&1
echo [TWK] + Memory management optimized

sc stop SysMain >nul 2>&1
sc config SysMain start= disabled >nul 2>&1
echo [TWK] + SysMain ^(Superfetch^) disabled

reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "IRQ8Priority" /t REG_DWORD /d 1 /f >nul 2>&1
echo [TWK] + Task scheduler optimized

sc config DiagTrack start= disabled >nul 2>&1
sc stop DiagTrack >nul 2>&1
sc config dmwappushsvc start= disabled >nul 2>&1
sc stop dmwappushsvc >nul 2>&1
sc config Fax start= disabled >nul 2>&1
echo [TWK] + Unnecessary services disabled

reg query "HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm" >nul 2>&1
if %errorlevel%==0 (
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak" /v "DisplayPowerSaving" /t REG_DWORD /d 0 /f >nul 2>&1
    reg add "HKLM\SOFTWARE\NVIDIA Corporation\Global\NVTweak" /v "Coolbits" /t REG_DWORD /d 8 /f >nul 2>&1
    echo [TWK] + NVIDIA tweaks applied
) else (
    echo [TWK] - NVIDIA not detected, skipping
)

reg query "HKLM\SYSTEM\CurrentControlSet\Services\amdwddmg" >nul 2>&1
if %errorlevel%==0 (
    echo [TWK] + AMD GPU detected
) else (
    echo [TWK] - AMD GPU not detected
)

set "FN_SETTINGS=%LOCALAPPDATA%\FortniteGame\Saved\Config\WindowsClient"
if exist "%FN_SETTINGS%\GameUserSettings.ini" (
    powershell -NoProfile -Command ^
        "$file='%FN_SETTINGS%\GameUserSettings.ini';" ^
        "$content=Get-Content $file;" ^
        "$content=$content -replace 'bUseVSync=True','bUseVSync=False';" ^
        "$content=$content -replace 'FrameRateLimit=\d+','FrameRateLimit=0.000000';" ^
        "$content | Set-Content $file" >nul 2>&1
    echo [TWK] + Fortnite VSync disabled, FPS cap removed
) else (
    echo [TWK] - Fortnite GameUserSettings.ini not found
)

echo [TWK] =======================================
echo [TWK] System tweaks applied!
echo [TWK] =======================================
endlocal
