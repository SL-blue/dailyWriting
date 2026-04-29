#!/bin/bash
#
# Build DailyWriting.app for macOS
#
# Usage: ./scripts/build_app.sh
#
# Prerequisites:
#   - Python 3.11+ with venv
#   - PyInstaller installed (pip install pyinstaller)
#
# Output:
#   - dist/DailyWriting.app (standalone application)
#   - build/ (intermediate build files)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Building DailyWriting.app ===${NC}"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"

# Check for virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo -e "${YELLOW}Warning: No venv found. Using system Python.${NC}"
fi

# Check PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}Installing PyInstaller...${NC}"
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/

# Create icon if it doesn't exist
if [ ! -f "resources/icon.icns" ]; then
    echo -e "${YELLOW}Creating placeholder icon...${NC}"
    ./scripts/create_icon.sh
fi

# Run PyInstaller
echo -e "${GREEN}Building application with PyInstaller...${NC}"
pyinstaller DailyWriting.spec --noconfirm

# Check if build succeeded
if [ -d "dist/DailyWriting.app" ]; then
    echo ""
    echo -e "${GREEN}=== Build Successful! ===${NC}"
    echo ""
    echo "Application: dist/DailyWriting.app"
    echo "Size: $(du -sh dist/DailyWriting.app | cut -f1)"
    echo ""
    echo "To run: open dist/DailyWriting.app"
    echo ""

    # Optional: Ad-hoc code signing for local use
    echo -e "${YELLOW}Signing with ad-hoc signature (for local use)...${NC}"
    codesign --force --deep --sign - dist/DailyWriting.app 2>/dev/null || true
    echo "Done!"
else
    echo -e "${RED}Build failed! Check output above for errors.${NC}"
    exit 1
fi
