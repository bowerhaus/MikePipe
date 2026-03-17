# Plan: MikePipe Option C — Tray/Menu Bar Apps + PyInstaller

**GitHub Issue**: [#2](https://github.com/bowerhaus/MikePipe/issues/2)

## Context
MikePipe's core streaming (sender.py + receiver.py) works well. The goal is to make it easy to install and use daily: a standalone app with a system tray icon (Windows) and menu bar icon (Mac), packaged as a single executable per platform. The sender will read the Mac's Tailscale IP from a config file (`mikepipe.ini`).

## Implementation Steps

### Step 1: Refactor sender.py and receiver.py into importable modules
- Extract core logic from `main()` into reusable functions/classes
- `sender.py`: Create a `Sender` class with `start()`, `stop()`, `is_streaming` state, and the hotkey listener
- `receiver.py`: Create a `Receiver` class with `start()`, `stop()`, `is_receiving` state
- Keep the existing `if __name__ == "__main__"` CLI entry points working (backward compatible)

**Files:** `sender.py`, `receiver.py`

### Step 2: Add config file support for sender
- Read `mikepipe.ini` from the same directory as the executable (or script)
- Format: INI with `[sender]` section containing `host` and optional `port`
- If config file missing, create a template and print an error message
- Add a `config.py` helper module

**Files:** `config.py` (new), `mikepipe.ini` (new — template/example)

### Step 3: Create Windows system tray app (`tray_sender.py`)
- Use `pystray` for the system tray icon
- Generate icon programmatically with `Pillow` (green circle = streaming, grey = stopped)
- Menu items: status label (disabled), separator, "Quit"
- Hotkey (Right Ctrl double-tap/single-tap) continues to work via `pynput` in a background thread
- `pystray` runs in the main thread; audio + hotkey in background threads
- Add `pystray` and `Pillow` to requirements

**Files:** `tray_sender.py` (new), `requirements.txt`

### Step 4: Create Mac menu bar app (`menubar_receiver.py`)
- Use `rumps` for the menu bar
- Menu bar title: Unicode mic character or "MikePipe", changes to show state
- Menu items: status label ("Receiving from ..." / "Waiting for sender..."), separator, "Quit"
- UDP receive loop runs in a background thread
- `rumps` runs the NSApplication event loop in the main thread
- Add `rumps` to requirements

**Files:** `menubar_receiver.py` (new), `requirements.txt`

### Step 5: PyInstaller build scripts
- **Windows:** `build_windows.bat` — runs `pyinstaller --onefile --noconsole --icon=icon.ico tray_sender.py`
- **Mac:** `build_mac.sh` — runs `pyinstaller --onefile --windowed --icon=icon.icns menubar_receiver.py`
- Create PyInstaller spec files if needed for data file bundling
- `sounddevice` hooks handle PortAudio automatically on both platforms
- Note: Mac build must be done on the Mac itself

**Files:** `build_windows.bat` (new), `build_mac.sh` (new)

### Step 6: Update requirements.txt with platform-specific deps
```
sounddevice
numpy
pynput          # Windows only (sender)
pystray         # Windows only (tray sender)
Pillow          # Windows only (tray icon generation)
rumps           # Mac only (menu bar receiver)
```
Consider splitting into `requirements-windows.txt` and `requirements-mac.txt`.

**Files:** `requirements.txt` (or split files)

### Step 7: Update README.md and CLAUDE.md
- Document the tray/menu bar apps
- Document the config file
- Document the build process

**Files:** `README.md`, `CLAUDE.md`

## Config File Format
```ini
[sender]
host = 100.64.1.23
port = 12345
```
Placed next to the `.exe` (or in the script directory during development).

## Tray/Menu Bar UI

**Windows system tray (sender):**
- Icon: green dot (streaming) / grey dot (stopped)
- Tooltip: "MikePipe — Streaming" or "MikePipe — Stopped"
- Right-click menu: Status label, separator, "Open Config...", "Quit"

**Mac menu bar (receiver):**
- Title: "🎤" or "MikePipe" — changes style to indicate receiving state
- Menu: Status label, separator, "Quit"

## Key Technical Notes
- `pystray` and `pynput` do NOT conflict (same author, different Win32 subsystems)
- `rumps` handles the NSApplication run loop; UDP receiver runs in a daemon thread
- PyInstaller `--noconsole` (Windows) / `--windowed` (Mac) hides the terminal
- Mac Gatekeeper: unsigned app needs `xattr -cr MikePipe.app` after download

## Verification
1. **Dev testing (no PyInstaller):** Run `python tray_sender.py` on Windows — tray icon appears, hotkey works, status updates. Run `python3 menubar_receiver.py` on Mac — menu bar icon appears, receives audio.
2. **Config file:** Delete `mikepipe.ini`, run sender — should show error/create template. Add IP, restart — should connect.
3. **PyInstaller builds:** Run build scripts, test the resulting executables on clean machines (no Python installed).
4. **End-to-end:** Windows .exe streaming to Mac .app, verify dictation works.
