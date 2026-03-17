# Plan: MikePipe Option C — Tray/Menu Bar Apps + PyInstaller

**GitHub Issue**: [#2](https://github.com/bowerhaus/MikePipe/issues/2)

## Context
MikePipe's core streaming (sender.py + receiver.py) works well. The goal is to make it easy to install and use daily: a standalone app with a system tray icon (Windows) and menu bar icon (Mac), packaged as a single executable per platform. The sender will read the Mac's Tailscale IP and mic device from a config file (`mikepipe.ini`).

## Decisions

- **Config location**: Standard OS paths — `%APPDATA%\MikePipe\mikepipe.ini` (Windows), `~/Library/Application Support/MikePipe/mikepipe.ini` (Mac)
- **Config scope**: Sender only — host, port, and mic device index. Receiver auto-detects BlackHole (no config needed).
- **Config created automatically** on first launch with commented template.

## Implementation Steps

### Step 1: Refactor sender.py and receiver.py into importable modules
- Extract core logic from `main()` into reusable functions/classes
- `sender.py`: Create a `Sender` class with `start()`, `stop()`, `is_streaming` state, and the hotkey listener
- `receiver.py`: Create a `Receiver` class with `start()`, `stop()`, `is_receiving` state
- Keep the existing `if __name__ == "__main__"` CLI entry points working (backward compatible)

**Files:** `sender.py`, `receiver.py`

### Step 2: Add config file support for sender
- Create `config.py` helper module with `get_config_dir()` and `load_config()`
- Config location: `%APPDATA%\MikePipe\` (Windows), `~/Library/Application Support/MikePipe/` (Mac)
- If config file missing, create it with a commented template and print instructions
- Format: INI with `[sender]` section

**Files:** `config.py` (new)

### Step 3: Create Windows system tray app (`tray_sender.py`)
- Use `pystray` for the system tray icon
- Generate icon programmatically with `Pillow` (green circle = streaming, grey = stopped)
- Menu items: status label (disabled), separator, "Open Config...", "Quit"
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
- **Windows:** `build_windows.bat` — runs `pyinstaller --onefile --noconsole tray_sender.py`
- **Mac:** `build_mac.sh` — runs `pyinstaller --onefile --windowed menubar_receiver.py`
- Create PyInstaller spec files if needed for data file bundling
- `sounddevice` hooks handle PortAudio automatically on both platforms
- Note: Mac build must be done on the Mac itself

**Files:** `build_windows.bat` (new), `build_mac.sh` (new)

### Step 6: Update requirements.txt with platform-specific deps
Split into platform-specific files:
- `requirements.txt` — shared deps (`sounddevice`, `numpy`)
- `requirements-windows.txt` — sender deps (`pynput`, `pystray`, `Pillow`)
- `requirements-mac.txt` — receiver deps (`rumps`)

**Files:** `requirements.txt`, `requirements-windows.txt` (new), `requirements-mac.txt` (new)

### Step 7: Update README.md and CLAUDE.md
- Document the tray/menu bar apps
- Document the config file location and format
- Document the build process

**Files:** `README.md`, `CLAUDE.md`

## Config File

**Location:**
- Windows: `%APPDATA%\MikePipe\mikepipe.ini`
- Mac: `~/Library/Application Support/MikePipe/mikepipe.ini`

**Format (sender only):**
```ini
[sender]
# Mac receiver Tailscale IP address
host = 100.64.1.23

# UDP port (default: 12345)
port = 12345

# Mic input device index (leave blank for system default)
# Run "python sender.py --list-devices" to see available devices
device =
```

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
2. **Config file:** Delete config, run sender — should create template at the standard OS location. Edit IP, restart — should connect.
3. **PyInstaller builds:** Run build scripts, test the resulting executables on both platforms.
4. **End-to-end:** Windows .exe streaming to Mac .app, verify dictation works.
