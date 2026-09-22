@echo off
:: ============================================================
::  resolution.bat  -  Fortnite Optimizer
::  Change display resolution via Windows API (no downloads)
::  Supports stretched competitive resolutions
::  Args: WIDTH HEIGHT [REFRESH_RATE]
:: ============================================================
setlocal EnableDelayedExpansion

set "W=%~1"
set "H=%~2"
set "R=%~3"
if "%W%"=="" set "W=1920"
if "%H%"=="" set "H=1080"
if "%R%"=="" set "R=0"

echo [RES] Changing resolution to %W%x%H%...

set "SCRIPT=%~dp0resolution.ps1"
if exist "%SCRIPT%" (
    powershell -ExecutionPolicy Bypass -NoProfile -File "%SCRIPT%" -targetW %W% -targetH %H% -targetR %R%
) else (
    echo [RES] ! Script resolution.ps1 not found
)

echo [RES] =======================================
echo [RES] Resolution %W%x%H% set!
echo [RES] =======================================
endlocal
