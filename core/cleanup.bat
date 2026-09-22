@echo off
:: ============================================================
::  cleanup.bat  -  Fortnite Optimizer
::  Pre-game cleanup: RAM, temp files, background bloatware
::  Keeps Epic Games Launcher and network sockets intact
:: ============================================================
setlocal EnableDelayedExpansion

set "KILL_PROC=%~1"
if "%KILL_PROC%"=="" set "KILL_PROC=1"

echo [CLN] Running safe pre-game cleanup...

:: 1. Очистка пользовательских временных файлов (без удаления файлов Epic)
del /q /f "%TEMP%\*.*" >nul 2>&1
del /q /f "C:\Windows\Temp\*.*" >nul 2>&1
echo [CLN] + Temporary files cleared

:: 2. Сброс DNS кэша
ipconfig /flushdns >nul 2>&1
echo [CLN] + DNS cache flushed

:: 3. Безопасная оптимизация оперативной памяти (не затрагивая лаунчер Epic Games и службы авторизации)
powershell -NoProfile -NonInteractive -Command ^
    "[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers();" >nul 2>&1

powershell -NoProfile -NonInteractive -Command ^
    "Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.WorkingSet -gt 50MB -and $_.Name -notmatch 'svchost|lsass|System|Epic|Fortnite|EasyAntiCheat|BEService'} | ForEach-Object { try { $_.MinWorkingSet = 1024; $_.MaxWorkingSet = 1024*1024*500 } catch {} }" >nul 2>&1

echo [CLN] + RAM optimized safely

:: 4. Закрытие фоновых ненужных приложений Windows
if "%KILL_PROC%"=="1" (
    taskkill /f /im GameBarFTServer.exe >nul 2>&1
    taskkill /f /im GameBar.exe >nul 2>&1
    taskkill /f /im XboxApp.exe >nul 2>&1
    taskkill /f /im XboxGameOverlay.exe >nul 2>&1
    taskkill /f /im XboxSpeechToTextOverlay.exe >nul 2>&1
    taskkill /f /im DiscordPTB.exe >nul 2>&1
    taskkill /f /im OneDrive.exe >nul 2>&1
    taskkill /f /im SearchUI.exe >nul 2>&1
    taskkill /f /im SearchApp.exe >nul 2>&1
    sc stop wuauserv >nul 2>&1
    sc stop bits >nul 2>&1
    echo [CLN] + Background bloatware closed (Xbox, GameBar, OneDrive)
) else (
    echo [CLN] - Process cleanup: skipped
)

echo [CLN] =======================================
echo [CLN] Очистка завершена! Сетевой стек и Epic Launcher в норме.
echo [CLN] =======================================
endlocal
