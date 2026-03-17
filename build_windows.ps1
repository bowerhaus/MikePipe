Write-Host "Building MikePipe Sender for Windows..."
python -m PyInstaller --noconfirm --onefile --noconsole --name MikePipeSender --icon=assets\icon.ico --add-data "assets;assets" tray_sender.py

Write-Host ""
Write-Host "Creating shortcut on Desktop..."
$desktop = [Environment]::GetFolderPath("Desktop")
$exe = Join-Path $PSScriptRoot "dist\MikePipeSender.exe"
$shortcut = Join-Path $desktop "MikePipeSender.lnk"

$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($shortcut)
$s.TargetPath = $exe
$s.Save()

Write-Host "Done. Shortcut placed on Desktop."
