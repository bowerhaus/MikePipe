# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MikePipe streams microphone audio from a Windows laptop to a Mac desktop over Tailscale, enabling Mac dictation to use the Windows mic. Audio is piped into BlackHole (virtual audio driver, pre-installed on the Mac).

## Architecture

```
[Windows]  tray_sender.py  --UDP-->  menubar_receiver.py  [Mac]  -->  BlackHole  -->  Mac Dictation
```

- **sender.py**: Core `Sender` class — captures mic via `sounddevice`, streams raw PCM over UDP. Double-tap Right Ctrl starts streaming, single tap stops.
- **receiver.py**: Core `Receiver` class — listens on UDP port 12345, plays received audio to BlackHole via `sounddevice`.
- **tray_sender.py** (Windows): System tray UI using `pystray` + `Pillow`. Wraps `Sender`.
- **menubar_receiver.py** (Mac): Menu bar UI using `rumps`. Wraps `Receiver`.
- **config.py**: Reads sender settings from `mikepipe.ini` (host, port, device).
- Audio format: 16kHz, 16-bit signed int, mono PCM (~32 KB/s).
- Frame size: 20ms (640 bytes) for low latency.

## Setup & Run

```bash
# Windows
pip install -r requirements-windows.txt
python tray_sender.py

# Mac
pip3 install -r requirements-mac.txt
python3 menubar_receiver.py
```

CLI mode (no tray/menubar):
```bash
python sender.py <mac-tailscale-ip>   # Windows
python3 receiver.py                    # Mac
```

## Config File

Sender config: `%APPDATA%\MikePipe\mikepipe.ini` (Windows) or `~/Library/Application Support/MikePipe/mikepipe.ini` (Mac). Auto-created on first launch.

## Key Constraints

- **Latency is critical.** FFmpeg/FFplay was tested and had ~10 seconds of latency to BlackHole — unusable. Use `sounddevice` with small callback-driven buffers (20ms frames). Total latency target: <100ms.
- Network: Tailscale (encrypted, stable IPs, no NAT). No need for additional encryption.
- Hotkey: Double-tap Right Ctrl within 400ms starts streaming, single tap stops. Uses `pynput` on Windows.
