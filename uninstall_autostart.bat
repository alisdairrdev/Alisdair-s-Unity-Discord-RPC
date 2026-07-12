@echo off
rem Disables auto-start (removes the login shortcut). Does not delete anything else.
powershell -NoProfile -Command "Remove-Item ([Environment]::GetFolderPath('Startup')+'\DevPresence.lnk') -ErrorAction SilentlyContinue"
echo.
echo Auto-start DISABLED. DevPresence will no longer launch at login.
pause
