# Plan: Add Custom App Icon to MikePipe

**GitHub Issue:** [#5](https://github.com/bowerhaus/MikePipe/issues/5)

## Context
MikePipe currently has no custom icon — Windows tray uses Pillow-generated coloured circles, Mac menu bar uses Unicode emoji, and PyInstaller uses its default icon for both `.exe` and `.app`. The user wants a proper branded icon appearing on desktop shortcuts, in the taskbar/dock, and in the tray/menu bar on both platforms.

## Prerequisites
The user will provide a source image (PNG, ideally 1024x1024 or larger, with transparency). This file should be placed in the repo as `assets/icon.png`.

## Steps

### Step 1: Create icon assets from source image
Create an `assets/` directory and a Python conversion script `assets/generate_icons.py` that:
- Takes `assets/icon.png` as input
- Generates `assets/icon.ico` (Windows — multi-resolution: 16, 32, 48, 64, 128, 256)
- Generates `assets/icon.icns` (Mac — requires sizes: 16, 32, 128, 256, 512, 1024)
- Generates `assets/icon_tray.png` (64x64, for Windows tray base image)
- Generates `assets/icon_menubar.png` (22x22, for Mac menu bar — will be used as a template image)

**Note:** `.icns` generation on Mac can use `iconutil` (ships with macOS) or the `Pillow` library. We'll use Pillow since it's already a dependency on Windows and keep a simple cross-platform script.

**Files:** `assets/generate_icons.py` (new), outputs to `assets/`

### Step 2: Wire icon into PyInstaller builds
- **build_windows.bat / build_windows.ps1**: Add `--icon=assets/icon.ico`
- **build_mac.sh**: Add `--icon=assets/icon.icns`
- This gives the `.exe` and `.app` their custom icon, which desktop shortcuts/symlinks inherit automatically

**Files:** `build_windows.bat`, `build_windows.ps1`, `build_mac.sh`

### Step 3: Update Windows tray icon (`tray_sender.py`)
- Load `assets/icon_tray.png` as the base icon (falling back to current Pillow generation if file missing)
- Overlay a small coloured status dot in the corner: green when streaming, grey when stopped
- Keep the existing `create_icon_image(streaming)` function signature, just change the implementation to composite the custom icon with a status dot

**Files:** `tray_sender.py`

### Step 4: Update Mac menu bar icon (`menubar_receiver.py`)
- Set `rumps.App(icon="assets/icon_menubar.png")` to display the custom icon in the menu bar
- Keep the existing `title` property for the emoji state indicator (⚪/🔴) — it appears next to the icon automatically
- The `icon` property sets the image; `title` sets text alongside it. Both display simultaneously in the menu bar.
- Use `template=True` so macOS renders the icon in the standard menu bar style (adapts to light/dark mode)

**Files:** `menubar_receiver.py`

### Step 5: Bundle icon assets into PyInstaller builds
- Add `--add-data "assets:assets"` to PyInstaller commands so icon files are included in the built app
- Update code to locate assets using `sys._MEIPASS` (PyInstaller's temp directory) when running from a built executable, falling back to the normal `assets/` path during development

**Files:** `build_windows.bat`, `build_windows.ps1`, `build_mac.sh`, `tray_sender.py`, `menubar_receiver.py`

### Step 6: Update `.gitignore` and documentation
- Add generated icon files to the repo (they're small and needed for builds)
- Update CLAUDE.md to mention the `assets/` directory
- Update progress.md

**Files:** `.gitignore`, `CLAUDE.md`

## Key Technical Details

| Where | Format | How |
|-------|--------|-----|
| Windows .exe icon | `.ico` | PyInstaller `--icon` flag |
| Windows taskbar | `.ico` | Inherited from .exe |
| Windows system tray | `.png` (64x64) | Loaded by Pillow, status dot overlaid |
| Mac .app icon | `.icns` | PyInstaller `--icon` flag |
| Mac Dock | `.icns` | Inherited from .app bundle |
| Mac menu bar | `.png` (22x22) | `rumps` `icon` parameter with `template=True` |
| Desktop shortcuts | Inherited | Symlinks/.lnk inherit from .app/.exe |

## Asset path resolution helper
Create a small utility (in a new `assets_util.py` or inline) to resolve asset paths:
```python
def asset_path(filename):
    """Resolve path to bundled asset, works both in dev and PyInstaller."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return os.path.join(base, 'assets', filename)
```

## Verification
1. Run `python assets/generate_icons.py` — check that `.ico`, `.icns`, tray `.png`, and menubar `.png` are generated
2. Run `python tray_sender.py` on Windows — tray shows custom icon with status dot
3. Run `python3 menubar_receiver.py` on Mac — menu bar shows custom icon + emoji state
4. Build with PyInstaller on both platforms — built apps show custom icon in taskbar/dock and on desktop shortcuts
