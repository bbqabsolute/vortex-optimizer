@echo off
:: ============================================================
::  ping_monitor.bat  -  Fortnite Optimizer
::  Ping test to Fortnite servers across all regions
::  Unique: shows best region BEFORE launching
:: ============================================================
setlocal EnableDelayedExpansion

echo.
echo  +=======================================================+
echo  ^|        FORTNITE SERVER PING TEST                    ^|
echo  +=======================================================+
echo.
echo  Measuring latency to Fortnite servers...
echo.

set "SCRIPT=%~dp0ping_monitor.ps1"
if exist "%SCRIPT%" (
    powershell -ExecutionPolicy Bypass -NoProfile -File "%SCRIPT%"
) else (
    echo [PING] ! Script ping_monitor.ps1 not found
)

echo.
echo  -------------------------------------------------------
endlocal
