"""MikePipe Receiver — listens for UDP audio and plays it to BlackHole on Mac."""

import argparse
import socket
import sys
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

    # Resolve output device
    if args.device is not None:
        device_index = args.device
        device_name = sd.query_devices(device_index)["name"]
    else:
        device_index, device_name = find_blackhole_device()
        if device_index is None:
            print("Error: BlackHole device not found. Install BlackHole or specify --device.", file=sys.stderr)
            sys.exit(1)

    print(f"Output device: [{device_index}] {device_name}")

    # Open UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))
    sock.settimeout(0.5)

    print(f"Listening on UDP port {UDP_PORT}...")
    print("Waiting for sender...")

    receiving = False
    last_recv_time = 0.0

    try:
        with sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=FRAME_SAMPLES,
            device=device_index,
        ) as stream:
            while True:
                try:
                    data, addr = sock.recvfrom(SOCKET_BUFFER)
                except socket.timeout:
                    if receiving and (time.time() - last_recv_time > SILENCE_TIMEOUT):
                        receiving = False
                        print("\rWaiting for sender...", flush=True)
                    continue

                if not receiving:
                    receiving = True
                    print(f"\rReceiving audio from {addr[0]}", flush=True)

                last_recv_time = time.time()

                # Convert bytes to numpy array and write to output
                audio = np.frombuffer(data, dtype=np.int16).reshape(-1, 1)
                stream.write(audio)

    except KeyboardInterrupt:
        print("\nShutting down.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        sock.close()


if __name__ == "__main__":
    main()
