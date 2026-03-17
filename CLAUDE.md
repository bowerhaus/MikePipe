# CLAUDE.md

## Architecture

```
[Windows]  tray_sender.py  --UDP-->  menubar_receiver.py  [Mac]  -->  BlackHole  -->  Mac Dictation
```

- **sender.py / receiver.py**: Core classes — `sounddevice` for audio capture/playback, raw PCM over UDP.
- **tray_sender.py** (Windows): System tray UI via `pystray` + `Pillow`. Wraps `Sender`.
- **menubar_receiver.py** (Mac): Menu bar UI via `rumps`. Wraps `Receiver`.
- **config.py**: Reads sender settings from `mikepipe.ini`.
- **assets/**: Icon sources (`icon.png`, `icon on.png`) and `generate_icons.py` which produces `.ico`, `.icns`, tray and menubar PNGs (off + on states).

## Dev Setup

```bash
# Windows
pip install -r requirements-windows.txt

# Mac
pip3 install -r requirements-mac.txt
```

## Build

```bash
# Windows
build_windows.bat   # or build_windows.ps1

# Mac
./build_mac.sh
```

PyInstaller bundles assets via `--add-data`. Asset path resolution uses `sys._MEIPASS` with fallback to `__file__` dir.

## Key Constraints

- **Latency target: <100ms.** Use `sounddevice` with 20ms callback-driven frames. Do not use FFmpeg/FFplay (tested, ~10s latency to BlackHole).
- Network: Tailscale (encrypted, stable IPs). No additional encryption needed.
- Audio format: 16kHz, 16-bit signed int, mono, UDP port 12345.
