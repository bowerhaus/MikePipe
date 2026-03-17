"""MikePipe Sender — streams Windows mic audio over UDP to the Mac receiver."""

import argparse
import socket
import sys
import threading
import time

import numpy as np
import sounddevice as sd

# Audio config
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"
FRAME_MS = 20
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)  # 320 samples
FRAME_BYTES = FRAME_SAMPLES * 2  # 640 bytes (16-bit)

UDP_PORT = 12345

# Hotkey state
streaming = False
lock = threading.Lock()


def start_streaming():
    global streaming
    with lock:
        if not streaming:
            streaming = True
            print("\r[STREAMING]", flush=True)


def stop_streaming():
    global streaming
    with lock:
        if streaming:
            streaming = False
            print("\r[STOPPED]", flush=True)


def start_hotkey_listener():
    """Double-tap Right Ctrl to start streaming, single tap to stop."""
    from pynput import keyboard

    last_press_time = 0.0
    DOUBLE_TAP_WINDOW = 0.4  # seconds

    def on_press(key):
        nonlocal last_press_time
        # Right Ctrl on Windows
        if key == keyboard.Key.ctrl_r:
            now = time.time()
            if now - last_press_time < DOUBLE_TAP_WINDOW:
                start_streaming()
                last_press_time = 0.0  # reset to avoid triple-tap
            else:
                last_press_time = now
                # Single tap stops streaming (after the double-tap window expires)
                # We use a timer so we can distinguish single from double tap
                threading.Timer(DOUBLE_TAP_WINDOW, _check_single_tap, args=(now,)).start()

    def _check_single_tap(press_time):
        nonlocal last_press_time
        # If no second tap happened (last_press_time still matches), it was a single tap
        if last_press_time == press_time:
            stop_streaming()

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()


def list_devices():
    print("Available input devices:")
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0:
            marker = " <-- default" if i == sd.default.device[0] else ""
            print(f"  [{i}] {d['name']}{marker}")
    print()


def main():
    parser = argparse.ArgumentParser(description="MikePipe Sender — stream mic audio over UDP")
    parser.add_argument("host", help="Mac receiver IP address (Tailscale IP)")
    parser.add_argument("--device", type=int, default=None, help="Input device index (default: system default)")
    parser.add_argument("--list-devices", action="store_true", help="List audio input devices and exit")
    args = parser.parse_args()

    if args.list_devices:
        list_devices()
        sys.exit(0)

    list_devices()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (args.host, UDP_PORT)

    start_hotkey_listener()

    print(f"Ready. Double-tap Right Ctrl to start, single tap to stop. Target: {args.host}:{UDP_PORT}")
    print("[STOPPED]")

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}", file=sys.stderr)
        with lock:
            is_streaming = streaming
        if is_streaming:
            sock.sendto(indata.tobytes(), dest)

    device_index = args.device if args.device is not None else sd.default.device[0]

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=FRAME_SAMPLES,
            device=device_index,
            callback=audio_callback,
        ):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
