' ============================================================
'  notify.vbs  -  Fortnite Optimizer
'  Simple notification dialog
' ============================================================
Option Explicit

Dim msg, title, icon
msg   = WScript.Arguments.Named("msg")
title = WScript.Arguments.Named("title")
icon  = WScript.Arguments.Named("icon")

If msg = "" Then msg = "Optimization complete!"
If title = "" Then title = "Fortnite Optimizer"
If icon = "" Then icon = "64"

MsgBox msg, CInt(icon), title
