"""MikePipe config file support — reads sender settings from mikepipe.ini."""

import configparser
import os
import sys

CONFIG_FILENAME = "mikepipe.ini"

CONFIG_TEMPLATE = """\
[sender]
# Mac receiver Tailscale IP address (required)
host =

# UDP port (default: 12345)
port = 12345

# Mic input device index (leave blank for system default)
# Run "python sender.py --list-devices" to see available devices
device =
"""


def get_config_dir():
    """Return the platform-appropriate config directory for MikePipe."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "MikePipe")
    else:
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "MikePipe")


def get_config_path():
    """Return the full path to mikepipe.ini."""
    return os.path.join(get_config_dir(), CONFIG_FILENAME)


def ensure_config():
    """Create config file with template if it doesn't exist. Returns the path."""
    path = get_config_path()
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(CONFIG_TEMPLATE)
        print(f"Created config file: {path}")
        print("Please edit it to set your Mac receiver's Tailscale IP address.")
    return path


def load_config():
    """Load sender config from mikepipe.ini. Returns (host, port, device).

    Returns None for device if not set (use system default).
    Raises SystemExit if host is not configured.
    """
    path = ensure_config()
    config = configparser.ConfigParser()
    config.read(path)

    if not config.has_section("sender"):
        print(f"Error: [sender] section missing in {path}", file=sys.stderr)
        sys.exit(1)

    host = config.get("sender", "host", fallback="").strip()
    if not host:
        print(f"Error: 'host' not set in {path}", file=sys.stderr)
        print("Please edit the config file and set the Mac receiver's Tailscale IP address.")
        sys.exit(1)

    port = config.getint("sender", "port", fallback=12345)

    device_str = config.get("sender", "device", fallback="").strip()
    device = int(device_str) if device_str else None

    return host, port, device
