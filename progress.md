# Progress: 002 - Tray/Menu Bar Apps + PyInstaller [COMPLETE]

## Plan
See [plans/002-tray-menubar-pyinstaller.md](plans/002-tray-menubar-pyinstaller.md)

## Branch
`tray-menubar-pyinstaller` (based off `main`)

## GitHub Issue
[#2](https://github.com/bowerhaus/MikePipe/issues/2)

## Status: COMPLETE

## Steps
- [x] Step 1: Refactor sender.py and receiver.py into importable modules
- [x] Step 2: Add config file support (`config.py`) with standard OS paths
- [x] Step 3: Create Windows system tray app (`tray_sender.py`) using `pystray`
- [x] Step 4: Create Mac menu bar app (`menubar_receiver.py`) using `rumps`
- [x] Step 5: PyInstaller build scripts for both platforms
- [x] Step 6: Update requirements.txt (split into platform-specific files)
- [x] Step 7: Update README.md and CLAUDE.md

## Key Decisions
- Config location: `%APPDATA%\MikePipe\mikepipe.ini` (Windows), `~/Library/Application Support/MikePipe/mikepipe.ini` (Mac)
- Config scope: Sender only — host, port, mic device index. Receiver auto-detects BlackHole.
- Config auto-created on first launch with commented template
- pystray + pynput do NOT conflict (same author, different Win32 subsystems)
- rumps handles NSApplication run loop; UDP receiver in daemon thread
- Mac build must be done on the Mac itself

## Testing Performed
- Windows .exe build tested successfully via `build_windows.bat` → `dist\MikePipeSender.exe`
- Mac build tested via `build_mac.sh` — PyInstaller completes, .app bundle created
- Config file auto-created at `%APPDATA%\MikePipe\mikepipe.ini` on Windows
- End-to-end: Windows sender streaming to Mac receiver, menu bar status indicator works
- Mac menu bar app shows red circle when receiving, white circle when idle

## Post-Implementation Fixes
- Fixed build scripts to use `python -m PyInstaller` instead of `pyinstaller` (not on PATH)
- Mac build: switched from `--onefile` to `--onedir` (PyInstaller deprecation — onefile + .app bundle clash with macOS security)
- Mac build: desktop symlink now points to `.app` bundle instead of raw binary (fixes Terminal window appearing on launch)
- Added `.DS_Store` to `.gitignore`
- Reduced `SILENCE_TIMEOUT` from 2.0s to 0.5s for faster menu bar status updates when sender stops
