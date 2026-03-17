"""MikePipe Receiver — listens for UDP audio and plays it to BlackHole on Mac."""

import argparse
import socket
import sys
import threading
import time

import numpy as np
import sounddevice as sd

# Audio config — must match sender
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"
FRAME_MS = 20
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)  # 320 samples
FRAME_BYTES = FRAME_SAMPLES * 2  # 640 bytes

UDP_PORT = 12345
SOCKET_BUFFER = 65536
SILENCE_TIMEOUT = 2.0  # seconds before showing "waiting" status


class Receiver:
    """Listens for UDP audio and plays it to an output device."""

    def __init__(self, device=None, port=UDP_PORT, on_state_change=None):
        self.port = port
        self.on_state_change = on_state_change

        # Resolve output device
        if device is not None:
            self.device = device
            self.device_name = sd.query_devices(device)["name"]
        else:
            self.device, self.device_name = find_blackhole_device()
            if self.device is None:
                raise RuntimeError("BlackHole device not found. Install BlackHole or specify a device.")

        self._receiving = False
        self._last_recv_time = 0.0
        self._sock = None
        self._stream = None
        self._running = False
        self._thread = None

    @property
    def is_receiving(self):
        return self._receiving

    def start(self):
        """Open socket and audio output, begin receiving in a background thread."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(("0.0.0.0", self.port))
        self._sock.settimeout(0.5)

        self._stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=FRAME_SAMPLES,
            device=self.device,
        )
        self._stream.start()
        self._running = True
        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop receiving and close resources."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._sock:
            self._sock.close()
            self._sock = None
        self._set_receiving(False)

    def _set_receiving(self, receiving, addr=None):
        if receiving != self._receiving:
            self._receiving = receiving
            if self.on_state_change:
                self.on_state_change(receiving, addr)

    def _receive_loop(self):
        while self._running:
            try:
                data, addr = self._sock.recvfrom(SOCKET_BUFFER)
            except socket.timeout:
                if self._receiving and (time.time() - self._last_recv_time > SILENCE_TIMEOUT):
                    self._set_receiving(False)
                continue
            except OSError:
                break

            self._set_receiving(True, addr)
            self._last_recv_time = time.time()

            audio = np.frombuffer(data, dtype=np.int16).reshape(-1, 1)
            self._stream.write(audio)


def find_blackhole_device():
    """Find the BlackHole audio device index."""
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if "blackhole" in d["name"].lower() and d["max_output_channels"] > 0:
            return i, d["name"]
    return None, None


def list_devices():
    print("Available output devices:")
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d["max_output_channels"] > 0:
            marker = ""
            if "blackhole" in d["name"].lower():
                marker = " <-- BlackHole"
            elif i == sd.default.device[1]:
                marker = " <-- default"
            print(f"  [{i}] {d['name']}{marker}")
    print()


def main():
    parser = argparse.ArgumentParser(description="MikePipe Receiver — receive mic audio and play to BlackHole")
    parser.add_argument("--device", type=int, default=None, help="Output device index (default: auto-detect BlackHole)")
    parser.add_argument("--list-devices", action="store_true", help="List audio output devices and exit")
    args = parser.parse_args()

    if args.list_devices:
        list_devices()
        sys.exit(0)

    list_devices()

    def on_state_change(receiving, addr):
        if receiving:
            print(f"\rReceiving audio from {addr[0]}", flush=True)
        else:
            print("\rWaiting for sender...", flush=True)

    try:
        receiver = Receiver(device=args.device, on_state_change=on_state_change)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Output device: [{receiver.device}] {receiver.device_name}")
    print(f"Listening on UDP port {UDP_PORT}...")
    print("Waiting for sender...")

    try:
        receiver.start()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        receiver.stop()


if __name__ == "__main__":
    main()
