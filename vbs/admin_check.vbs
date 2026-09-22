' ============================================================
'  admin_check.vbs  -  Fortnite Optimizer
'  Проверяет права администратора и перезапускает с UAC если нужно
' ============================================================
Set oShell = CreateObject("Shell.Application")
Set oFSO   = CreateObject("Scripting.FileSystemObject")

' Получаем путь к батнику, который надо поднять (передаётся как аргумент)
Dim targetBat
targetBat = WScript.Arguments(0)

' Проверяем, являемся ли уже администратором через попытку открыть системный файл
Dim isAdmin
isAdmin = False
On Error Resume Next
Dim oFile
Set oFile = oFSO.OpenTextFile("\\.\pipe\lsass", 8)
If Err.Number = 0 Then
    isAdmin = True
    oFile.Close
End If
On Error GoTo 0

If Not isAdmin Then
    ' Перезапускаем с правами администратора
    oShell.ShellExecute "cmd.exe", "/c """ & targetBat & """", "", "runas", 1
    WScript.Quit
End If
