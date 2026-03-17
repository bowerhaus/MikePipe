"""Generate platform-specific icon assets from the source icon.png."""

import os
import struct
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(SCRIPT_DIR, "icon.png")
SOURCE_ON = os.path.join(SCRIPT_DIR, "icon on.png")

# Output files — off (idle) state
ICO_PATH = os.path.join(SCRIPT_DIR, "icon.ico")
ICNS_PATH = os.path.join(SCRIPT_DIR, "icon.icns")
TRAY_PATH = os.path.join(SCRIPT_DIR, "icon_tray.png")
MENUBAR_PATH = os.path.join(SCRIPT_DIR, "icon_menubar.png")

# Output files — on (active) state
TRAY_ON_PATH = os.path.join(SCRIPT_DIR, "icon_tray_on.png")
MENUBAR_ON_PATH = os.path.join(SCRIPT_DIR, "icon_menubar_on.png")

# Sizes needed for each format
ICO_SIZES = [16, 32, 48, 64, 128, 256]
ICNS_SIZES = [16, 32, 128, 256, 512, 1024]


def crop_to_square(img):
    """Crop image to center square."""
    w, h = img.size
    if w == h:
        return img
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def generate_ico(img):
    """Generate Windows .ico file."""
    sizes = [(s, s) for s in ICO_SIZES]
    img.save(ICO_PATH, format="ICO", sizes=sizes)
    print(f"  {ICO_PATH}")


def generate_icns_with_iconutil(img):
    """Generate Mac .icns using iconutil (macOS only)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        iconset = os.path.join(tmpdir, "icon.iconset")
        os.makedirs(iconset)
        # iconutil expects specific filenames
        entries = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"),
            (1024, "icon_512x512@2x.png"),
        ]
        for size, name in entries:
            resized = img.resize((size, size), Image.LANCZOS)
            resized.save(os.path.join(iconset, name))
        subprocess.run(
            ["iconutil", "-c", "icns", iconset, "-o", ICNS_PATH],
            check=True,
        )
    print(f"  {ICNS_PATH}")


def generate_icns_with_pillow(img):
    """Generate Mac .icns using Pillow (cross-platform fallback)."""
    sizes = [(s, s) for s in ICNS_SIZES]
    img.save(ICNS_PATH, format="ICNS", sizes=sizes)
    print(f"  {ICNS_PATH} (via Pillow)")


def generate_icns(img):
    """Generate .icns — use iconutil on Mac, Pillow elsewhere."""
    if sys.platform == "darwin":
        try:
            generate_icns_with_iconutil(img)
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    generate_icns_with_pillow(img)


def add_rounded_background(img, size, bg_color=(50, 50, 50, 200), radius=10, padding=4):
    """Add a rounded rectangle background behind the icon."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=bg_color)
    # Resize icon to fit within the background with padding
    icon_size = size - padding * 2
    icon_resized = img.resize((icon_size, icon_size), Image.LANCZOS)
    canvas.paste(icon_resized, (padding, padding), icon_resized)
    return canvas


def generate_tray(img, path):
    """Generate 64x64 tray icon for Windows with rounded background."""
    tray = add_rounded_background(img, 64, bg_color=(120, 120, 120, 220), radius=12, padding=4)
    tray.save(path)
    print(f"  {path}")


def generate_menubar(img, path):
    """Generate 44x44 menu bar icon for Mac with rounded background."""
    menubar = add_rounded_background(img, 44, bg_color=(120, 120, 120, 220), radius=8, padding=3)
    menubar.save(path)
    print(f"  {path}")


def main():
    if not os.path.exists(SOURCE):
        print(f"Error: source icon not found at {SOURCE}")
        sys.exit(1)

    print(f"Source: {SOURCE}")
    img = Image.open(SOURCE).convert("RGBA")
    img = crop_to_square(img)
    print(f"Cropped to {img.size[0]}x{img.size[1]}")

    print("Generating icons (off/idle state):")
    generate_ico(img)
    generate_icns(img)
    generate_tray(img, TRAY_PATH)
    generate_menubar(img, MENUBAR_PATH)

    if os.path.exists(SOURCE_ON):
        print(f"\nSource (on): {SOURCE_ON}")
        img_on = Image.open(SOURCE_ON).convert("RGBA")
        img_on = crop_to_square(img_on)
        print(f"Cropped to {img_on.size[0]}x{img_on.size[1]}")
        print("Generating icons (on/active state):")
        generate_tray(img_on, TRAY_ON_PATH)
        generate_menubar(img_on, MENUBAR_ON_PATH)
    else:
        print(f"\nNo 'on' source found at {SOURCE_ON}, skipping on-state icons.")

    print("Done.")


if __name__ == "__main__":
    main()
