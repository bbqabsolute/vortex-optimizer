@echo off
:: ============================================================
::  mouse_optimize.bat  -  Fortnite Optimizer
::  1:1 aim without acceleration - maximum mouse accuracy
::  Unique: correct SmoothMouseXY curves for true 1:1
:: ============================================================
setlocal EnableDelayedExpansion

echo [MOU] Optimizing mouse settings...

reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d "0" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold1" /t REG_SZ /d "0" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold2" /t REG_SZ /d "0" /f >nul 2>&1
echo [MOU] + Mouse acceleration: DISABLED

reg add "HKCU\Control Panel\Mouse" /v "MouseSensitivity" /t REG_SZ /d "10" /f >nul 2>&1
echo [MOU] + Mouse sensitivity: 10 ^(neutral 1:1^)

reg add "HKCU\Control Panel\Mouse" /v "SmoothMouseXCurve" /t REG_BINARY /d 0000000000000000C0CC0C0000000080990C0000000000007A700E000000000000805B100000 /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "SmoothMouseYCurve" /t REG_BINARY /d 0000000000000000000038000000000000007000000000000000A800000000000000E0000000 /f >nul 2>&1
echo [MOU] + SmoothMouseXY curves: 1:1 ^(no acceleration^)

powershell -NoProfile -Command ^
    "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class M { [DllImport(\"user32.dll\")] public static extern bool SystemParametersInfo(uint a, uint b, IntPtr c, uint d); }'; [M]::SystemParametersInfo(0x0004, 0, [IntPtr]::Zero, 0x03);" >nul 2>&1

reg add "HKCU\Control Panel\Mouse" /v "DoubleClickSpeed" /t REG_SZ /d "500" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "DragWidth" /t REG_SZ /d "2" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "DragHeight" /t REG_SZ /d "2" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseHoverTime" /t REG_SZ /d "400" /f >nul 2>&1

echo [MOU]
echo [MOU] Mouse polling rate recommendations:
echo [MOU]   500Hz  - standard ^(most mice^)
echo [MOU]   1000Hz - optimal for Fortnite
echo [MOU]   2000Hz+ - top tier ^(Razer, Logitech Hero^)
echo [MOU]   Check in your mouse software!
echo [MOU]
echo [MOU] + Mouse optimization applied
echo [MOU] =======================================
echo [MOU] Mouse optimized for 1:1 aim!
echo [MOU] =======================================
endlocal
