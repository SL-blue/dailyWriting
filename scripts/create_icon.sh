#!/bin/bash
#
# Create app icon for DailyWriting
#
# Usage: ./scripts/create_icon.sh [source_image.png]
#
# If no source image is provided, creates a simple placeholder icon.
#
# Requirements:
#   - macOS with sips and iconutil commands
#   - For custom icon: provide a 1024x1024 PNG image

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESOURCES_DIR="$PROJECT_ROOT/resources"
ICONSET_DIR="$RESOURCES_DIR/icon.iconset"

mkdir -p "$RESOURCES_DIR"
rm -rf "$ICONSET_DIR"
mkdir -p "$ICONSET_DIR"

# Check if source image provided
if [ -n "$1" ] && [ -f "$1" ]; then
    SOURCE_IMAGE="$1"
    echo "Using source image: $SOURCE_IMAGE"
else
    # Create a simple placeholder icon using Python
    echo "Creating placeholder icon..."

    python3 << 'PYEOF'
import os

# Simple PPM image (no dependencies needed)
# Creates a green square with "DW" text approximation

size = 1024
# Green color (#00b894)
r, g, b = 0, 184, 148

# Create a simple solid color image
header = f"P6\n{size} {size}\n255\n"
pixels = bytes([r, g, b] * size * size)

output_path = os.path.join(os.environ.get('RESOURCES_DIR', 'resources'), 'icon_source.ppm')
with open(output_path, 'wb') as f:
    f.write(header.encode())
    f.write(pixels)

print(f"Created: {output_path}")
PYEOF

    # Convert PPM to PNG using sips
    RESOURCES_DIR="$RESOURCES_DIR"
    SOURCE_IMAGE="$RESOURCES_DIR/icon_source.ppm"
    sips -s format png "$SOURCE_IMAGE" --out "$RESOURCES_DIR/icon_source.png" >/dev/null 2>&1
    SOURCE_IMAGE="$RESOURCES_DIR/icon_source.png"
    rm -f "$RESOURCES_DIR/icon_source.ppm"
    echo "Created placeholder: $SOURCE_IMAGE"
fi

# Generate all required icon sizes
echo "Generating icon sizes..."

SIZES=(16 32 64 128 256 512 1024)

for size in "${SIZES[@]}"; do
    # Standard resolution
    sips -z $size $size "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_${size}x${size}.png" >/dev/null 2>&1

    # Retina resolution (2x) for sizes up to 512
    if [ $size -le 512 ]; then
        double=$((size * 2))
        sips -z $double $double "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" >/dev/null 2>&1
    fi
done

# Create .icns file
echo "Creating icon.icns..."
iconutil -c icns "$ICONSET_DIR" -o "$RESOURCES_DIR/icon.icns"

# Cleanup
rm -rf "$ICONSET_DIR"

echo ""
echo "Icon created: $RESOURCES_DIR/icon.icns"
echo ""
echo "To use a custom icon, run:"
echo "  ./scripts/create_icon.sh path/to/your/1024x1024.png"
