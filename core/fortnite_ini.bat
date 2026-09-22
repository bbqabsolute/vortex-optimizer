@echo off
:: ============================================================
::  fortnite_ini.bat  -  Fortnite Optimizer
::  Deep tweaks for Engine.ini and GameUserSettings.ini
:: ============================================================
setlocal EnableDelayedExpansion

set "FN_CFG=%LOCALAPPDATA%\FortniteGame\Saved\Config\WindowsClient"

echo [INI] Searching for Fortnite config files...

if not exist "%FN_CFG%" (
    echo [INI] ! Config folder not found: %FN_CFG%
    echo [INI] ! Fortnite not installed or non-standard path
    goto :end
)

echo [INI] + Found: %FN_CFG%
echo [INI] Applying optimized settings...

set "SCRIPT=%~dp0fortnite_ini.ps1"
if exist "%SCRIPT%" (
    powershell -ExecutionPolicy Bypass -NoProfile -File "%SCRIPT%"
) else (
    echo [INI] ! Script fortnite_ini.ps1 not found
)

set "SCALABILITY=%FN_CFG%\Scalability.ini"
(
    echo [ScalabilityGroups]
    echo sg.ResolutionQuality=100
    echo sg.ViewDistanceQuality=1
    echo sg.AntiAliasingQuality=0
    echo sg.ShadowQuality=0
    echo sg.GlobalIlluminationQuality=0
    echo sg.ReflectionQuality=0
    echo sg.PostProcessQuality=0
    echo sg.TextureQuality=2
    echo sg.EffectsQuality=0
    echo sg.FoliageQuality=0
    echo sg.ShadingQuality=0
    echo sg.LandscapeQuality=2
) > "%SCALABILITY%" 2>nul
echo [INI] + Scalability.ini: shadows/effects/AA/reflections = 0

echo [INI] =======================================
echo [INI] Fortnite INI tweaks applied!
echo [INI] Backups saved as *.backup
echo [INI] =======================================

:end
endlocal
