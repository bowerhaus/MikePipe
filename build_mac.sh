#!/bin/bash
set -e
echo "Building MikePipe Receiver for Mac..."
python3 -m PyInstaller --onefile --windowed --name MikePipeReceiver menubar_receiver.py
echo
echo "Done. Output: dist/MikePipeReceiver"
echo "Note: To allow unsigned app, run: xattr -cr dist/MikePipeReceiver.app"
