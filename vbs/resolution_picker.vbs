' ============================================================
'  resolution_picker.vbs  -  Fortnite Optimizer
'  Display resolution selector (native + competitive)
' ============================================================
Option Explicit

Dim oShell, oFSO, baseDir, cfgPath
Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")

baseDir = oFSO.GetParentFolderName(WScript.ScriptFullName)
baseDir = oFSO.GetParentFolderName(baseDir)
cfgPath = baseDir & "\config\settings.cfg"

' --- Read current resolution settings ---
Dim curW, curH, curR, curEnabled
curW = "1920" : curH = "1080" : curR = "0" : curEnabled = "0"

If oFSO.FileExists(cfgPath) Then
    Dim oF, ln, p
    Set oF = oFSO.OpenTextFile(cfgPath, 1)
    Do While Not oF.AtEndOfStream
        ln = Trim(oF.ReadLine())
        If Left(ln,1) <> "#" And InStr(ln,"=") > 0 Then
            p = Split(ln,"=",2)
            Select Case Trim(p(0))
                Case "RESOLUTION_WIDTH"   : curW = Trim(p(1))
                Case "RESOLUTION_HEIGHT"  : curH = Trim(p(1))
                Case "RESOLUTION_REFRESH" : curR = Trim(p(1))
                Case "RESOLUTION_CHANGE"  : curEnabled = Trim(p(1))
            End Select
        End If
    Loop
    oF.Close
End If

' --- Resolution menu ---
Dim menu
menu = "+================================================+" & vbCrLf & _
       "|       CHANGE DISPLAY RESOLUTION              |" & vbCrLf & _
       "+================================================+" & vbCrLf & vbCrLf & _
       "Current: " & curW & "x" & curH & "  [change " & IIf(curEnabled="1","ON","OFF") & "]" & vbCrLf & vbCrLf & _
       "--- NATIVE ----------------------------------" & vbCrLf & _
       "1  1920 x 1080  (Full HD - standard)" & vbCrLf & _
       "2  2560 x 1440  (2K / QHD)" & vbCrLf & _
       "3  3840 x 2160  (4K - high-end PCs only)" & vbCrLf & _
       "4  1280 x 720   (HD - more FPS)" & vbCrLf & vbCrLf & _
       "--- COMPETITIVE STRETCHED -------------------" & vbCrLf & _
       "5  1440 x 1080  (4:3 stretched - top pros)" & vbCrLf & _
       "6  1280 x 1024  (5:4 stretched)" & vbCrLf & _
       "7  1600 x 1080  (wide stretched)" & vbCrLf & _
       "8  1920 x 1440  (4:3 stretched 1440p)" & vbCrLf & vbCrLf & _
       "--- LOW (MAX FPS) ---------------------------" & vbCrLf & _
       "9  1024 x 768   (4:3 very high FPS)" & vbCrLf & _
       "10 800 x 600    (extreme FPS)" & vbCrLf & vbCrLf & _
       "0  OFF - do not change resolution" & vbCrLf & _
       "C  Custom resolution (enter WIDTHxHEIGHT)" & vbCrLf & vbCrLf & _
       "Enter number:"

Dim choice
choice = InputBox(menu, "Fortnite Optimizer - Resolution", "1")

If IsNull(choice) Or choice = "" Then WScript.Quit

Dim newW, newH, newEnabled
newEnabled = "1"

