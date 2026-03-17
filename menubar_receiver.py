"""MikePipe Menu Bar Receiver — Mac menu bar app for receiving mic audio."""

import os
import sys

import rumps

from receiver import Receiver, list_devices

_base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
_icon_off_path = os.path.join(_base_dir, "assets", "icon_menubar.png")
_icon_on_path = os.path.join(_base_dir, "assets", "icon_menubar_on.png")


class MikePipeMenuBar(rumps.App):
    def __init__(self):
        icon_path = _icon_off_path if os.path.exists(_icon_off_path) else None
        super().__init__("MikePipe", title="", icon=icon_path, template=False, quit_button=None)
        self._icon_off = _icon_off_path if os.path.exists(_icon_off_path) else None
        self._icon_on = _icon_on_path if os.path.exists(_icon_on_path) else None
        self.status_item = rumps.MenuItem("Waiting for sender...", callback=None)
        self.status_item.set_callback(None)
        self.quit_item = rumps.MenuItem("Quit", callback=self._on_quit)
        self.menu = [self.status_item, None, self.quit_item]

        list_devices()

        self.receiver = Receiver(on_state_change=self._on_state_change)
        print(f"Output device: [{self.receiver.device}] {self.receiver.device_name}")
        print(f"Listening on UDP port {self.receiver.port}...")

    def _on_state_change(self, receiving, addr):
        if receiving:
            if self._icon_on:
                self.icon = self._icon_on
            else:
                self.title = "\U0001f534"
            self.status_item.title = f"Receiving from {addr[0]}"
        else:
            if self._icon_off:
                self.icon = self._icon_off
            else:
                self.title = "\u26AA"
            self.status_item.title = "Waiting for sender..."

    def _on_quit(self, _):
        self.receiver.stop()
        rumps.quit_application()

    def run(self):
        self.receiver.start()
        super().run()


def main():
    try:
        app = MikePipeMenuBar()
    except RuntimeError as e:
        print(f"Error: {e}")
        return
    app.run()


if __name__ == "__main__":
    main()
