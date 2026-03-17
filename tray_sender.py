"""MikePipe Tray Sender — Windows system tray app for streaming mic audio."""

import os
import subprocess
import sys
import threading

from PIL import Image, ImageDraw
import pystray

from config import get_config_path, load_config
from sender import Sender, list_devices


ICON_SIZE = 64

# Load custom tray icons (off and on states)
_base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
_tray_off_path = os.path.join(_base_dir, "assets", "icon_tray.png")
_tray_on_path = os.path.join(_base_dir, "assets", "icon_tray_on.png")

_ICON_OFF = None
_ICON_ON = None
if os.path.exists(_tray_off_path):
    _ICON_OFF = Image.open(_tray_off_path).convert("RGBA").resize((ICON_SIZE, ICON_SIZE))
if os.path.exists(_tray_on_path):
    _ICON_ON = Image.open(_tray_on_path).convert("RGBA").resize((ICON_SIZE, ICON_SIZE))


def create_icon_image(streaming):
    """Return the appropriate tray icon for the current state."""
    if streaming and _ICON_ON:
        return _ICON_ON.copy()
    if not streaming and _ICON_OFF:
        return _ICON_OFF.copy()
    # Fallback: simple coloured circle
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (0, 200, 0, 255) if streaming else (128, 128, 128, 255)
    draw.ellipse([8, 8, ICON_SIZE - 8, ICON_SIZE - 8], fill=color)
    return img


def open_config():
    """Open the config file in the default editor."""
    path = get_config_path()
    if sys.platform == "win32":
        os.startfile(path)
    else:
        subprocess.Popen(["open", path])


def main():
    host, port, device = load_config()
    list_devices()

    icon = None
    status_item = None

    def update_tray(streaming):
        if icon:
            icon.icon = create_icon_image(streaming)
            label = "Streaming" if streaming else "Stopped"
            icon.title = f"MikePipe — {label}"

    sender = Sender(host, port=port, device=device, on_state_change=update_tray)

    def on_open_config(tray_icon, item):
        open_config()

    def on_quit(tray_icon, item):
        sender.stop()
        tray_icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("MikePipe Sender", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open Config...", on_open_config),
        pystray.MenuItem("Quit", on_quit),
    )

    icon = pystray.Icon(
        "MikePipe",
        create_icon_image(False),
        title="MikePipe — Stopped",
        menu=menu,
    )

    def run_sender():
        sender.start_hotkey_listener()
        sender.start()

    # Start sender in background, run tray icon on main thread
    threading.Thread(target=run_sender, daemon=True).start()
    icon.run()


if __name__ == "__main__":
    main()
