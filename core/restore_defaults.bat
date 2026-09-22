@echo off
:: ============================================================
::  restore_defaults.bat  -  Fortnite Optimizer
::  Full rollback of all optimizer changes to Windows defaults
:: ============================================================
setlocal EnableDelayedExpansion

echo [RST] Restoring all optimizer changes...
echo [RST] This may take 30-60 seconds...

powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e >nul 2>&1
echo [RST] + Power plan: restored to Balanced

bcdedit /deletevalue useplatformtick >nul 2>&1
bcdedit /deletevalue disabledynamictick >nul 2>&1
echo [RST] + System timer: restored

reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 1 /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /f >nul 2>&1
echo [RST] + Game DVR: restored

reg delete "HKCU\System\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /f >nul 2>&1
reg delete "HKCU\System\GameConfigStore" /v "GameDVR_HonorUserFSEBehaviorMode" /f >nul 2>&1
reg delete "HKCU\System\GameConfigStore" /v "GameDVR_DXGIHonorFSEWindowsCompatible" /f >nul 2>&1
echo [RST] + Fullscreen Optimizations: restored

reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d 0 /f >nul 2>&1
echo [RST] + Visual effects: restored

netsh int tcp set global autotuninglevel=normal >nul 2>&1
netsh int tcp set global congestionprovider=default >nul 2>&1
netsh int tcp set global ecncapability=default >nul 2>&1
netsh int tcp set global timestamps=default >nul 2>&1
netsh int tcp set global initialRto=3000 >nul 2>&1
echo [RST] + TCP/IP stack: restored

reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 10 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d 20 /f >nul 2>&1
echo [RST] + NetworkThrottling: restored

reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\QoS\Fortnite" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "IgnorePushBitOnReceives" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "NonBlockingSendSpecialBuffering" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "DefaultReceiveWindow" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "DefaultSendWindow" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v "FastSendDatagramThreshold" /f >nul 2>&1
echo [RST] + QoS & AFD socket rules: restored to defaults

for /f "tokens=*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces" /k /f "" 2^>nul ^| findstr /i "HKEY"') do (
    reg delete "%%A" /v "TcpAckFrequency" /f >nul 2>&1
    reg delete "%%A" /v "TCPNoDelay" /f >nul 2>&1
    reg delete "%%A" /v "TcpDelAckTicks" /f >nul 2>&1
)
echo [RST] + Nagle Algorithm: restored

powershell -NoProfile -Command "Get-NetAdapter | ForEach-Object { try { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses -ErrorAction SilentlyContinue } catch {} }" >nul 2>&1
reg delete "HKCU\Environment" /v "HTTPS_PROXY" /f >nul 2>&1
reg delete "HKCU\Environment" /v "HTTP_PROXY" /f >nul 2>&1
reg delete "HKCU\Environment" /v "ALL_PROXY" /f >nul 2>&1
reg delete "HKCU\Environment" /v "NO_PROXY" /f >nul 2>&1
ipconfig /flushdns >nul 2>&1
echo [RST] + DNS & Proxy: restored to defaults

netsh interface teredo set state default >nul 2>&1
netsh interface 6to4 set state default >nul 2>&1
netsh interface isatap set state default >nul 2>&1
echo [RST] + IPv6 tunnels: restored

reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f >nul 2>&1
echo [RST] + HAGS: restored

sc config WSearch start= delayed-auto >nul 2>&1
net start WSearch >nul 2>&1
sc config SysMain start= auto >nul 2>&1
net start SysMain >nul 2>&1
sc config wuauserv start= manual >nul 2>&1
sc config DiagTrack start= auto >nul 2>&1
echo [RST] + Services: restored

reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "DisablePagingExecutive" /t REG_DWORD /d 0 /f >nul 2>&1
echo [RST] + Memory management: restored

reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d 2 /f >nul 2>&1
echo [RST] + Win32 priority: restored

netsh winsock reset >nul 2>&1
echo [RST] + Winsock: reset

echo.
echo [RST] =====================================================
echo [RST] ALL CHANGES REVERTED!
echo [RST] RECOMMEND RESTARTING YOUR COMPUTER
echo [RST] =====================================================
echo.
pause
endlocal
