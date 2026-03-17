@echo off
echo Building MikePipe Sender for Windows...
python -m PyInstaller --noconfirm --onefile --noconsole --name MikePipeSender --icon=assets\icon.ico --add-data "assets;assets" tray_sender.py
echo.

echo Creating shortcut on Desktop...
set "DESKTOP=%USERPROFILE%\Desktop"
set "EXE=%~dp0dist\MikePipeSender.exe"
set "SHORTCUT=%DESKTOP%\MikePipeSender.lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%EXE%'; $s.Save()"

echo Done. Shortcut placed on Desktop.
pause
