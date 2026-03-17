# MikePipe

Stream microphone audio from a Windows laptop to a Mac desktop over Tailscale, enabling Mac dictation to use the Windows mic.

Audio is piped into BlackHole (virtual audio driver) on the Mac.

## Architecture

```
[Windows]  sender.py  --UDP-->  receiver.py  [Mac]  -->  BlackHole  -->  Mac Dictation
```

- **sender.py** (Windows): Captures mic via `sounddevice`, streams raw PCM over UDP. Double-tap AltGr toggles streaming.
- **receiver.py** (Mac): Listens on UDP port 12345, plays received audio to BlackHole.
- Audio: 16kHz, 16-bit signed int, mono PCM. 20ms frames for low latency.

## Prerequisites

- **Both machines**: Python 3.8+, connected via [Tailscale](https://tailscale.com/)
- **Mac**: [BlackHole](https://existential.audio/blackhole/) virtual audio driver installed
- **Mac**: System Settings → Sound → Input set to "BlackHole" (so dictation reads from it)

## Setup

```bash
# On both machines
pip install -r requirements.txt
```

## Usage

### 1. Find your Mac's Tailscale IP

On the Mac, run:
```bash
tailscale ip -4
```
Or check the Tailscale app. It will be something like `100.x.y.z`.

### 2. Start the receiver on the Mac

```bash
python receiver.py
```

It auto-detects BlackHole. To use a different output device:
```bash
python receiver.py --list-devices
python receiver.py --device 5
```

### 3. Start the sender on Windows

```bash
python sender.py <mac-tailscale-ip>
```

To choose a specific mic:
```bash
python sender.py --list-devices
python sender.py <mac-tailscale-ip> --device 2
```

### 4. Stream audio

- **Double-tap AltGr** (Right Alt) to start streaming — console shows `[STREAMING]`
- **Double-tap AltGr** again to stop — console shows `[STOPPED]`
- Open Mac dictation — it will transcribe speech from your Windows mic

## Configure Mac Dictation

1. System Settings → Keyboard → Dictation → turn on
2. System Settings → Sound → Input → select **BlackHole**
3. Alternatively, some apps let you select the input device directly

## Troubleshooting

- **No audio received**: Check that both machines are on Tailscale and can ping each other. Ensure the receiver is running before the sender starts streaming.
- **High latency**: This should not happen with this setup (~50ms expected). If it does, check for network issues on Tailscale.
- **Wrong mic**: Use `--list-devices` on the sender to pick the correct input device.
- **BlackHole not found**: Ensure BlackHole is installed and restart the receiver. Use `--list-devices` to verify it appears.
