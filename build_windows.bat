@echo off
echo Building MikePipe Sender for Windows...
python -m PyInstaller --onefile --noconsole --name MikePipeSender tray_sender.py
echo.
echo Done. Output: dist\MikePipeSender.exe
pause
