' ============================================================
'  show_menu.vbs  -  Fortnite Optimizer v2.0
'  Full settings menu - all options in one place
' ============================================================
Option Explicit

Dim oFSO, oShell
Set oFSO   = CreateObject("Scripting.FileSystemObject")
Set oShell = CreateObject("WScript.Shell")

Dim baseDir
baseDir = oFSO.GetParentFolderName(WScript.ScriptFullName)
baseDir = oFSO.GetParentFolderName(baseDir)

Dim cfgPath
cfgPath = baseDir & "\config\settings.cfg"

' --- Load settings ---
Dim cfg
Set cfg = CreateObject("Scripting.Dictionary")

cfg("PRESET")             = "CUSTOM"
cfg("FPS_BOOST")          = "1"
cfg("VISUAL_EFFECTS")     = "1"
cfg("DISABLE_DVRGAME")    = "1"
cfg("POWER_PLAN")         = "1"
cfg("HAGS_DISABLE")       = "0"
cfg("HIGH_PRIORITY")      = "1"
cfg("NETWORK_BOOST")      = "1"
cfg("NAGLE_OFF")          = "1"
cfg("DNS_OPTIMIZE")       = "1"
cfg("DNS_PRIMARY")        = "1.1.1.1"
cfg("DNS_SECONDARY")      = "8.8.8.8"
cfg("CPU_UNPARK")         = "1"
cfg("MSI_MODE")           = "1"
cfg("MOUSE_OPTIMIZE")     = "1"
cfg("FORTNITE_INI")       = "1"
cfg("PAGEFILE_OPTIMIZE")  = "0"
cfg("RESOLUTION_CHANGE")  = "0"
cfg("RESOLUTION_WIDTH")   = "1920"
cfg("RESOLUTION_HEIGHT")  = "1080"
cfg("RESOLUTION_REFRESH") = "0"
cfg("PING_MONITOR")       = "1"
cfg("RAM_CLEANUP")        = "1"
cfg("KILL_USELESS")       = "1"
cfg("LAUNCH_EPIC")        = "1"
cfg("EPIC_PATH")          = "C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"

If oFSO.FileExists(cfgPath) Then
    Dim oFile, line, parts
    Set oFile = oFSO.OpenTextFile(cfgPath, 1)
    Do While Not oFile.AtEndOfStream
        line = Trim(oFile.ReadLine())
        If Len(line) > 0 And Left(line,1) <> "#" Then
            parts = Split(line, "=", 2)
            If UBound(parts) = 1 Then
                cfg(Trim(parts(0))) = Trim(parts(1))
            End If
        End If
    Loop
    oFile.Close
End If

' --- Helper functions ---
Function YN(key)
    If cfg(key) = "1" Then YN = "ON " Else YN = "OFF"
End Function

Function Toggle(key)
    If cfg(key) = "1" Then cfg(key) = "0" Else cfg(key) = "1"
    cfg("PRESET") = "CUSTOM"
End Function

Function PadR(s, n)
    PadR = Left(s & Space(n), n)
End Function

' --- Main menu loop ---
Dim choice, done
done = False

