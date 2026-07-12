@echo off
rem Stops the background DevPresence process (only this one, not other Python apps).
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe'\" | Where-Object { $_.CommandLine -like '*devpresence.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
echo DevPresence stopped.
