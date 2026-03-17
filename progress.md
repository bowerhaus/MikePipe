# Progress: 001 - Windows Mic to Mac Audio Pipe

## Plan
See [plans/001-windows-mic-to-mac-audio-pipe.md](plans/001-windows-mic-to-mac-audio-pipe.md)

## Branch
`windows-mic-to-mac-audio-pipe` (based off `main`)

## Status: Steps 1-4 complete, ready for testing

## Steps
- [x] Step 1: Create `requirements.txt`
- [x] Step 2: Create `sender.py` (Windows — mic capture + hotkey + UDP send)
- [x] Step 3: Create `receiver.py` (Mac — UDP receive + BlackHole playback)
- [x] Step 4: Create `README.md`
- [ ] Step 5: Package as desktop-launchable apps (PyInstaller)
- [ ] Testing & verification

## Context for Resume
- Project streams Windows mic audio to Mac over Tailscale for dictation use
- Uses Python `sounddevice` library with small 20ms frames for low latency
- BlackHole already installed on Mac
- Hotkey: double-tap AltGr to toggle streaming
- Audio format: 16kHz, 16-bit, mono PCM over UDP port 12345
- FFmpeg was tried before and had ~10s latency — must avoid large buffers
- Steps 1-4 implemented: requirements.txt, sender.py, receiver.py, README.md all created
- Step 5 (PyInstaller packaging) and testing still pending
- Need to test on actual hardware: run receiver.py on Mac, sender.py on Windows
