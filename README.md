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

## Quick Start (Pre-built Releases)

If you don't want to install Python or build from source, download the pre-built executables from the [GitHub Releases](https://github.com/bowerhaus/MikePipe/releases) page:

- **Windows**: Download `MikePipeSender.exe`
- **Mac**: Download `MikePipeReceiver.app`

See the platform-specific instructions below for prerequisites and first-run setup.

## Prerequisites

### Windows

- Connected to [Tailscale](https://tailscale.com/)
- No additional software required if using the pre-built release

### Mac

- Connected to [Tailscale](https://tailscale.com/)
- [BlackHole](https://existential.audio/blackhole/) virtual audio driver installed
- Configure Mac dictation to use BlackHole as its input:
  1. System Settings → Keyboard → Dictation → turn on
  2. System Settings → Sound → Input → select **BlackHole**

## Installation

### Option 1: Pre-built Releases (Recommended)

1. Go to [Releases](https://github.com/bowerhaus/MikePipe/releases) and download the latest version for your platform.
2. **Windows**: Place `MikePipeSender.exe` anywhere convenient (e.g. Desktop). Double-click to run.
3. **Mac**: Move `MikePipeReceiver.app` to your Applications folder or Desktop. If macOS Gatekeeper blocks the app, right-click → Open, or run:
   ```bash
   xattr -cr /path/to/MikePipeReceiver.app
   ```

### Option 2: Run from Source

Requires Python 3.8+ on both machines.

**Windows:**
```bash
git clone https://github.com/bowerhaus/MikePipe.git
cd MikePipe
pip install -r requirements-windows.txt
python tray_sender.py
```

**Mac:**
```bash
git clone https://github.com/bowerhaus/MikePipe.git
cd MikePipe
pip3 install -r requirements-mac.txt
python3 menubar_receiver.py
```

### Option 3: Build from Source

Build standalone executables yourself using PyInstaller.

**Windows:**
```bash
build_windows.bat
```
Output: `dist\MikePipeSender.exe` with a desktop shortcut.

**Mac** (must be run on the Mac itself):
```bash
chmod +x build_mac.sh
./build_mac.sh
```
Output: `dist/MikePipeReceiver.app` with a desktop alias.

## Usage

### Windows Sender

1. **Launch** `MikePipeSender.exe` (or `python tray_sender.py` from source).
2. **First run**: A config file is created automatically. Right-click the system tray icon → **Open Config...** to set your Mac's Tailscale IP address, then restart the app.
3. **Start streaming**: Double-tap **Right Ctrl**.
4. **Stop streaming**: Single tap **Right Ctrl**.
5. The tray icon changes to show streaming status — a microphone icon with a red dot when active.

### Mac Receiver

1. **Launch** `MikePipeReceiver.app` (or `python3 menubar_receiver.py` from source).
2. A microphone icon appears in the menu bar. It changes to show a red indicator when audio is being received.
3. The receiver auto-detects BlackHole as its output device. Audio received from the Windows sender is played into BlackHole, where Mac dictation picks it up.
4. Click the menu bar icon for status info, or to quit.

### CLI Mode

The original command-line scripts are also available for advanced use or debugging:

```bash
# Mac (start first)
python3 receiver.py

# Windows
python sender.py <mac-tailscale-ip>
```

Use `--list-devices` on either script to choose a specific audio device.

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
- **Wrong mic**: Use `--list-devices` on the sender to pick the correct input device, then set it in the config file.
- **BlackHole not found**: Ensure BlackHole is installed and restart the receiver. Use `--list-devices` to verify it appears.
- **Mac app blocked by Gatekeeper**: Right-click the app → Open, or run `xattr -cr MikePipeReceiver.app`.
- **`python` / `pip` not found on Mac**: Use `python3` and `pip3` instead.

## License

[MIT](LICENSE)