Do While Not done
    Dim menuText
    menuText = "+================================================+" & vbCrLf & _
               "|   FORTNITE OPTIMIZER v2.0 - SETTINGS         |" & vbCrLf & _
               "|   Preset: " & UCase(cfg("PRESET")) & Space(35 - Len(cfg("PRESET"))) & "|" & vbCrLf & _
               "+================================================+" & vbCrLf & _
               "|  -- PRESETS --------------------------------   |" & vbCrLf & _
               "|  P  -> Select preset                          |" & vbCrLf & _
               "+================================================+" & vbCrLf & _
               "|  -- FPS --------------------------------       |" & vbCrLf & _
               "|  1  FPS boost              [" & PadR(YN("FPS_BOOST"),3) & "]              |" & vbCrLf & _
               "|  2  Disable Game DVR       [" & PadR(YN("DISABLE_DVRGAME"),3) & "]              |" & vbCrLf & _
               "|  3  Ultra Performance plan [" & PadR(YN("POWER_PLAN"),3) & "]              |" & vbCrLf & _
               "|  4  Disable Windows FX     [" & PadR(YN("VISUAL_EFFECTS"),3) & "]              |" & vbCrLf & _
               "|  5  HAGS OFF (GTX/RTX20)  [" & PadR(YN("HAGS_DISABLE"),3) & "]              |" & vbCrLf & _
               "|  6  HIGH process priority  [" & PadR(YN("HIGH_PRIORITY"),3) & "]              |" & vbCrLf & _
               "+================================================+" & vbCrLf & _
               "|  -- PING / NETWORK --------------------        |" & vbCrLf & _
               "|  7  Network optimizations  [" & PadR(YN("NETWORK_BOOST"),3) & "]              |" & vbCrLf & _
               "|  8  Nagle Algorithm OFF    [" & PadR(YN("NAGLE_OFF"),3) & "]              |" & vbCrLf & _
               "|  9  DNS optimization       [" & PadR(YN("DNS_OPTIMIZE"),3) & "]              |" & vbCrLf & _
               "|  10 Configure DNS servers" & vbCrLf & _
               "+================================================+" & vbCrLf & _
               "|  -- CPU / GPU -------------------------        |" & vbCrLf & _
               "|  11 CPU Unpark (all cores) [" & PadR(YN("CPU_UNPARK"),3) & "]              |" & vbCrLf & _
               "|  12 MSI Mode GPU/NIC       [" & PadR(YN("MSI_MODE"),3) & "]              |" & vbCrLf & _
               "+================================================+" & vbCrLf & _
               "|  -- MOUSE / AIM -----------------------        |" & vbCrLf & _
               "|  13 Mouse 1:1 optimization [" & PadR(YN("MOUSE_OPTIMIZE"),3) & "]              |" & vbCrLf & _
               "+================================================+" & vbCrLf & _
               "|  -- FORTNITE --------------------------        |" & vbCrLf & _
               "|  14 INI tweaks (Engine.ini)[" & PadR(YN("FORTNITE_INI"),3) & "]              |" & vbCrLf & _
               "|  15 Pagefile optimization  [" & PadR(YN("PAGEFILE_OPTIMIZE"),3) & "]              |" & vbCrLf & _
               "|  16 Change resolution -> " & cfg("RESOLUTION_WIDTH") & "x" & cfg("RESOLUTION_HEIGHT") & " [" & PadR(YN("RESOLUTION_CHANGE"),3) & "]    |" & vbCrLf & _
               "+================================================+" & vbCrLf & _
               "|  -- LAUNCH ----------------------------        |" & vbCrLf & _
               "|  17 Ping monitor on launch [" & PadR(YN("PING_MONITOR"),3) & "]              |" & vbCrLf & _
               "|  18 RAM + temp cleanup     [" & PadR(YN("RAM_CLEANUP"),3) & "]              |" & vbCrLf & _
               "|  19 Kill unnecessary procs [" & PadR(YN("KILL_USELESS"),3) & "]              |" & vbCrLf & _
               "|  20 Epic Games path" & vbCrLf & _
               "+================================================+" & vbCrLf & _
               "|  21 Restore ALL changes to defaults           |" & vbCrLf & _
               "|  22 Fortnite server ping test                 |" & vbCrLf & _
               "+================================================+" & vbCrLf & _
               "  0  Save and exit" & vbCrLf & vbCrLf & _
               "Enter option number:"

    choice = InputBox(menuText, "Fortnite Optimizer v2.0 - Settings", "0")

    If IsNull(choice) Or choice = "" Or choice = "0" Then
        done = True
    ElseIf UCase(choice) = "P" Then
        Dim presetVBS
        presetVBS = baseDir & "\vbs\preset_picker.vbs"
        If oFSO.FileExists(presetVBS) Then
            oShell.Run "wscript.exe """ & presetVBS & """", 1, True
            If oFSO.FileExists(cfgPath) Then
                Set oFile = oFSO.OpenTextFile(cfgPath, 1)
                Do While Not oFile.AtEndOfStream
                    line = Trim(oFile.ReadLine())
                    If Len(line) > 0 And Left(line,1) <> "#" Then
                        parts = Split(line, "=", 2)
                        If UBound(parts) = 1 And cfg.Exists(Trim(parts(0))) Then
                            cfg(Trim(parts(0))) = Trim(parts(1))
                        End If
                    End If
                Loop
                oFile.Close
            End If
        End If
    ElseIf choice = "1"  Then Toggle "FPS_BOOST"
    ElseIf choice = "2"  Then Toggle "DISABLE_DVRGAME"
    ElseIf choice = "3"  Then Toggle "POWER_PLAN"
    ElseIf choice = "4"  Then Toggle "VISUAL_EFFECTS"
    ElseIf choice = "5"  Then
        Dim hagsmsg
        If cfg("HAGS_DISABLE") = "0" Then
            hagsmsg = "HAGS will be DISABLED." & vbCrLf & "Recommended for: GTX 10xx, RTX 20xx"
        Else
            hagsmsg = "HAGS will be ENABLED." & vbCrLf & "Recommended for: RTX 30xx, RTX 40xx"
        End If
        If MsgBox(hagsmsg & vbCrLf & vbCrLf & "Toggle?", 36, "HAGS") = 6 Then Toggle "HAGS_DISABLE"
    ElseIf choice = "6"  Then Toggle "HIGH_PRIORITY"
    ElseIf choice = "7"  Then Toggle "NETWORK_BOOST"
    ElseIf choice = "8"  Then Toggle "NAGLE_OFF"
    ElseIf choice = "9"  Then Toggle "DNS_OPTIMIZE"
    ElseIf choice = "10" Then
        Dim d1, d2
        d1 = InputBox("Primary DNS:", "DNS Settings", cfg("DNS_PRIMARY"))
        If Not IsNull(d1) And Len(Trim(d1)) > 0 Then cfg("DNS_PRIMARY") = Trim(d1)
        d2 = InputBox("Secondary DNS:", "DNS Settings", cfg("DNS_SECONDARY"))
        If Not IsNull(d2) And Len(Trim(d2)) > 0 Then cfg("DNS_SECONDARY") = Trim(d2)
    ElseIf choice = "11" Then Toggle "CPU_UNPARK"
    ElseIf choice = "12" Then
        If cfg("MSI_MODE") = "0" Then
            If MsgBox("MSI Mode reduces GPU/NIC interrupt latency." & vbCrLf & _
                "Requires reboot to take full effect." & vbCrLf & vbCrLf & "Enable?", 36, "MSI Mode") = 6 Then
                Toggle "MSI_MODE"
            End If
        Else
            Toggle "MSI_MODE"
        End If
    ElseIf choice = "13" Then Toggle "MOUSE_OPTIMIZE"
    ElseIf choice = "14" Then
        If cfg("FORTNITE_INI") = "0" Then
            If MsgBox("INI tweaks disable: shadows, bloom, DoF, fog, grass." & vbCrLf & _
                "Backups created automatically (*.backup)." & vbCrLf & vbCrLf & "Enable?", 36, "INI Tweaks") = 6 Then
                Toggle "FORTNITE_INI"
            End If
        Else
            Toggle "FORTNITE_INI"
        End If
    ElseIf choice = "15" Then
        If cfg("PAGEFILE_OPTIMIZE") = "0" Then
            If MsgBox("Pagefile will be set to fixed size." & vbCrLf & _
                "Eliminates stutters from pagefile resizing." & vbCrLf & _
                "Requires reboot." & vbCrLf & vbCrLf & "Enable?", 36, "Pagefile") = 6 Then
                Toggle "PAGEFILE_OPTIMIZE"
            End If
        Else
            Toggle "PAGEFILE_OPTIMIZE"
        End If
    ElseIf choice = "16" Then
        Dim resVBS
        resVBS = baseDir & "\vbs\resolution_picker.vbs"
        If oFSO.FileExists(resVBS) Then
            oShell.Run "wscript.exe """ & resVBS & """", 1, True
            If oFSO.FileExists(cfgPath) Then
                Set oFile = oFSO.OpenTextFile(cfgPath, 1)
                Do While Not oFile.AtEndOfStream
                    line = Trim(oFile.ReadLine())
                    If Len(line) > 0 And Left(line,1) <> "#" Then
                        parts = Split(line, "=", 2)
                        If UBound(parts) = 1 And cfg.Exists(Trim(parts(0))) Then
                            cfg(Trim(parts(0))) = Trim(parts(1))
                        End If
                    End If
                Loop
                oFile.Close
            End If
        End If
    ElseIf choice = "17" Then Toggle "PING_MONITOR"
    ElseIf choice = "18" Then Toggle "RAM_CLEANUP"
    ElseIf choice = "19" Then Toggle "KILL_USELESS"
    ElseIf choice = "20" Then
        Dim ep
        ep = InputBox("Path to EpicGamesLauncher.exe:", "Epic Games Path", cfg("EPIC_PATH"))
        If Not IsNull(ep) And Len(Trim(ep)) > 0 Then cfg("EPIC_PATH") = Trim(ep)
    ElseIf choice = "21" Then
        If MsgBox("Rollback ALL optimizer changes?" & vbCrLf & _
            "All Windows settings will be restored to defaults.", 36, "Restore Defaults") = 6 Then
            oShell.Run """" & baseDir & "\core\restore_defaults.bat""", 1, True
            MsgBox "Rollback complete! Recommend restarting PC.", 64, "Done"
        End If
    ElseIf choice = "22" Then
        oShell.Run """" & baseDir & "\core\ping_monitor.bat""", 1, True
    End If
Loop

' --- Save settings ---
If Not oFSO.FolderExists(baseDir & "\config") Then
    oFSO.CreateFolder(baseDir & "\config")
End If

Dim oOut
Set oOut = oFSO.CreateTextFile(cfgPath, True)
oOut.WriteLine "# Fortnite Optimizer - Settings v2.0"
oOut.WriteLine "# Saved: " & Now()
oOut.WriteLine ""
Dim k
For Each k In cfg.Keys
    oOut.WriteLine k & "=" & cfg(k)
Next
oOut.Close

MsgBox "Settings saved!" & vbCrLf & vbCrLf & _
    "Preset: " & cfg("PRESET") & vbCrLf & _
    "Run LAUNCH_OPTIMIZER.bat to apply.", 64, "Saved"
