@echo off
:: ============================================================
::  launch_fortnite.bat  -  Fortnite Optimizer
::  Launches Fortnite with de-elevation (no UAC conflict)
::  Uses explorer.exe to strip Admin token before handing
::  the URI to Epic Games Launcher
:: ============================================================
setlocal EnableDelayedExpansion

echo [LAUNCH] Запуск Fortnite через Epic Games Launcher...

:: Сброс всех переменных прокси для защиты сетевой авторизации Epic Games
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "ALL_PROXY="
set "http_proxy="
set "https_proxy="
set "all_proxy="

:: 1. Ищем официальный ярлык Fortnite на рабочем столе
set "SHORTCUT="
if exist "%USERPROFILE%\Desktop\Fortnite.url"        set "SHORTCUT=%USERPROFILE%\Desktop\Fortnite.url"
if "%SHORTCUT%"=="" if exist "c:\Users\bbq\Desktop\Fortnite.url" set "SHORTCUT=c:\Users\bbq\Desktop\Fortnite.url"
if "%SHORTCUT%"=="" if exist "%PUBLIC%\Desktop\Fortnite.url"     set "SHORTCUT=%PUBLIC%\Desktop\Fortnite.url"

:: 2. URI-протокол Epic (запасной вариант)
set "FN_URI=com.epicgames.launcher://apps/fn%%3A4fe75bbc5a674f4f9b356b5c90567da5%%3AFortnite?action=launch&silent=true"

:: 3. Запуск через explorer.exe — он СНИМАЕТ Admin-права (деэлевация)
::    Это критично: Epic Games Launcher работает без Admin, и если мы
::    передадим запрос с Admin-токеном — он заблокирует вход в аккаунт.
if not "%SHORTCUT%"=="" (
    echo [LAUNCH] + Запуск через ярлык (деэлевация): %SHORTCUT%
    explorer.exe "%SHORTCUT%"
) else (
    echo [LAUNCH] + Запуск через URI-протокол Epic (деэлевация)
    explorer.exe "%FN_URI%"
)

:: 4. Назначение высокого приоритета процессу (фоновый монитор)
set "HIGH_PRIO=%~2"
if "%HIGH_PRIO%"=="" set "HIGH_PRIO=1"

if "%HIGH_PRIO%"=="1" (
    echo [LAUNCH] + Монитор приоритета: ожидание FortniteClient...
    start "" /B powershell -NoProfile -WindowStyle Hidden -Command ^
        "$done=$false; for($i=0;$i-lt60;$i++){$p=Get-Process 'FortniteClient-Win64-Shipping' -EA SilentlyContinue; if($p){try{$p.PriorityClass='High';$done=$true}catch{};break}; Start-Sleep 2}; if($done){Write-EventLog -LogName Application -Source 'Optimizer' -EventId 1 -Message 'FN High Priority set' -EA SilentlyContinue}"
)

echo [LAUNCH] Команда запуска отправлена. Форtnite загружается...
endlocal
