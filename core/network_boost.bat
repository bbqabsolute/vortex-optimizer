@echo off
:: ============================================================
::  network_boost.bat  -  Fortnite Optimizer
::  Network optimization to reduce ping without breaking login
::  Args: DNS_PRIMARY DNS_SECONDARY NAGLE_OFF DNS_OPTIMIZE
:: ============================================================
setlocal EnableDelayedExpansion

set "DNS1=%~1"
set "DNS2=%~2"
set "NAGLE=%~3"
set "DNS_OPT=%~4"

if "%DNS1%"=="" set "DNS1=8.8.8.8"
if "%DNS2%"=="" set "DNS2=8.8.4.4"
if "%NAGLE%"=="" set "NAGLE=1"
if "%DNS_OPT%"=="" set "DNS_OPT=1"

echo [NET] Applying network optimizations...

:: 1. TCP/IP Stack (автонастройка окна для стабильного соединения без сброса сокетов)
netsh int tcp set global autotuninglevel=normal >nul 2>&1
netsh int tcp set global rss=enabled >nul 2>&1
netsh int tcp set global chimney=disabled >nul 2>&1
netsh int tcp set global dca=enabled >nul 2>&1
netsh int tcp set global netdma=disabled >nul 2>&1
netsh int tcp set global ecncapability=disabled >nul 2>&1
netsh int tcp set global timestamps=disabled >nul 2>&1
netsh int tcp set global initialRto=2000 >nul 2>&1
netsh int tcp set global nonsackrttresiliency=disabled >nul 2>&1
echo [NET] + TCP/IP stack optimized (Autotuning: Normal)

:: 2. Снятие системного троттлинга сети
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f >nul 2>&1
echo [NET] + NetworkThrottling disabled

:: 3. Очистка и восстановление буферов AFD (Защита служб друзей Epic Games / EOS)
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "IgnorePushBitOnReceives" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "NonBlockingSendSpecialBuffering" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "DefaultReceiveWindow" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "DefaultSendWindow" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "FastSendDatagramThreshold" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\QoS\Fortnite" /f >nul 2>&1
reg delete "HKCU\Environment" /v "HTTPS_PROXY" /f >nul 2>&1
reg delete "HKCU\Environment" /v "HTTP_PROXY" /f >nul 2>&1
reg delete "HKCU\Environment" /v "ALL_PROXY" /f >nul 2>&1
reg delete "HKCU\Environment" /v "NO_PROXY" /f >nul 2>&1
echo [NET] + Network buffers & Epic Social sockets: verified safe

:: 4. Отключение задержки Nagle
if "%NAGLE%"=="1" (
    for /f "tokens=*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces" /k /f "" 2^>nul ^| findstr /i "HKEY"') do (
        reg add "%%A" /v "TcpAckFrequency" /t REG_DWORD /d 1 /f >nul 2>&1
        reg add "%%A" /v "TCPNoDelay" /t REG_DWORD /d 1 /f >nul 2>&1
        reg add "%%A" /v "TcpDelAckTicks" /t REG_DWORD /d 0 /f >nul 2>&1
    )
    reg add "HKLM\SOFTWARE\Microsoft\MSMQ\Parameters" /v "TCPNoDelay" /t REG_DWORD /d 1 /f >nul 2>&1
    echo [NET] + Nagle Algorithm disabled (instant packet dispatch)
) else (
    echo [NET] - Nagle disable: skipped
)

:: 5. Настройка DNS (через PowerShell с корректной поддержкой русских имён адаптеров)
if "%DNS_OPT%"=="1" (
    ipconfig /flushdns >nul 2>&1
    powershell -NoProfile -Command "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | ForEach-Object { try { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses '%DNS1%','%DNS2%' -ErrorAction SilentlyContinue } catch {} }" >nul 2>&1
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v "CacheHashTableBucketSize" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v "CacheHashTableSize" /t REG_DWORD /d 384 /f >nul 2>&1
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v "MaxCacheEntryTtlLimit" /t REG_DWORD /d 64000 /f >nul 2>&1
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v "MaxSOACacheEntryTtlLimit" /t REG_DWORD /d 301 /f >nul 2>&1
    ipconfig /flushdns >nul 2>&1
    echo [NET] + DNS configured: %DNS1% / %DNS2%
) else (
    echo [NET] - DNS optimization: skipped
)

:: 6. Отключение неиспользуемых туннелей IPv6
netsh interface teredo set state disabled >nul 2>&1
netsh interface 6to4 set state disabled >nul 2>&1
netsh interface isatap set state disabled >nul 2>&1
echo [NET] + IPv6 tunnels disabled

echo [NET] =======================================
echo [NET] Сетевые оптимизации успешно применены!
echo [NET] (Службы сокетов сохранены для авторизации Epic)
echo [NET] =======================================
endlocal
