@echo off
:: ============================================================
::  cpu_unpark.bat  -  Fortnite Optimizer
::  Unpark all CPU cores + disable throttling
::  Unique: guarantees ALL cores are active
:: ============================================================
setlocal EnableDelayedExpansion

echo [CPU] Unparking CPU cores...

set "SG=54533251-82be-4824-96c1-47b60b740d00"
set "PARKING=0cc5b647-c1df-4637-891a-dec35c318583"
set "MINSTATE=893dee8e-2bef-41e0-89c6-b55d0929964c"
set "MAXSTATE=bc5038f7-23e0-4960-96da-33abaf5935ec"
set "BOOSTMODE=be337238-0d82-4146-a960-4f3749d470c7"
set "IDLEDISABLE=5d76a2ca-e8c0-402f-a133-2158492d58ad"

powercfg /setacvalueindex SCHEME_CURRENT %SG% %PARKING% 100 >nul 2>&1
powercfg /setdcvalueindex SCHEME_CURRENT %SG% %PARKING% 100 >nul 2>&1
echo [CPU] + Core Parking disabled ^(100%% cores active^)

powercfg /setacvalueindex SCHEME_CURRENT %SG% %MINSTATE% 100 >nul 2>&1
powercfg /setdcvalueindex SCHEME_CURRENT %SG% %MINSTATE% 100 >nul 2>&1
echo [CPU] + Min CPU frequency: 100%%

powercfg /setacvalueindex SCHEME_CURRENT %SG% %MAXSTATE% 100 >nul 2>&1
powercfg /setdcvalueindex SCHEME_CURRENT %SG% %MAXSTATE% 100 >nul 2>&1
echo [CPU] + Max CPU frequency: 100%%

powercfg /setacvalueindex SCHEME_CURRENT %SG% %BOOSTMODE% 3 >nul 2>&1
echo [CPU] + Turbo Boost: Aggressive mode

powercfg /setacvalueindex SCHEME_CURRENT %SG% %IDLEDISABLE% 1 >nul 2>&1
echo [CPU] + CPU Idle states: disabled

powercfg /setactive SCHEME_CURRENT >nul 2>&1

reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\%SG%\%PARKING%" /v "Attributes" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "IRQ8Priority" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "IRQ16Priority" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d 0x26 /f >nul 2>&1

echo [CPU] CPU Information:
for /f "tokens=2 delims==" %%A in ('wmic cpu get Name /value 2^>nul ^| findstr "="') do echo [CPU]   %%A
for /f "tokens=2 delims==" %%A in ('wmic cpu get NumberOfCores /value 2^>nul ^| findstr "="') do echo [CPU]   Cores: %%A
for /f "tokens=2 delims==" %%A in ('wmic cpu get NumberOfLogicalProcessors /value 2^>nul ^| findstr "="') do echo [CPU]   Threads: %%A

echo [CPU] =======================================
echo [CPU] CPU Unpark + Boost ready!
echo [CPU] =======================================
endlocal
