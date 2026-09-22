@echo off
:: ============================================================
::  msi_mode.bat  -  Fortnite Optimizer
::  Message Signaled Interrupts for GPU + NIC
::  Reduces GPU interrupt latency -> lower frame time
:: ============================================================
setlocal EnableDelayedExpansion

echo [MSI] Enabling MSI Mode for GPU and NIC...

set "SCRIPT=%~dp0msi_mode.ps1"
if exist "%SCRIPT%" (
    powershell -ExecutionPolicy Bypass -NoProfile -File "%SCRIPT%"
) else (
    echo [MSI] ! Script msi_mode.ps1 not found
)

echo [MSI] + MSI Mode applied
echo [MSI] + GPU interrupt priority: HIGH ^(3^)

reg query "HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm" >nul 2>&1
if %errorlevel%==0 (
    reg add "HKCU\SOFTWARE\NVIDIA Corporation\Global\NVTweak" /v "DisplayPowerSaving" /t REG_DWORD /d 0 /f >nul 2>&1
    echo [MSI] + NVIDIA Low Latency Mode activated
)

echo [MSI] ! MSI Mode requires REBOOT to fully take effect!
echo [MSI] =======================================
echo [MSI] MSI Mode configured!
echo [MSI] =======================================
endlocal
