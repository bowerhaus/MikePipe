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


class Sender:
    """Captures mic audio and streams it over UDP."""

    def __init__(self, host, port=UDP_PORT, device=None, on_state_change=None):
        self.host = host
        self.port = port
        self.device = device if device is not None else sd.default.device[0]
        self.on_state_change = on_state_change

        self._streaming = False
        self._lock = threading.Lock()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._dest = (self.host, self.port)
        self._stream = None
        self._running = False

    @property
    def is_streaming(self):
        with self._lock:
            return self._streaming

    def start_streaming(self):
        with self._lock:
            if not self._streaming:
                self._streaming = True
                if self.on_state_change:
                    self.on_state_change(True)

    def stop_streaming(self):
        with self._lock:
            if self._streaming:
                self._streaming = False
                if self.on_state_change:
                    self.on_state_change(False)

    def start(self):
        """Open the audio input stream and begin capturing."""
        self._running = True
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=FRAME_SAMPLES,
            device=self.device,
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self):
        """Stop capturing and close resources."""
        self._running = False
        self.stop_streaming()
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}", file=sys.stderr)
        if self.is_streaming:
            self._sock.sendto(indata.tobytes(), self._dest)

    def start_hotkey_listener(self):
        """Double-tap Right Ctrl to start streaming, single tap to stop."""
        from pynput import keyboard

        last_press_time = 0.0
        DOUBLE_TAP_WINDOW = 0.4

        def on_press(key):
            nonlocal last_press_time
            if key == keyboard.Key.ctrl_r:
                now = time.time()
                if now - last_press_time < DOUBLE_TAP_WINDOW:
                    self.start_streaming()
                    last_press_time = 0.0
                else:
                    last_press_time = now
                    threading.Timer(DOUBLE_TAP_WINDOW, _check_single_tap, args=(now,)).start()

        def _check_single_tap(press_time):
            nonlocal last_press_time
            if last_press_time == press_time:
                self.stop_streaming()

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

    def on_state_change(streaming):
        if streaming:
            print("\r[STREAMING]", flush=True)
        else:
            print("\r[STOPPED]", flush=True)

    sender = Sender(args.host, device=args.device, on_state_change=on_state_change)
    sender.start_hotkey_listener()

    print(f"Ready. Double-tap Right Ctrl to start, single tap to stop. Target: {args.host}:{UDP_PORT}")
    print("[STOPPED]")

    try:
        sender.start()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        sender.stop()


if __name__ == "__main__":
    main()
