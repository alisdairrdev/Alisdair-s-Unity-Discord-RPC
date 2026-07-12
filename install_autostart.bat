@echo off
rem Enables auto-start: DevPresence will launch quietly every time you log in.
setlocal
for /f "delims=" %%i in ('python -c "import sys,os;print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"') do set "PYW=%%i"
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Startup')+'\DevPresence.lnk'); $s.TargetPath='%PYW%'; $s.Arguments='\"%~dp0devpresence.py\"'; $s.WorkingDirectory='%~dp0'; $s.WindowStyle=7; $s.Save()"
echo.
echo Auto-start ENABLED. DevPresence will launch quietly when you log in.
pause
