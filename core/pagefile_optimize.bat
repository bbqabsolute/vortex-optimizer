@echo off
:: ============================================================
::  pagefile_optimize.bat  -  Fortnite Optimizer
::  Fixed pagefile size = eliminates resize stutters
:: ============================================================
setlocal EnableDelayedExpansion

echo [PGF] Optimizing pagefile...

set "SCRIPT=%~dp0pagefile_optimize.ps1"
if exist "%SCRIPT%" (
    powershell -ExecutionPolicy Bypass -NoProfile -File "%SCRIPT%"
) else (
    echo [PGF] ! Script pagefile_optimize.ps1 not found
)

reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "ClearPageFileAtShutdown" /t REG_DWORD /d 0 /f >nul 2>&1

echo [PGF] =======================================
echo [PGF] Pagefile optimized!
echo [PGF] Reboot required to apply pagefile size
echo [PGF] =======================================
endlocal
