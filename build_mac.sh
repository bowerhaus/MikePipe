#!/bin/bash
set -e
echo "Building MikePipe Receiver for Mac..."
python3 -m PyInstaller --onefile --windowed --name MikePipeReceiver menubar_receiver.py
echo

echo "Creating symlink on Desktop..."
DESKTOP="$HOME/Desktop"
ln -sf "$(pwd)/dist/MikePipeReceiver" "$DESKTOP/MikePipeReceiver"

echo "Done. Symlink placed on Desktop."
echo "Note: To allow unsigned app, run: xattr -cr dist/MikePipeReceiver.app"
