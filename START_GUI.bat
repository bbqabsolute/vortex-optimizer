@echo off
:: ============================================================
::  START_GUI.bat - VORTEX v5.0
::  Unleash Competitive Performance
::  Reliable Python GUI Launcher with Administrator Elevation
:: ============================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title VORTEX — Unleash Competitive Performance

:: 1. Проверка прав администратора и автоматический вызов UAC
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo  [UAC] Запрос прав администратора для VORTEX...
    echo ========================================================
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: 1.1. Автоматическое восстановление сокетов и служб друзей Fortnite (EOS / AFD)
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "IgnorePushBitOnReceives" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "NonBlockingSendSpecialBuffering" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "DefaultReceiveWindow" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "DefaultSendWindow" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "FastSendDatagramThreshold" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\QoS\Fortnite" /f >nul 2>&1

:: 2. Detect Python executable location
set "PY_CMD="

if exist "C:\Users\bbq\AppData\Local\Programs\Python\Python311\python.exe" (
    set "PY_CMD=C:\Users\bbq\AppData\Local\Programs\Python\Python311\python.exe"
    goto :py_found
)
if defined LOCALAPPDATA (
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        goto :py_found
    )
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        goto :py_found
    )
    if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        goto :py_found
    )
)
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :py_found
)
where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :py_found
)

:py_found
if not defined PY_CMD (
    echo.
    echo ========================================================
    echo  [ERROR] Python was not found on your system!
    echo  Please install Python 3.11 from python.org
    echo ========================================================
    echo.
    pause
    exit /b 1
)

:: 2. Ensure PATH includes Python directory and Scripts
for %%I in ("%PY_CMD%") do (
    set "PATH=%%~dpI;%%~dpIScripts;!PATH!"
)

:: 3. Run GUI
"%PY_CMD%" "%~dp0gui.py"
if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo  The GUI closed with code %errorlevel%.
    echo  If this was unexpected, see gui_crash.log
    echo ========================================================
    echo.
    pause
)

exit /b
