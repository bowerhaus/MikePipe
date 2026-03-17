# MikePipe

MikePipe streams microphone audio from a Windows laptop to a Mac desktop over a local network, enabling Mac dictation to use the Windows mic. This is useful when remoting into a Mac via Jump Desktop (or similar), which doesn't forward microphone audio.

Audio is captured on Windows, sent as raw PCM over UDP via Tailscale, and played into BlackHole (a virtual audio driver on the Mac). Mac dictation then reads from BlackHole as its input device. The result is near-real-time speech-to-text using the Windows mic, with under 100ms of latency.

## How It Works

```
[Windows Laptop]                        [Mac Desktop]
┌──────────────────┐    UDP/Tailscale    ┌──────────────────┐
│ tray_sender.py   │───────────────────→│ menubar_receiver  │
│ - System tray    │    port 12345       │ - Menu bar icon   │
│ - Mic capture    │                     │ - Plays audio to  │
│ - Right Ctrl     │                     │   BlackHole       │
│   hotkey toggle  │                     │                   │
└──────────────────┘                     └──────────────────┘
                                                │
                                                ▼
                                         Mac Dictation
                                         (input: BlackHole)
```

- **Audio format**: 16kHz, 16-bit signed int, mono PCM (~32 KB/s)
- **Frame size**: 20ms (640 bytes) for low latency
- **Transport**: UDP over Tailscale — encrypted, stable IPs, no NAT issues

## Prerequisites

- **Both machines**: Python 3.8+, connected via [Tailscale](https://tailscale.com/)
- **Mac**: [BlackHole](https://existential.audio/blackhole/) virtual audio driver installed

## Setup

### Mac

```bash
pip3 install -r requirements-mac.txt
```

Configure Mac dictation to use BlackHole as its input:
1. System Settings → Keyboard → Dictation → turn on
2. System Settings → Sound → Input → select **BlackHole**

### Windows

```bash
pip install -r requirements-windows.txt
```

## Running

### Desktop Apps (recommended)

**Windows — System Tray Sender:**

On first launch, a config file is created at `%APPDATA%\MikePipe\mikepipe.ini`. Edit it to set your Mac's Tailscale IP address, then restart.

```bash
python tray_sender.py
```

A system tray icon appears (green = streaming, grey = stopped). Right-click for options including "Open Config...".

**Mac — Menu Bar Receiver:**

```bash
python3 menubar_receiver.py
```

A menu bar item shows the connection status. The receiver auto-detects BlackHole.

### CLI Mode

The original command-line scripts still work:

```bash
# Mac (start first)
python3 receiver.py

# Windows
python sender.py <mac-tailscale-ip>
```

Use `--list-devices` on either script to choose a specific audio device.

### Hotkey

- **Double-tap Right Ctrl** to start streaming
- **Single tap Right Ctrl** to stop

## Building Standalone Executables

Requires PyInstaller (included in platform requirements).

**Windows:**
```bash
build_windows.bat
```
Output: `dist\MikePipeSender.exe`

**Mac** (must be run on the Mac itself):
```bash
pip3 install -r requirements-mac.txt
chmod +x build_mac.sh
./build_mac.sh
```
Output: `dist/MikePipeReceiver`

If Gatekeeper blocks the unsigned app, run `xattr -cr dist/MikePipeReceiver.app`.

## Config File

The sender reads settings from `mikepipe.ini`:

- **Windows**: `%APPDATA%\MikePipe\mikepipe.ini`
- **Mac**: `~/Library/Application Support/MikePipe/mikepipe.ini`

```ini
[sender]
# Mac receiver Tailscale IP address (required)
host = 100.64.1.23

# UDP port (default: 12345)
port = 12345

# Mic input device index (leave blank for system default)
device =
```

## Troubleshooting

- **No audio received**: Check that both machines are on Tailscale and can ping each other. Ensure the receiver is running before the sender starts streaming.
- **High latency**: Should be under 100ms with this setup. If not, check for network issues on Tailscale.
- **Wrong mic**: Use `--list-devices` on the sender to pick the correct input device.
- **BlackHole not found**: Ensure BlackHole is installed and restart the receiver. Use `--list-devices` to verify it appears.
- **`python` / `pip` not found on Mac**: Use `python3` and `pip3` instead.

## License

[MIT](LICENSE)
