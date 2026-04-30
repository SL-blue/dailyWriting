#!/usr/bin/env python3
"""
Generate resources/icon.ico from a 1024x1024 PNG.

Usage:
    python scripts/create_icon.py [path/to/source.png]

If no path is given, falls back to resources/icon_source.png, then to a
solid-color placeholder. Pillow encodes all standard Windows ICO sizes
(16, 24, 32, 48, 64, 128, 256) into a single .ico file.

This script is cross-platform (works on Windows, macOS, Linux) so the
Windows build can run without macOS-only tools like sips/iconutil.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required. Install with: pip install Pillow")


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESOURCES = PROJECT_ROOT / "resources"
DEFAULT_SOURCE = RESOURCES / "icon_source.png"
OUTPUT = RESOURCES / "icon.ico"

# Standard Windows ICO sizes
SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def make_placeholder() -> Image.Image:
    return Image.new("RGB", (1024, 1024), (0, 184, 148))


def main() -> int:
    RESOURCES.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        source = Path(sys.argv[1]).expanduser().resolve()
        if not source.exists():
            sys.exit(f"Source image not found: {source}")
        img = Image.open(source).convert("RGBA")
        print(f"Using source image: {source}")
    elif DEFAULT_SOURCE.exists():
        img = Image.open(DEFAULT_SOURCE).convert("RGBA")
        print(f"Using existing source: {DEFAULT_SOURCE}")
    else:
        img = make_placeholder()
        print("No source image found — using built-in placeholder.")

    img.save(OUTPUT, format="ICO", sizes=SIZES)
    print(f"Wrote: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
