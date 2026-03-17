# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MikePipe streams microphone audio from a Windows laptop to a Mac desktop over Tailscale, enabling Mac dictation to use the Windows mic. Audio is piped into BlackHole (virtual audio driver, pre-installed on the Mac).

## Architecture

```
[Windows]  sender.py  --UDP-->  receiver.py  [Mac]  -->  BlackHole  -->  Mac Dictation
```

- **sender.py** (Windows): Captures mic via `sounddevice`, streams raw PCM over UDP. Double-tap AltGr toggles streaming on/off.
- **receiver.py** (Mac): Listens on UDP port 12345, plays received audio to the BlackHole device via `sounddevice`.
- Audio format: 16kHz, 16-bit signed int, mono PCM (~32 KB/s).
- Frame size: 20ms (640 bytes) for low latency.

## Setup & Run

```bash
# Both machines
pip install -r requirements.txt

# Mac (start first, runs continuously)
python receiver.py

# Windows
python sender.py <mac-tailscale-ip>
```

## Key Constraints

- **Latency is critical.** FFmpeg/FFplay was tested and had ~10 seconds of latency to BlackHole — unusable. Use `sounddevice` with small callback-driven buffers (20ms frames). Total latency target: <100ms.
- Network: Tailscale (encrypted, stable IPs, no NAT). No need for additional encryption.
- Hotkey: Double-tap AltGr (Right Alt) within 400ms toggles streaming. Uses `pynput` on Windows.
