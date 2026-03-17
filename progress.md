# Progress: 001 - Windows Mic to Mac Audio Pipe

## Plan
See [plans/001-windows-mic-to-mac-audio-pipe.md](plans/001-windows-mic-to-mac-audio-pipe.md)

## Branch
`windows-mic-to-mac-audio-pipe` (based off `main`)

## Status: COMPLETE

## Steps
- [x] Step 1: Create `requirements.txt`
- [x] Step 2: Create `sender.py` (Windows — mic capture + hotkey + UDP send)
- [x] Step 3: Create `receiver.py` (Mac — UDP receive + BlackHole playback)
- [x] Step 4: Create `README.md`
- [x] Step 5: Package as desktop-launchable apps — moved to [Plan 002](plans/002-tray-menubar-pyinstaller.md)
- [x] Testing & verification — tested on real hardware (see below)
- [x] Additional: MIT license, .gitattributes for cross-platform line endings

## Testing Performed
- Receiver launched on Mac (`python3 receiver.py`) — auto-detected BlackHole, listening on UDP 12345
- Sender launched on Windows (`python sender.py <mac-tailscale-ip>`) — connected successfully
- Hotkey: double-tap Right Ctrl starts streaming, single tap stops — confirmed working
- Audio received on Mac and played to BlackHole — verified with Mac dictation
- Hotkey changed from AltGr to Right Ctrl to align with Mac dictation shortcut via Jump Desktop
