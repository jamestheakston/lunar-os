#!/bin/bash
# Lunar OS Build Script
# This script builds the Lunar OS ISO from Debian Live

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_ROOT/config/build"

echo "=== Lunar OS Build Script ==="
echo "Project root: $PROJECT_ROOT"
echo "Config directory: $CONFIG_DIR"
echo ""

# Check if running as root (required for lb build)
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Please run: sudo $0"
    exit 1
fi

# Check for required dependencies
echo "Checking dependencies..."
for cmd in lb build; do
    if ! command -v lb &> /dev/null; then
        echo "Error: '$cmd' not found. Please install live-build:"
        echo "  apt-get install live-build"
        exit 1
    fi
done

# Clean previous build if it exists
if [ -d "$PROJECT_ROOT/build" ]; then
    echo "Cleaning previous build..."
    rm -rf "$PROJECT_ROOT/build"
fi

# Create build directory
mkdir -p "$PROJECT_ROOT/build"
cd "$PROJECT_ROOT/build"

# Copy configuration
echo "Copying configuration..."
cp -r "$CONFIG_DIR"/* .

# Apply custom configurations
echo "Applying Lunar OS customizations..."

# Copy package lists
if [ -f "$PROJECT_ROOT/config/packages.list" ]; then
    cp "$PROJECT_ROOT/config/packages.list" config/packages.list.chroot
fi

# Copy chroot includes (files to be added to the system)
if [ -d "$PROJECT_ROOT/config/includes.chroot" ]; then
    cp -r "$PROJECT_ROOT/config/includes.chroot"/* config/includes.chroot/
fi

# Copy binary includes (files to be added to the ISO)
if [ -d "$PROJECT_ROOT/config/includes.binary" ]; then
    cp -r "$PROJECT_ROOT/config/includes.binary"/* config/includes.binary/
fi

# Copy hooks
if [ -d "$PROJECT_ROOT/config/packages.hook" ]; then
    cp -r "$PROJECT_ROOT/config/packages.hook"/* config/hooks/
fi

# Copy assets to chroot hooks directory (for the copy-assets hook)
echo "Copying assets to chroot hooks..."
mkdir -p config/chroot_local-includes/tmp/lunar-assets/desktop
mkdir -p config/chroot_local-includes/tmp/lunar-assets/plymouth
mkdir -p config/chroot_local-includes/tmp/lunar-assets/icons

cp -r "$PROJECT_ROOT/assets/desktop"/* config/chroot_local-includes/tmp/lunar-assets/desktop/ 2>/dev/null || true
cp -r "$PROJECT_ROOT/assets/boot/plymouth"/* config/chroot_local-includes/tmp/lunar-assets/plymouth/ 2>/dev/null || true
cp -r "$PROJECT_ROOT/assets/icons"/* config/chroot_local-includes/tmp/lunar-assets/icons/ 2>/dev/null || true

echo "Assets copied:"
ls -la config/chroot_local-includes/tmp/lunar-assets/desktop/ 2>/dev/null || echo "No desktop assets"
ls -la config/chroot_local-includes/tmp/lunar-assets/plymouth/ 2>/dev/null || echo "No plymouth assets"

# Build the ISO
echo ""
echo "=== Building Lunar OS ISO ==="
echo "This may take 30-60 minutes depending on your system..."
echo ""

lb build

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Build successful! ==="
    echo "ISO file location: $PROJECT_ROOT/build/*.iso"
    ls -lh "$PROJECT_ROOT"/*.iso 2>/dev/null || echo "Warning: ISO file not found in expected location"
    echo ""
    echo "To test the ISO:"
    echo "  qemu-system-x86_64 -m 2048 -cdrom $PROJECT_ROOT/build/*.iso -boot d"
    echo ""
    echo "To write to USB:"
    echo "  dd if=$PROJECT_ROOT/build/*.iso of=/dev/sdX bs=4M status=progress"
    echo "  (Replace /dev/sdX with your USB device)"
else
    echo ""
    echo "=== Build failed ==="
    echo "Check the logs above for errors"
    exit 1
fi
