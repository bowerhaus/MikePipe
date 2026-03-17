"""MikePipe Menu Bar Receiver — Mac menu bar app for receiving mic audio."""

import rumps

from receiver import Receiver, list_devices


class MikePipeMenuBar(rumps.App):
    def __init__(self):
        super().__init__("MikePipe", title="\u26AA", quit_button=None)
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
            self.title = "\U0001f534"  # red circle = receiving
            self.status_item.title = f"Receiving from {addr[0]}"
        else:
            self.title = "\u26AA"  # white circle = idle
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
