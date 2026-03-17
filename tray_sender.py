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


def create_icon_image(streaming):
    """Generate a tray icon: green circle if streaming, grey if stopped."""
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (0, 200, 0, 255) if streaming else (128, 128, 128, 255)
    margin = 8
    draw.ellipse([margin, margin, ICON_SIZE - margin, ICON_SIZE - margin], fill=color)
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
