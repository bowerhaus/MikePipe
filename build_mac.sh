#!/bin/bash
set -e
echo "Building MikePipe Receiver for Mac..."
python3 -m PyInstaller --noconfirm --onedir --windowed --name MikePipeReceiver --icon=assets/icon.icns --add-data "assets:assets" menubar_receiver.py
echo

echo "Creating alias on Desktop..."
DESKTOP="$HOME/Desktop"
ln -sf "$(pwd)/dist/MikePipeReceiver.app" "$DESKTOP/MikePipeReceiver.app"

echo "Done. App alias placed on Desktop."
echo "Note: To allow unsigned app, run: xattr -cr dist/MikePipeReceiver.app"
