# MikePipe: Windows Mic → Mac Audio Pipe — COMPLETED

**GitHub Issue**: [#1](https://github.com/bowerhaus/MikePipe/issues/1)
**Status**: Complete (Steps 1-4 implemented and tested; Step 5 moved to [Plan 002](002-tray-menubar-pyinstaller.md))

## Context
The user remotes into a Mac desktop from a Windows laptop via Jump Desktop. Jump Desktop doesn't forward microphone audio, so Mac dictation can't use the Windows mic. We need a separate audio pipe with hotkey activation.

**Environment**:
- Network: Tailscale (encrypted tunnel, stable IPs, no NAT issues)
- Mac: BlackHole already installed, full admin access
- UI: Console output on Windows (no tray icon needed)
- Hotkey: Double-tap AltGr (Right Alt) to toggle streaming

## Chosen Approach: Python Client-Server + BlackHole

```
[Windows Laptop]                      [Mac Desktop]
┌──────────────────┐    UDP/Tailscale   ┌──────────────────┐
│ sender.py        │──────────────────→│ receiver.py       │
│ - Mic capture    │    port 12345      │ - Receives audio  │
│ - Double-tap     │                    │ - Plays to        │
│   AltGr toggle   │                    │   BlackHole       │
│ - Console status │                    │ - Console status  │
└──────────────────┘                    └──────────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ Mac Dictation │
                                        │ (input set to │
                                        │  BlackHole)   │
                                        └──────────────┘
```

## Implementation Plan

### Step 1: Create `requirements.txt`
```
sounddevice
numpy
pynput
```
- `sounddevice` — cross-platform audio capture/playback (uses PortAudio under the hood)
- `numpy` — required by sounddevice for audio buffers
- `pynput` — keyboard listener for AltGr double-tap detection on Windows

### Step 2: Create `sender.py` (Windows side)
**Responsibilities**:
1. List available audio input devices and select the default mic (or allow override via CLI arg)
2. Listen for AltGr double-tap (two presses within 400ms) using `pynput`
3. When activated: open a UDP socket and start streaming mic audio
4. Audio format: 16kHz sample rate, 16-bit signed integer, mono — optimal for speech recognition
5. Send audio in chunks (~20ms frames = 640 bytes per frame)
6. Print clear status messages: "STREAMING" / "STOPPED"
7. When deactivated (another double-tap): stop streaming, close audio stream

**Key design decisions**:
- UDP not TCP — lower latency, no head-of-line blocking. Dropped packets just mean a tiny audio glitch, which is fine for dictation
- Small frame size (20ms) for low latency
- No compression — raw PCM. On Tailscale the bandwidth is ~32 KB/s for 16kHz/16-bit/mono, which is nothing
- Mac IP address provided as a CLI argument: `python sender.py <mac-tailscale-ip>`

### Step 3: Create `receiver.py` (Mac side)
**Responsibilities**:
1. List audio output devices and find BlackHole (or allow override via CLI arg `--device`)
2. Open a UDP socket listening on port 12345
3. Receive audio chunks and play them to the BlackHole device via `sounddevice`
4. Handle sender start/stop gracefully (detect silence/no-data, don't crash)
5. Print status: "Receiving audio..." / "Sender disconnected"

**Key design decisions**:
- Use a small playback buffer to minimize latency while avoiding underruns
- The receiver runs continuously — it's always listening. The sender controls when audio flows.
- Simple protocol: just raw PCM bytes over UDP. A 4-byte header with sequence number for ordering (optional — can add if we see issues)

### Step 4: Create `README.md`
- Setup instructions for both machines
- How to find Mac's Tailscale IP
- How to configure Mac dictation to use BlackHole as input
- Usage: start receiver on Mac, start sender on Windows, double-tap AltGr to stream

### Step 5: Package as desktop-launchable apps
- **Windows**: Use PyInstaller to bundle `sender.py` into a `.exe` with custom icon
- **Mac**: Use PyInstaller to bundle `receiver.py` into a `.app` with custom icon
- Add `pyinstaller` to dev dependencies
- Create `build_windows.bat` and `build_mac.sh` scripts
- Note: Mac `.app` must be built on the Mac itself

## Files to create
| File | Machine | Purpose |
|------|---------|---------|
| `sender.py` | Windows | Mic capture + hotkey + UDP send |
| `receiver.py` | Mac | UDP receive + BlackHole playback |
| `requirements.txt` | Both | Python dependencies |
| `README.md` | — | Setup & usage instructions |
| `sender.spec` | Windows | PyInstaller spec for sender .exe |
| `receiver.spec` | Mac | PyInstaller spec for receiver .app |

## Important: Latency Constraint
A previous attempt using FFmpeg/FFplay to stream to BlackHole had ~10 seconds of latency — completely unusable for dictation. This was caused by FFmpeg's large default input/output buffers. The Python `sounddevice` approach avoids this by using small callback-driven audio frames (20ms) with minimal buffering. This is a hard requirement — the pipe must feel near-real-time.

## Technical Notes

### AltGr Double-Tap Detection
- `pynput` sees AltGr as `Key.alt_gr` on Windows
- Track timestamps of AltGr key presses; if two presses within 400ms → toggle
- Need to be careful: AltGr sometimes generates both Ctrl+Alt events on some keyboards — will handle this in the key listener

### BlackHole Configuration on Mac
- Set Mac System Preferences → Sound → Input to "BlackHole" for dictation
- Or in dictation settings specifically select BlackHole as the input device
- The receiver plays audio *to* BlackHole's output channels, which appear as BlackHole's input to other apps

### Latency Budget
- Mic capture buffer: ~20ms
- Network (Tailscale LAN): ~1-5ms
- Playback buffer: ~20-40ms
- **Total expected: ~40-65ms** — well under what's noticeable for dictation

## Verification / Testing
1. On Mac: `python receiver.py` — should print available devices and show BlackHole, then listen
2. On Windows: `python sender.py <mac-ip>` — should show "Ready. Double-tap AltGr to start streaming"
3. Double-tap AltGr → console shows "STREAMING"
4. On Mac: open System Preferences → Sound → Input → select BlackHole → verify the level meter moves when you speak
5. Open dictation, verify it transcribes speech from the Windows mic
6. Double-tap AltGr again → "STOPPED", dictation should stop receiving audio