Select Case UCase(Trim(choice))
    Case "0"    : newEnabled = "0" : newW = curW : newH = curH
    Case "1"    : newW = "1920" : newH = "1080"
    Case "2"    : newW = "2560" : newH = "1440"
    Case "3"    : newW = "3840" : newH = "2160"
    Case "4"    : newW = "1280" : newH = "720"
    Case "5"    : newW = "1440" : newH = "1080"
    Case "6"    : newW = "1280" : newH = "1024"
    Case "7"    : newW = "1600" : newH = "1080"
    Case "8"    : newW = "1920" : newH = "1440"
    Case "9"    : newW = "1024" : newH = "768"
    Case "10"   : newW = "800"  : newH = "600"
    Case "C"
        Dim custom
        custom = InputBox("Enter resolution in format WIDTHxHEIGHT" & vbCrLf & _
            "Examples: 1920x1080  /  1440x1080  /  2560x1440", "Custom Resolution", "1920x1080")
        If IsNull(custom) Or custom = "" Then WScript.Quit
        Dim pts
        pts = Split(custom, "x", 2)
        If UBound(pts) < 1 Then
            MsgBox "Invalid format! Use WIDTHxHEIGHT (e.g. 1920x1080)", 16, "Error"
            WScript.Quit
        End If
        newW = Trim(pts(0))
        newH = Trim(pts(1))
    Case Else
        MsgBox "Invalid choice!", 16, "Error"
        WScript.Quit
End Select

' --- Ask for refresh rate ---
Dim newR
If newEnabled = "1" Then
    newR = InputBox("Refresh rate (Hz):" & vbCrLf & vbCrLf & _
        "Enter 0 to keep current refresh rate" & vbCrLf & _
        "Common: 60, 75, 144, 165, 240", "Refresh Rate", "0")
    If IsNull(newR) Or newR = "" Then newR = "0"
Else
    newR = curR
End If

' --- Update config ---
If Not oFSO.FileExists(cfgPath) Then
    MsgBox "Settings file not found! Open SETTINGS.bat first.", 16, "Error"
    WScript.Quit
End If

Dim oFileR
Set oFileR = oFSO.OpenTextFile(cfgPath, 1)
Dim content
content = oFileR.ReadAll()
oFileR.Close

content = UpdateCfg(content, "RESOLUTION_CHANGE", newEnabled)
content = UpdateCfg(content, "RESOLUTION_WIDTH", newW)
content = UpdateCfg(content, "RESOLUTION_HEIGHT", newH)
content = UpdateCfg(content, "RESOLUTION_REFRESH", newR)

Dim oFileW
Set oFileW = oFSO.CreateTextFile(cfgPath, True)
oFileW.Write content
oFileW.Close

' --- Confirmation ---
If newEnabled = "1" Then
    Dim msg
    msg = "Resolution set:" & vbCrLf & vbCrLf & _
        "  Width:   " & newW & " px" & vbCrLf & _
        "  Height:  " & newH & " px" & vbCrLf & _
        "  Refresh: " & IIf(newR="0","no change",newR & " Hz") & vbCrLf & vbCrLf & _
        "Will apply on next LAUNCH_OPTIMIZER.bat run."

    Dim applyNow
    applyNow = MsgBox(msg & vbCrLf & vbCrLf & "Apply resolution RIGHT NOW?", 36, "Resolution")
    If applyNow = 6 Then
        Dim resScript
        resScript = baseDir & "\core\resolution.bat"
        If oFSO.FileExists(resScript) Then
            oShell.Run """" & resScript & """ " & newW & " " & newH & " " & newR, 1, True
        End If
    End If
Else
    MsgBox "Resolution change DISABLED." & vbCrLf & _
        "Resolution will not change on launch.", 64, "Done"
End If

' --- Helper functions ---
Function UpdateCfg(txt, key, val)
    Dim lines, i, updated
    lines = Split(txt, vbCrLf)
    updated = False
    For i = 0 To UBound(lines)
        If Left(Trim(lines(i)),1) <> "#" And InStr(lines(i), key & "=") = 1 Then
            lines(i) = key & "=" & val
            updated = True
        End If
    Next
    If Not updated Then
        ReDim Preserve lines(UBound(lines)+1)
        lines(UBound(lines)) = key & "=" & val
    End If
    UpdateCfg = Join(lines, vbCrLf)
End Function

Function IIf(cond, t, f)
    If cond Then IIf = t Else IIf = f
End Function
