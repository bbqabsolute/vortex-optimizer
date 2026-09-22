' ============================================================
'  preset_picker.vbs  -  Fortnite Optimizer
'  Interactive preset selection with descriptions
' ============================================================
Option Explicit

Dim oShell, oFSO, baseDir, cfgPath
Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")

baseDir = oFSO.GetParentFolderName(WScript.ScriptFullName)
baseDir = oFSO.GetParentFolderName(baseDir)
cfgPath = baseDir & "\config\settings.cfg"

Dim menu
menu = "+================================================+" & vbCrLf & _
       "|       SELECT OPTIMIZATION PRESET             |" & vbCrLf & _
       "+================================================+" & vbCrLf & vbCrLf & _
       "1  TOURNAMENT  - Competitive / Ranked" & vbCrLf & _
       "   All optimizations ON, HAGS: OFF" & vbCrLf & _
       "   DNS: Cloudflare, Max FPS, min ping" & vbCrLf & _
       "   Best for: ranked matches, tournaments" & vbCrLf & vbCrLf & _
       "2  PERFORMANCE  - High FPS + Stability" & vbCrLf & _
       "   All tweaks ON, HAGS: ON (for RTX 30xx+)" & vbCrLf & _
       "   Balanced FPS and system stability" & vbCrLf & vbCrLf & _
       "3  BALANCED    - Casual Play" & vbCrLf & _
       "   Core tweaks only, no aggressive settings" & vbCrLf & _
       "   Good FPS without touching INI files" & vbCrLf & vbCrLf & _
       "4  STREAMING   - For Streamers" & vbCrLf & _
       "   Optimized for streaming Fortnite" & vbCrLf & _
       "   Game DVR: ON, keeps OBS running" & vbCrLf & vbCrLf & _
       "0  CUSTOM      - Return to manual settings" & vbCrLf & vbCrLf & _
       "Enter preset number:"

Dim choice
choice = InputBox(menu, "Fortnite Optimizer - Presets", "2")

If IsNull(choice) Or choice = "" Or choice = "0" Then
    MsgBox "Preset unchanged. Using your current settings.", 64, "Cancelled"
    WScript.Quit
End If

Dim presetName, presetDesc
Select Case choice
    Case "1"
        presetName = "TOURNAMENT"
        presetDesc = "TOURNAMENT - Competitive mode"
    Case "2"
        presetName = "PERFORMANCE"
        presetDesc = "PERFORMANCE - High FPS + Stability"
    Case "3"
        presetName = "BALANCED"
        presetDesc = "BALANCED - Casual play"
    Case "4"
        presetName = "STREAMING"
        presetDesc = "STREAMING - For streamers"
    Case Else
        MsgBox "Invalid choice. Enter a number from 0 to 4.", 48, "Error"
        WScript.Quit
End Select

Dim confirm
confirm = MsgBox("Apply preset?" & vbCrLf & vbCrLf & presetDesc & vbCrLf & vbCrLf & _
    "Your current settings will be replaced.", 36, "Confirm")

If confirm <> 6 Then
    MsgBox "Cancelled.", 64, "Cancelled"
    WScript.Quit
End If

Dim presetsScript
presetsScript = baseDir & "\core\presets.bat"

If oFSO.FileExists(presetsScript) Then
    oShell.Run """" & presetsScript & """ " & presetName, 1, True
    MsgBox "Preset " & presetName & " applied!" & vbCrLf & vbCrLf & _
        "Run LAUNCH_OPTIMIZER.bat to apply optimization.", 64, "Done"
Else
    MsgBox "Error: core\presets.bat not found!", 16, "Error"
End If
