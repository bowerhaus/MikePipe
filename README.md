# MikePipe

MikePipe streams microphone audio from a Windows laptop to a Mac desktop over a local network, enabling Mac dictation to use the Windows mic. This is useful when remoting into a Mac via Jump Desktop (or similar), which doesn't forward microphone audio.

Audio is captured on Windows, sent as raw PCM over UDP via Tailscale, and played into BlackHole (a virtual audio driver on the Mac). Mac dictation then reads from BlackHole as its input device. The result is near-real-time speech-to-text using the Windows mic, with under 100ms of latency.

A hotkey on Windows controls streaming: double-tap Right Ctrl to start, single tap to stop.

## How It Works

```
[Windows Laptop]                        [Mac Desktop]
┌──────────────────┐    UDP/Tailscale    ┌──────────────────┐
│ sender.py        │───────────────────→│ receiver.py       │
│ - Mic capture    │    port 12345       │ - Plays audio to  │
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
pip3 install -r requirements.txt
```

Configure Mac dictation to use BlackHole as its input:
1. System Settings → Keyboard → Dictation → turn on
2. System Settings → Sound → Input → select **BlackHole**

### Windows

```bash
pip install -r requirements.txt
```

## Running

### 1. Find your Mac's Tailscale IP

On the Mac:
```bash
tailscale ip -4
```
Or check the Tailscale app. It will be something like `100.x.y.z`.

### 2. Start the receiver on the Mac (start first, runs continuously)

```bash
python3 receiver.py
```

It auto-detects BlackHole. To use a different output device:
```bash
python3 receiver.py --list-devices
python3 receiver.py --device 5
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

- **Double-tap Right Ctrl** to start streaming — console shows `[STREAMING]`
- **Single tap Right Ctrl** to stop — console shows `[STOPPED]`
- Speak into the Windows mic — Mac dictation transcribes your speech

## Troubleshooting

- **No audio received**: Check that both machines are on Tailscale and can ping each other. Ensure the receiver is running before the sender starts streaming.
- **High latency**: Should be under 100ms with this setup. If not, check for network issues on Tailscale.
- **Wrong mic**: Use `--list-devices` on the sender to pick the correct input device.
- **BlackHole not found**: Ensure BlackHole is installed and restart the receiver. Use `--list-devices` to verify it appears.
- **`python` / `pip` not found on Mac**: Use `python3` and `pip3` instead.

## License

[MIT](LICENSE)
