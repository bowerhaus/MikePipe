# Progress: 002 - Tray/Menu Bar Apps + PyInstaller

## Plan
See [plans/002-tray-menubar-pyinstaller.md](plans/002-tray-menubar-pyinstaller.md)

## Branch
`tray-menubar-pyinstaller` (based off `windows-mic-to-mac-audio-pipe`)

## GitHub Issue
[#2](https://github.com/bowerhaus/MikePipe/issues/2)

## Status: All steps complete — Windows build tested, Mac build not yet tested

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

## Step 4 Notes
- `menubar_receiver.py`: uses `rumps` for Mac menu bar
- Title: "MikePipe" (idle) / red circle + "MikePipe" (receiving)
- Menu: status label ("Waiting for sender..." / "Receiving from x.x.x.x"), "Quit"
- Receiver runs in daemon thread via `Receiver.start()`, rumps on main thread
- Auto-detects BlackHole device via Receiver class

## Step 3 Notes
- `tray_sender.py`: uses `pystray` + `Pillow` for system tray icon
- Green circle = streaming, grey circle = stopped
- Menu: "MikePipe Sender" (disabled label), separator, "Open Config...", "Quit"
- Tooltip updates: "MikePipe — Streaming" / "MikePipe — Stopped"
- pystray runs on main thread, sender + hotkey on daemon thread
- Reads config via `load_config()` from config.py

## Step 2 Notes
- `config.py`: `get_config_dir()`, `get_config_path()`, `ensure_config()`, `load_config()`
- `load_config()` returns `(host, port, device)` — device is None if not set
- Auto-creates config with commented template on first run
- Exits with helpful message if host not configured
- Windows: `%APPDATA%\MikePipe\mikepipe.ini`, Mac: `~/Library/Application Support/MikePipe/mikepipe.ini`

## Step 1 Notes
- `Sender` class: `__init__(host, port, device, on_state_change)`, `start()`, `stop()`, `is_streaming`, `start_streaming()`, `stop_streaming()`, `start_hotkey_listener()`
- `Receiver` class: `__init__(device, port, on_state_change)`, `start()`, `stop()`, `is_receiving`
- `on_state_change` callback allows tray/menubar apps to react to state changes
- Receiver runs its receive loop in a daemon thread (via `start()`), making it easy to integrate with `rumps`
- Both CLI entry points (`if __name__ == "__main__"`) still work identically to before

## Post-Implementation Notes
- Fixed build scripts to use `python -m PyInstaller` instead of `pyinstaller` (not on PATH)
- Windows .exe build tested successfully via `build_windows.bat` → `dist\MikePipeSender.exe`
- Config file auto-created at `%APPDATA%\MikePipe\mikepipe.ini` — user has opened and seen it
- Nothing committed yet — user is staging manually
- No changes have been committed to the branch yet

## What's Left
- Test `python tray_sender.py` end-to-end (Windows tray → Mac receiver → dictation)
- Test Mac build on Mac (`build_mac.sh`)
- Test CLI backward compatibility (`python sender.py <ip>`)
- Stage, commit, and create PR to close #2

## Context for Resume
- All 7 implementation steps are complete, code is written but uncommitted
- Files created: `config.py`, `tray_sender.py`, `menubar_receiver.py`, `build_windows.bat`, `build_mac.sh`, `requirements-windows.txt`, `requirements-mac.txt`
- Files modified: `sender.py` (Sender class), `receiver.py` (Receiver class), `requirements.txt` (shared only), `README.md`, `CLAUDE.md`
- User stages changes manually — do not auto-stage
