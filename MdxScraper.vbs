' This script runs a Python script using uv without a visible command window.
' Modern approach using uv's built-in environment management

Set WshShell = CreateObject("WScript.Shell")

' Get the directory where this VBScript is located.
appDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' --- User Configuration ---
entryScript = "MdxScraper.py"
' --------------------------

' Use chr(34) to represent the double-quote character (") for clarity.
q = chr(34)

' Use uv run to automatically manage environment
uvPath = "uv"
cdCmd = "cd /D " & q & appDir & q
uvCmd = uvPath & " run python " & q & entryScript & q

' Command using uv run
fullCommand = cdCmd & " & " & uvCmd

' Create the final command to be executed by cmd.exe, wrapped in quotes.
cmdToRun = "cmd.exe /K " & q & fullCommand & q

' Run the command:
' 0 = The window is hidden.
' True = The script waits for the command to finish.
WshShell.Run cmdToRun, 1, True

'
